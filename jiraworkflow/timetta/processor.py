
import json
import uuid
import requests
import re

from datetime import datetime, timedelta
from .wp_auth import WPAuth
from .utils import auth, DowloadCalendarException
from accounts.models import CustomUser
from timetta.models import TimettaProjects, TimettaConnect
from Jira.processor import JiraTasks
from jinja2 import Template
from django_logging import log as logger

import icalendar
import recurring_ical_events

class TimettaHTTPRequests:
    def __init__(self):
        self.main_headers = {"Content-Type": "application/json"}
        self.url = 'https://auth.timetta.com/'
        wp_auth = WPAuth()
        auth_token = wp_auth.get_auth_token()
        if auth_token is None:
            raise Exception("Timetta: Couldn't get auth_token!")
        print(auth_token)

    @auth("wp")
    def get_timelines(self, sheet, headers=None):
        url = f"https://api.timetta.com/odata/TimeSheets({sheet})?$expand=approvalStatus($select=id,name,code),timeSheetLines($select=id,date,orderNumber,rowVersion;$expand=project($select=id,name;$expand=billingType($select=code),organization($select=id,name)),projectTask($select=id,name,leadTaskId),timeAllocations($orderby=date;$select=id,duration,comments,date,decimalValue1,decimalValue2;$expand=);$orderby=orderNumber),timeOffRequests($select=id;$expand=approvalStatus($select=id,name,code),timeOffType($select=id,name),timeAllocations($orderby=date))"
        return requests.get(url=url, headers=headers)

    @auth("wp")
    def get_timesheet_role(self, sheet, project, headers=None):
        url = f"https://api.timetta.com/odata/TimeSheets({sheet})/WP.GetRoles(projectId={project})"
        return requests.get(url=url, headers=headers)

    @auth("wp")
    def get_timeseets(self, date, user, headers=None):
        url = f"https://api.timetta.com/odata/TimeSheets/GetIdForPeriod(date={date},userId={user})"
        return requests.get(url=url, headers=headers)

    @auth("wp")
    def get_user(self, email, headers=None):
        url = f"https://api.timetta.com/odata/Users?$filter=startswith(email,'{email}')"
        return requests.get(url=url, headers=headers)

    @auth("wp")
    def get_tasks(self, project, headers=None):
        url = f"https://api.timetta.com/odata/Projects({project})/ProjectTasks?$select=name,id"
        return requests.get(url=url, headers=headers)

    @auth("wp")
    def projects(self, headers=None):
        url = f"https://api.timetta.com/odata/ProjectTotals?$select=id&$filter=((project/stateId eq CD2F2BF7-9388-43B8-9039-DDED9700AFD2) or (project/stateId eq 9752FC91-714A-414F-9C03-8A3A1D6CCE06))&$expand=project($select=name)&$orderby=project/name"
        return requests.get(url=url, headers=headers)

    @auth("wp")
    def project_and_task(self, headers=None):
        url = f"https://api.timetta.com/odata/ProectTotals?$select=id&$filter=(project/stateId eq CD2F2BF7-9388-43B8-9039-DDED9700AFD2)&$expand=project($select=name;$expand=ProjectTasks($select=id,name))&$orderby=project/name"
        return requests.get(url=url, headers=headers)
    
    @auth("wp")
    def update_timesheet(self, timesheet, headers=None):
        url = f"https://api.timetta.com/odata/TimeSheets({timesheet.get('id')})"
        return requests.put(url=url, headers={**headers, **self.main_headers}, data=json.dumps(timesheet))
    
    @auth("wp")
    def post_time(self, timeEntries, headers=None):
        url = f"https://api.timetta.com/odata/TrackTime"
        logger.info({"JiraSunc": {"Timetta post time": {"time entries": timeEntries, 'url': url}}})
        return requests.post(url=url, headers={**headers, **self.main_headers}, data=json.dumps(timeEntries))
    

class TimettaSync(TimettaHTTPRequests):
    def __init__(self):
        super().__init__()

    def get_user_id(self, user):
        print('---------/ GET USER ID /----------')
        userdata = self.get_user(user).get('value')
        print('DATA:', userdata)
        if len(userdata) > 0:
            u = userdata.pop()
            print('U:', u.get('id'))
            return u.get('id')
        else:
            raise Exception(f'Sync: User with email {user}, in Timetta, not found')

    def get_timesheet(self, date, user):
        print('---------/ GET TIMESEET ID /----------')
        sheet = self.get_timeseets(date, self.get_user_id(user))
        print('DATA:', sheet)
        return sheet.get('value')
    
    def get_role(self, sheet, project):
        roles = self.get_timesheet_role(sheet=sheet, project=project).get('value')
        if len(roles) > 0:
            return roles.pop().get('id')
        else:
            raise Exception(f'Sync: User role not defined in project {project}, sheet {sheet}')
        
    def parse_time(self, time):
        # print('parse time:', time)
        _time = { re.match(r"(?P<value>[0-9]*)(?P<key>[h,m])", t).group('key'): re.match(r"(?P<value>[0-9]*)(?P<key>[h,m])", t).group('value') for t in re.findall(r"[0-9]*[h,m]", time)}
        # print('search time:', _time)

        hour = 0
        minute = 0

        if _time.get('h'):
            hour = _time.get('h')
        if _time.get('m'):
            minute = _time.get('m')
        
        return int(hour) + (int(minute) % (60 * 24) / 60)

    def create_timeline(self, timesheets, project, task):
        sheets = timesheets.get("id")
        print('-------------------')
        print(timesheets)
        print('-------------------')
        print(f'create timeline, sheets: {sheets}')
        sheetlines = []
        role = self.get_role(sheets, project)
        for line in timesheets.get('timeSheetLines'):
            print('LINE -->', line)
            sheetlines.append({
                "id": line.get("id"),
                "projectId":  line['project']['id'] if line.get('project') else None,
                "projectTaskId": line['projectTask']['id'] if line.get('projectTask') else None,
                "orderNumber": line.get('orderNumber'),
                "roleId": role,
                "timeAllocations": line.get('timeAllocations')
            })
        sheetlines.append({
                            "projectId": project,
                            "projectTaskId": task,
                            "orderNumber": len(sheetlines),
                            "roleId": role,
                            "timeAllocations": []
                        })
        payload =   {
                        "id": timesheets.get('id'),
                        "rowVersion": timesheets.get('rowVersion'),
                        "timeSheetLines": sheetlines,
                    }
        
        status = self.update_timesheet(payload)
        return status

    def get_timeline(self, sheet, _project, _task):
        timeline = self.get_timelines(sheet)
        # CREATE TIMELINE LIST
        if timeline['approvalStatus']['code'] == 'Draft':
            # CREATE TIMELINE LIST
            timeline_list = {}
            for line in timeline.get('timeSheetLines'):
                print(line)
                project = line.get('project')
                project_task = line.get('projectTask')
                if project and project_task:
                    print(project)
                    project_id = project.get('id')
                    project_task_id = project_task.get('id')
                    timeline_list[hash(project_id + project_task_id)] = {'id': line.get('id'), 'rowVersion': line.get('rowVersion')}
            # CHECK TIMELINE PROJECT AND TASK
            if hash(_project + _task) in [*timeline_list.keys()]:
                print('timeline is defined')
                return True
            else:
                print('timeline not defined')
                return self.create_timeline(timeline, _project, _task)

        else:
            return False

    def meetings(self, useremail, week, _role, _project):
        u = CustomUser.objects.get(email=useremail)
        if u.synchronization_meetings:
            pass

    def _sync(self, useremail, week, project, issues, strategy='replace'):
        logger.info({"JiraSunc": {"Timetta": {"TimettaSync": {"user": useremail, "week": week, "project": project, "issues": issues, "strategy": strategy}}}})
        p = TimettaProjects.objects.get(jira_tag=project)
        t = TimettaConnect.objects.get(id=1)
        # Параметры
        _sheet = self.get_timesheet(user=useremail, date=week)
        _project = p.project_id
        _task = p.task_id
        _role = self.get_role(_sheet, _project)
        logger.info({"JiraSunc": {"Timetta": {"TimettaSyncData": {"seet": _sheet, "project": _project, "task": _task, "role": _role}}}})
        # Задачи
        self.get_timeline(_sheet, _project, _task)
        timeEntries = []
        for issue, task_property in issues.items():
            logger.info({"JiraSunc": {"Timetta": {"Timetta create time entries": {"issue": issue, "task_property": task_property}}}})
            for date, time in task_property.get('worklog').items():
                logger.info({"JiraSunc": {"Timetta": {"Timetta create time entries": {"date": date, "time": time}}}})
                timeEntries.append({
                    "date": date,
                    "comment": Template(t.simple).render(
                                                            issue=issue, 
                                                            issue_summary=task_property.get('summary'),
                                                            issue_link=task_property.get('link'),
                                                            issue_status=task_property.get('status')
                                                        ),
                    "hours": self.parse_time(time),
                    "userId": self.get_user_id(useremail),
                    "projectId": _project,
                    "projectTaskId": _task,
                    "activityId": None,
                    "roleId": _role
                })
    
        
        payload = {
            "strategyIfEntryExists": strategy,
            "timeEntries": timeEntries
        }
        logger.info({"JiraSunc": {"Timetta": {"Timetta create playload": {"payload": payload}}}})

        self.post_time(payload)
        return payload


    def sync(self, strategy='replace'):
        jira = JiraTasks()
        _tasks = jira.get_tasks()
        # Task list
        for useremail, weeks in _tasks.items():
            for week, projects in weeks.items():
                _sheet = self.get_timesheet(user=useremail, date=week)
                # Проект
                for project, isues in projects.items():
                        p = TimettaProjects.objects.get(jira_tag=project)
                        t = TimettaConnect.objects.get(id=1)
                        _project = p.project_id
                        _task = p.task_id
                        _role = self.get_role(_sheet, _project)
                        timeEntries = []
                        for issue, task_property in isues.items():
                            for date, time in task_property.get('worklog').items():
                                timeEntries.append({
                                    "date": date,
                                    "comment": Template(t.simple).render(
                                                                            issue=issue, 
                                                                            issue_summary=task_property.get('summary'),
                                                                            issue_link=task_property.get('link'),
                                                                            issue_status=task_property.get('status')
                                                                        ),
                                    "hours": self.parse_time(time),
                                    "userId": self.get_user_id(useremail),
                                    "projectId": _project,
                                    "projectTaskId": _task,
                                    "activityId": None,
                                    "roleId": _role
                                })

                        payload = {
                            "strategyIfEntryExists": strategy,
                            "timeEntries": timeEntries
                        }

                        self.post_time(payload)





class YandexCalendarTasks(TimettaSync):
    def __init__(self, user) -> None:
        super().__init__()
        self.user = user
        self.tz = 'Europe/Moscow'
        self.url = f'https://calendar.yandex.ru/export/ics.xml?private_token={user.synchronization_meetings_key}&tz_id={self.tz}'
        print(self.url)

    def get_week_days(self, today=datetime.today()):
        return {
            'today': today.strftime('%Y/%m/%d'),
            'current_week_day_monday': (today - timedelta(datetime.weekday(today))),
            'current_week_day_sunday': (today + timedelta(6 - datetime.weekday(today)))
        }

    def get_custom_rule(self, summary):
        logger.info({"JiraSunc": {"Meetings": {"SEATCH CUSTOM PROJECT RULE": {"summary":str(summary)}}}})
        for project in TimettaProjects.objects.all():
            print('PROJECT', project.jira_tag)
            # logger.info({"JiraSunc": {"Meetings": {"For project": {"project": project.jira_tag, "meeting_summary": project.meeting_summary, "meeting_task_id": project.meeting_task_id}}}})
            print('SYMMARY', project.meeting_summary)
            if project.meeting_summary and project.meeting_task_id:
                for line in project.meeting_summary.split(';'):
                    print('line', line)
                    # logger.info({"JiraSunc": {"Meetings": {"Check summary": {"calendar summary": str(summary).lower(), "Rule summary": line.lower()}}}})
                    print(line.lstrip().lower(), 'in', str(summary).lower())
                    if line.lstrip().lower() in str(summary).lower():
                        return project
                    else:
                        e = []
                        tags = line.lstrip().split(',')
                        for tag in tags:
                            if tag.lower() in str(summary).lower():
                                e.append(tag)
                        if len(e) == len(tags) and len(tags) > 0:
                            return project
            else:
                return None
                

    def get_default_rule(self):
        project = TimettaProjects.objects.filter(meeting_summary='*')
        if project.exists():
           return project.first()
        else:
            return None

    def get_project(self, summary):
        logger.info({"JiraSunc": {"Meetings": {"GET PROJECT": {"summary":summary}}}})
        custom_project = self.get_custom_rule(summary)
        if custom_project:
           logger.info({"JiraSunc": {"Meetings": {"Project custom": {"project": custom_project.jira_tag}}}})
           return custom_project
        else:
           project = self.get_default_rule()
           logger.info({"JiraSunc": {"Meetings": {"Project default": {"project": project.jira_tag}}}})
           return project

    def get_time(self, sdate, edate):
        return ((edate - sdate).total_seconds() / 60) % (60 * 24) / 60

    def get_task(self, sdate=None, edate=None):
        tasks = []
        _sweek = sdate if sdate else self.get_week_days().get('current_week_day_monday')
        _eweek = edate if edate else self.get_week_days().get('current_week_day_sunday')
        logger.info({"JiraSunc": {"Meetings": {"Import calendar": {"url": self.url}}}})
        self.req = requests.get(self.url)
        if self.req.status_code == 200:
            timmeta_user_id = self.get_user_id(self.user.email)
            calendar = icalendar.Calendar.from_ical(self.req.content)
            events = recurring_ical_events.of(calendar).between(_sweek, _eweek)
            logger.info({"JiraSunc": {"Meetings": {"Search evens in date": {"sdate": _sweek.strftime('%Y/%m/%d'), "edate": _eweek.strftime('%Y/%m/%d')}}}})
            for component in events:
                event_sdate = component.get("dtstart").dt
                evant_edate = component.get("dtend").dt
                logger.info({
                    "JiraSunc": {
                        "Meetings": {
                            "For events": 
                            {"summary": str(component.get('summary')), 
                             "edate": str(component.get('dtend').dt),
                             "sdate": str(component.get('dtstart').dt),
                             "time": self.get_time(event_sdate, evant_edate),
                             "url": str(component.get('url'))
                             }
                        }
                    }
                })
                date = event_sdate.strftime('%Y-%m-%d')
                project = self.get_project(str(component.get('SUMMARY')))
                logger.info({"JiraSunc": {"Meetings": {"Get project": {"project": project.jira_tag, "project_id": project.project_id, "task_id": project.meeting_task_id}}}})
                if project:
                    sheet = self.get_timesheet(user=self.user.email, date=_sweek)
                    logger.info({"JiraSunc": {"Meetings": {"Get sheet": {"sheet": sheet}}}})
                    role = self.get_role(sheet, project.project_id)
                    logger.info({"JiraSunc": {"Meetings": {"Get role": {"role": role}}}})
                    etm = self.get_timeline(sheet, project.project_id, project.meeting_task_id)
                    logger.info({"JiraSunc": {"Meetings": {"Chech timeline": {"sheet": sheet, "project_id": project.project_id, "meeting_task_id": project.meeting_task_id, "enable": etm}}}})
                    data = {
                                "date": date,
                                "hours": self.get_time(event_sdate, evant_edate),
                                "comment": Template(project.meeting_template).render(
                                    summary=str(component.get('summary')),
                                    description=str(component.get('description')),
                                    organizer=str(component.get('organizer')),
                                    edate=str(component.get('dtend').dt),
                                    sdate=str(component.get('dtstart').dt),
                                    time=self.get_time(event_sdate, evant_edate),
                                    url=str(component.get('url'))
                                    ),
                                "userId": timmeta_user_id,
                                "projectId": project.project_id,
                                "projectTaskId": project.meeting_task_id,
                                "activityId": None,
                                "roleId": role
                            }
                    tasks.append(data)
                    logger.info({"JiraSunc": {"Meetings": {"Append data timeline list": {"timeline data": data}}}})
            return self.req, tasks
        else:
            return self.req, tasks
    
    def sync(self, sdate=None, edate=None, strategy='merge'):
        request, tasks = self.get_task(sdate, edate)
        payload = {
                    "strategyIfEntryExists": strategy,
                    "timeEntries": tasks
                }
        logger.info({"JiraSunc": {"Meetings": {"Post playload": {"playload": payload}}}})
        if request.status_code == 200:
            self.post_time(payload)
            return payload
        else:
            raise DowloadCalendarException(request)