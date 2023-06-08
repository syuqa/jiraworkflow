import json

from celery import shared_task
from .processor import JiraTasks
from timetta.tasks import timetta_sync_users
from accounts.models import CustomUser

@shared_task(bind=True, name='Jira: Выгрузка задач')
def jira_sync(self, username="Периодическое задание"):
    jira = JiraTasks()
    issues = jira.get_tasks(CustomUser.objects.filter(synchronization=True, synchronization_custom=False))
    timetta_sync_users.apply_async(kwargs={"issues": issues})
    return issues
    