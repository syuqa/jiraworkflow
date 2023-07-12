import json
import hashlib
from datetime import datetime, timedelta
from django import template
from django_celery_results.models import TaskResult
from timetta.utils import get_children, SyncStatusException, SyncTaskChildrenNone
from timetta.models import TimettaProjects

register = template.Library()

@register.simple_tag
def get_dict_data(data, key):
    # print('get_dict_data', data, key, data.get(key))
    return data.get(key)

@register.filter(name='project_is_exist')
def project_is_exist(project):
    return TimettaProjects.objects.filter(jira_tag=project).exists()

@register.filter(name='get_item_index')
def get_item_index(data, key):
    keys = [*data.keys()]
    return keys.index(key)

@register.filter(name='items')
def items(data, attr=None):
    if attr:
        values = data.get(attr)
        if values and isinstance(values, dict):
            return values.items()
        else:
            return ()
    else:
        return data.items()

@register.filter(name='tojson')
def to_json(data):
    return json.dumps(data)

@register.filter(name='ident')
def ident(data):
    return json.dumps(json.loads(data), indent=4)

@register.filter(name='enum')
def enum(data):
    return enumerate(data)

@register.filter(name='len')
def lens(data):
    return len(data)

@register.filter(name='max3list')
def max3list(data):
    n = len(data) / 3 
    if len(data) % 3 > 0:
        n += 1
    return int(n)

@register.filter(name='startswith')
def startsh(text, tag):
    return str(text).startswith(tag)

@register.filter(name='rustatus')
def rustatus(status):
    ru = {
        "FAILURE_ALL": "ОШИБКА",
        "SUCCESS": "ВЫПОЛНЕНО",
        "FAILURE": "ОШИБКА",
        "PENDING": "ОЖИДАЕТ",
        "RETRY": "ПОВТОРИТЬ",
        "REVOKED": "ОТМЕНЕН",
        "STARTED": "ВЫПОЛНЯЕТСЯ"

    }
    return ru.get(status) if ru.get(status) else status

@register.filter(name='statcolor')
def statcolort(status):
    color = {
        "SUCCESS": "color-green",
        "FAILURE": "color-red tooltip-init popup-open",
        "PENDING": "color-orange",
        "RETRY": "color-blueviolet",
        "REVOKED": "color-grey",
        "STARTED": "color-blue"

    }
    return color.get(status)  if color.get(status) else 'color-black'

@register.filter(name='errormessage')
def errormessage(result):
    # json.dumps(parsed, indent=4)
    message = json.loads(result)
    return f"""{message.get('exc_type')}"""

@register.filter(name='runuser')
def runuser(kwargs):
    print('---- get run name -----')
    print(kwargs.replace('...', '').replace("False", "false").replace("True", "true").replace("[", "'").replace("]", "'"))
    try:
        u = json.loads(json.loads(kwargs.replace('...', '').replace("False", "false").replace("True", "true").replace("[", "'").replace("]", "'")).replace("'", '"'))
        print(u)
        if u.get('username'):
            return u.get('username')
        else:
            return 'не определен'
    except Exception as e:
        print(e)
        return 'не определен'

@register.filter(name='get')
def get(data, key):
    return data.get(key)

@register.filter(name='get_task_syncusers')
def get_task_syncusers(task_id, user):
    task = TaskResult.objects.get(task_id=task_id)
    print('taskid', task_id, 'user', user , 'tasks', task)
    child = [t[0][0] for t in json.loads(task.meta).get('children')]
    print(child)
    r = TaskResult.objects.filter(task_id__in=child, task_name="Timetta: Синхронизация по неделям", result__contains=user).first()
    return r

@register.filter(name='get_task_synweek')
def get_task_synweek(usertask_id, week):
    task = TaskResult.objects.get(task_id=usertask_id)
    child = [t[0][0] for t in json.loads(task.meta).get('children')]
    return TaskResult.objects.filter(task_id__in=child, task_name="Timetta: Синхронизация по проектам", result__contains=week).first()

@register.filter(name='weekinfo')
def weekinfo(date, info):
    print('WEEK DATE', date)
    today = datetime.strptime(date, '%Y-%m-%d')
    week = today.isocalendar()[1]
    end = today + timedelta(6 - datetime.weekday(today))
    d = {'week': f'{week} неделя {today.strftime("%Y")}г.'}
    if today.strftime("%Y") == end.strftime("%Y"):
        d["dates"] = f'{today.strftime("%d.%m")} - {end.strftime("%d.%m")} {today.strftime("%Y")} года'
        return d.get(info)
    else:
        d["dates"] = f'{today.strftime("%d.%m.%Y")} - {end.strftime("%d.%m.%Y")}'
        return d.get(info)

@register.simple_tag
def strhash(*args):
        print(args)
        m = hashlib.sha256()
        for text in args:
            m.update(text.encode())
        m.digest()
        return m.hexdigest()

def check_status(id, status, msg=None, trace=None):
    if not status == 'SUCCESS':
        raise SyncStatusException(status, msg, trace)

def check_status_child(parent, task_kwargs=None, taskname=None):
    tasks = []
    result = None
    if task_kwargs:
        if taskname:
            children = TaskResult.objects.filter(task_id__in=parent, task_kwargs__contains=task_kwargs, task_name=taskname)
        else:
            children = TaskResult.objects.filter(task_id__in=parent, task_kwargs__contains=task_kwargs)
    else:
        if taskname:
            children = TaskResult.objects.filter(task_id__in=parent, task_name=taskname)
        else:
            children = TaskResult.objects.filter(task_id__in=parent)
    print('--- children: ', children)
    if len(children) > 0:
        for child in children:
            check_status(child.task_id, child.status, child.result, child.traceback)
            tasks = [*tasks, *get_children(child.meta)]
            result = child.result
        return tasks, result
    else:
        raise SyncTaskChildrenNone(parent)

@register.simple_tag
def get_task_children(task, user, name=None):
    try:
        _task = TaskResult.objects.get(task_id=task)
        if name:
            return TaskResult.objects.filter(task_id__in=get_children(_task.meta), task_kwargs__contains=user, task_name=name)
        else:
            return TaskResult.objects.filter(task_id__in=get_children(_task.meta), task_kwargs__contains=user)
    except TaskResult.DoesNotExist:
        return []


@register.simple_tag
def get_meetings_task(task, user):
    try:
        task = TaskResult.objects.get(task_id=task)
        user_task = TaskResult.objects.filter(task_id__in=get_children(task.meta), task_kwargs__contains=user)
        if user_task.exists():
            meetings_task = TaskResult.objects.filter(task_id__in=get_children(user_task.first().meta), task_name='Timetta: Синхронизация митингов')
            return meetings_task
        else:
            return []
    except TaskResult.DoesNotExist:
        return []

@register.simple_tag
def get_status_sync(task, user='', week='', project='', stask=False):
    t = 'Timetta: Синхронизация по неделям' if stask else None
    try:
        print('TASK <', task, '> USER <', user, '> WEEK <', week, '> PROJECT <', project, '>')
        users, uresult = check_status_child([task])
        print('USER: ', users, 'RESULT:', uresult)
        weeks, wresult = check_status_child(parent=users)
        print('WEEK: ', weeks, 'RESULT', wresult)
        proj, presult = check_status_child(parent=weeks, task_kwargs=user, taskname=t)
        print('PROJ: ', proj, 'RESULT', presult)
        sync, sresult = check_status_child(parent=proj, task_kwargs=week)
        print('SYNC: ', proj, 'RESULT', sresult)
        _as, result = check_status_child(sync, project)
        print('ASYNC:', _as, 'RESULT', result)
        result = {
            'status': 'SUCCESS',
            'result': result
        }
        return result
    except SyncStatusException as e:
        print('EXEP ARGS', e.args)
        status = json.loads(e.args[1])
        trace = list(filter(None, e.args[2].replace('"', "'").split('\n')))
        status[trace[0]] = trace[1:]
        info =  {
            "status": e.args[0],
            "result":  json.dumps(status),
            "trace": e.args[2]
            } 
        return info
    except SyncTaskChildrenNone as e:
        info =  {
            "status": 'Выполняется',
            "result": {},
            "trace": f'Task {e.args[0]} not children.'
            } 
        return info
    
