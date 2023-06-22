import json

from celery import shared_task
from .processor import TimettaSync, YandexCalendarTasks
from accounts.models import CustomUser

@shared_task(bind=True, name="test_task")
def test_task(self):
    print(f'Request: {self.request}')

@shared_task(bind=True, name="Timetta: Синхронизация по пользователям")
# 'Timetta: Синхронизация по пользователям'
def timetta_sync_users(self, issues):
    for useremail, weeks in issues.items():
        print(f'{useremail}: CREATE TASK SYNC USER')
        # Task
        timetta_sync_week.apply_async(
            kwargs={"useremail": useremail, "weeks": weeks})
        # Mitings
        meetings_sync.apply_async(
                kwargs={"user": useremail}
            )


@shared_task(bind=True, name="Timetta: Синхронизация по неделям")
# 'Timetta: Синхронизация по неделям'
def timetta_sync_week(self, useremail, weeks):
    for week, projects in weeks.items():
        print(f'{useremail}: CREATE TASK SYNC WEEEK {week}')
        timetta_sync_project.apply_async(
            kwargs={"useremail": useremail, "week": week, "projects": projects})
    return useremail

@shared_task(bind=True, name="Timetta: Синхронизация по проектам")
#'Timetta: Синхронизация по проектам'
def timetta_sync_project(self, useremail, week, projects):
    for project, issues in projects.items():
        print(f'{useremail}: CREATE TASK SYNC PROJECT {project} :: week {week}')
        try:
            timetta_sync.apply_async(
                kwargs={"useremail": useremail, "week": week, "project": project, "issues": issues}).result
        except Exception as e:
            print(e)
    return week

@shared_task(bind=True, name="Timetta: Синхронизация задач")
# 'Timetta: Синхронизация задач'
def timetta_sync(self, useremail, week, project, issues, ):
    print(f'{useremail}: CREATE SYNC {project} :: week {week}')
    timetta = TimettaSync()
    return timetta._sync(useremail, week, project, issues)


@shared_task(bind=True, name="Timetta: Синхронизация митингов")
def meetings_sync(self, user):
    print(f'{user}: CREATE SYNC MEETINGS')
    u = CustomUser.objects.get(email=user)
    if u.synchronization_meetings:
        meeting = YandexCalendarTasks(u)
        return meeting.sync()
    else:
        return {"status": "Synchronization meetings disable"}