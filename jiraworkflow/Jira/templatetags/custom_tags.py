import json
import hashlib
from datetime import datetime, timedelta
from django import template
from django_celery_results.models import TaskResult
from timetta.utils import get_children, SyncStatusException, SyncTaskChildrenNone

register = template.Library()


@register.filter(name='items')
def items(data):
    return data.items()

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
        "FAILURE": "color-red tooltip-init",
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
    try:
        u = json.loads(json.loads(kwargs).replace("'", '"'))
        if u.get('username'):
            return u.get('username')
        else:
            return 'не определен'
    except Exception:
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

def check_status_child(parent, task_kwargs=None):
    tasks = []
    result = None
    if task_kwargs:
        children = TaskResult.objects.filter(task_id__in=parent, task_kwargs__contains=task_kwargs)
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
def get_task_children(task, user):
    try:
        _task = TaskResult.objects.get(task_id=task)
        print(task, user, _task)
        return TaskResult.objects.filter(task_id__in=get_children(_task.meta), task_kwargs__contains=user)
    except TaskResult.DoesNotExist:
        return []

@register.simple_tag
def get_status_sync(task, user='', week='', project=''):
    try:
        print('TASK <', task, '> USER <', user, '> WEEK <', week, '> PROJECT <', project, '>')
        users, uresult = check_status_child([task])
        print('USER: ', users, 'RESULT:', uresult)
        weeks, wresult = check_status_child(users)
        print('WEEK: ', weeks, 'RESULT', wresult)
        proj, presult = check_status_child(weeks, user)
        print('PROJ: ', proj, 'RESULT', presult)
        sync, sresult = check_status_child(proj, week)
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
            "status": '',
            "result": {},
            "trace": f'Task {e.args[0]} not children.'
            } 
        return ''
    
