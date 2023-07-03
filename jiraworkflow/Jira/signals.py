from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import JiraExercise
from django_celery_beat.models import CrontabSchedule, PeriodicTask

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