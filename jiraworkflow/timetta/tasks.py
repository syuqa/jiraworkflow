import json

from celery import shared_task
from .processor import TimettaSync, YandexCalendarTasks
from accounts.models import CustomUser

@shared_task(bind=True, name="test_task")
def test_task(self):
    print(f'Request: {self.request}')


@shared_task(bind=True, name="Выборочная синхронизация")
def custom_sync(self, issues, username, mitings, method):
    timetta_sync_users.apply_async(
        kwargs={"issues": issues, "custom": True, "sync": mitings, "method": method}
    )
    return issues

@shared_task(bind=True, name="Timetta: Синхронизация по пользователям")
# 'Timetta: Синхронизация по пользователям'
def timetta_sync_users(self, issues, custom=False, sync=False, method="replace"):
    for useremail, weeks in issues.items():
        print(f'{useremail}: CREATE TASK SYNC USER')
        # Task
        timetta_sync_week.apply_async(
            kwargs={"useremail": useremail, "weeks": weeks, "method":method})
        # Mitings
        meetings_sync.apply_async(
                kwargs={"user": useremail, "custom": custom, "sync": sync}
            )


@shared_task(bind=True, name="Timetta: Синхронизация по неделям")
# 'Timetta: Синхронизация по неделям'
def timetta_sync_week(self, useremail, weeks, method):
    for week, projects in weeks.items():
        print(f'{useremail}: CREATE TASK SYNC WEEEK {week}')
        timetta_sync_project.apply_async(
            kwargs={"useremail": useremail, "week": week, "projects": projects, "method": method})
    return useremail

@shared_task(bind=True, name="Timetta: Синхронизация по проектам")
#'Timetta: Синхронизация по проектам'
def timetta_sync_project(self, useremail, week, projects, method):
    for project, issues in projects.items():
        print(f'{useremail}: CREATE TASK SYNC PROJECT {project} :: week {week}')
        try:
            timetta_sync.apply_async(
                kwargs={"useremail": useremail, "week": week, "project": project, "issues": issues, "method": method}).result
        except Exception as e:
            print(e)
    return week

@shared_task(bind=True, name="Timetta: Синхронизация задач")
# 'Timetta: Синхронизация задач'
def timetta_sync(self, useremail, week, project, issues, method):
    print(f'{useremail}: CREATE SYNC {project} :: week {week}')
    timetta = TimettaSync()
    return timetta._sync(useremail, week, project, issues, method)


@shared_task(bind=True, name="Timetta: Синхронизация митингов")
def meetings_sync(self, user, custom=False, sync=None):
    print(f'{user}: CREATE SYNC MEETINGS', 'self', self)
    u = CustomUser.objects.get(email=user)
    _sync = sync if sync is not None else u.synchronization_meetings
    print('METUNGS IF', custom, _sync, )
    if custom and _sync or not custom and _sync:
         meeting = YandexCalendarTasks(u)
         return meeting.sync()
    else:
        return {"status": "Synchronization meetings disable"}