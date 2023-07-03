from django.dispatch import receiver
from django.db.models.signals import post_save
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from .models import CustomUser
from Jira.models import JiraExercise 


@receiver(post_save, sender=CustomUser)
def post_save_exercise(created, instance, **kwargs):
    if created:
        if '@' in instance.username:
            instance.username = instance.username.split('@')[0]
            instance.save()
    else:
        day_of_week = ','.join(instance.synchronization_day_of_week)
        try:
            time = instance.user_time.split(':')
            cron = CrontabSchedule.objects.get(hour=time[0], minute=time[1], day_of_week=day_of_week, month_of_year='*', day_of_month='*')
        except CrontabSchedule.DoesNotExist:
            cron = CrontabSchedule.objects.create(hour=time[0], minute=time[1], day_of_week=day_of_week, month_of_year='*', day_of_month='*')

        try:
            shedule = PeriodicTask.objects.get(name=f'jira_user{instance.id}_sync_once_a_week')
            shedule.enabled = instance.synchronization_custom
            shedule.crontab = cron
            shedule.save()
        except PeriodicTask.DoesNotExist as e:
            print(e)
            PeriodicTask.objects.create(name=f'jira_user{instance.id}_sync_once_a_week', task='Jira: Выгрузка задач', crontab=cron)
        