import json

from django.dispatch import receiver
from django.db.models.signals import post_save
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from django_celery_results.models import TaskResult
from django.core.mail import send_mail
from django.conf import settings

from .models import JiraExercise
from accounts.models import CustomUser
from .templatetags.custom_tags import get_status_sync

from timetta.utils import get_children

class SyncException(Exception):
    def __init__(self, task):
        self.task = task
        self.send_message = False
        self.task_traceback = task.traceback
        self.task_result = task.result
        self.task_kwargs = eval(json.loads(task.task_kwargs))
        self.email = []

    def traceback(self):
        return self.task_traceback
    
    def result(self):
        return self.task_result
    
    def emails(self):
        return list(set(self.email))

    def __str__(self):
        if self.task.task_name == 'Jira: Выгрузка задач':
            for u in CustomUser.objects.filter(synchronization=True):
                if u.email in self.task.result and u.notification in ['enable', 'only_error']:
                    self.email.append(u.email)
            return 'Ошибка выгрузки задач с Jira'
        elif self.task.task_name == 'Timetta: Синхронизация задач':
            # project_task = TaskResult.objects.filter(task_name="Timetta: Синхронизация по проектам", meta__contains=self.task.task_id).first()
            user = CustomUser.objects.get(email=self.task_kwargs.get('useremail'))
            task_project = TaskResult.objects.filter(task_name="Timetta: Синхронизация по проектам", meta__contains=self.task.task_id).first()
            task_week = TaskResult.objects.filter(task_name="Timetta: Синхронизация по неделям", meta__contains=task_project.task_id).first()
            task_user = TaskResult.objects.filter(task_name="Timetta: Синхронизация по пользователям", meta__contains=task_week.task_id).first()
            task_head = TaskResult.objects.filter(task_name="Jira: Выгрузка задач", meta__contains=task_user.task_id).exists()
            print(f'EXC-HEADER: Timetta: Синхронизация задач > {task_project.task_id} > {task_week.task_id} > {task_user.task_id} => {task_head}')
            print(f'EXC-NOTIFI: {user.email}, {user.notification}')
            if user.notification in ['enable', 'only_error'] and task_head:
                self.email.append(self.task_kwargs.get('useremail'))            
            return f'Ошибка синхронизация задач, неделя {self.task_kwargs.get("week")}, проект {self.task_kwargs.get("project")}'
        elif self.task.task_name == 'Timetta: Синхронизация митингов':
            user = CustomUser.objects.get(email=self.task_kwargs.get('useremail'))
            if user.notification in ['enable', 'only_error'] and self.task_kwargs.get('custom') and self.task_kwargs.get('sync'):
                self.email.append(self.task_kwargs.get('useremail'))
            return f"Ошибка синхронизации митингов (задач из календаря)"
        else:
            return f"Ошибка выпоолнения задачи {self.task.task_id}"


@receiver(post_save, sender=JiraExercise)
def post_save_exercise(created, instance, **kwargs):
    day_of_week = ','.join(instance.day_of_week)
    if instance.name:
        try:
            time = instance.time.split(':')
            cron = CrontabSchedule.objects.get(hour=time[0], minute=time[1], day_of_week=day_of_week, month_of_year='*', day_of_month='*')
        except CrontabSchedule.DoesNotExist:
            cron = CrontabSchedule.objects.create(hour=time[0], minute=time[1], day_of_week=day_of_week, month_of_year='*', day_of_month='*')

        try:
            shedule = PeriodicTask.objects.get(name=instance.name)
            shedule.enabled = instance.enable
            shedule.crontab = cron
            shedule.save()
        except PeriodicTask.DoesNotExist as e:
            print(e)
            PeriodicTask.objects.create(name=instance.name, task='Jira: Выгрузка задач', crontab=cron)


@receiver(post_save, sender=TaskResult)
def post_save_taskresult(created, instance, **kwargs):
    try:
        if instance.status == 'FAILURE':
            raise SyncException(instance)
        else:
           task_kwargs = eval(json.loads(instance.task_kwargs))
           if instance.task_name in ['Timetta: Синхронизация задач', 'Timetta: Синхронизация митингов']:
               user = CustomUser.objects.get(email = task_kwargs.get('useremail'))
               if user.notification == 'enable':
                    if instance.task_name == 'Timetta: Синхронизация задач':
                        send_mail(subject="Синхронизация задач", message="Задача выполнена", recipient_list=[task_kwargs.get('useremail')], from_email=settings.DEFAULT_FROM_EMAIL)
                    elif instance.task_name == 'Timetta: Синхронизация митингов':
                        send_mail(subject="Синхронизации митингов (задач из календаря)", message="Задача выполнена", recipient_list=[task_kwargs.get('useremail')], from_email=settings.DEFAULT_FROM_EMAIL)

    except SyncException as e:
        print(e, e.args, e.emails(), e.traceback())
        if len(e.emails()) > 0:
            send_mail(subject=str(e), message=f"""{e.traceback()}""", recipient_list=e.emails(), from_email=settings.DEFAULT_FROM_EMAIL)
    except BaseException as e:
        print(e)
