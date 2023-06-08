
import json
import uuid
import requests
import re

from datetime import datetime
from .wp_auth import WPAuth
from .utils import auth
from accounts.models import CustomUser
from timetta.models import TimettaProjects, TimettaConnect
from Jira.processor import JiraTasks
from jinja2 import Template

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
        print(timeline['approvalStatus'])
        if timeline['approvalStatus']['code'] == 'Draft':
            # CREATE TIMELINE LIST
            timeline_list = {}
            for line in timeline.get('timeSheetLines'):
                project = line.get('project')
                project_task = line.get('projectTask')
                if project and project_task:
                    project_id = project.get('id')
                    project_task_id = project_task.get('id')
                    timeline_list[hash(project_id + project_task_id)] = {'id': line.id, 'rowVersion': line.rowVersion}
            # CHECK TIMELINE PROJECT AND TASK
            if hash(_project + _task) in [*timeline_list.keys()]:
                print('timeline is defined')
                return True
            else:
                print('timeline not defined')
                return self.create_timeline(timeline, _project, _task)

        else:
            return False

    def _sync(self, useremail, week, project, isues, strategy='replace'):
        p = TimettaProjects.objects.get(jira_tag=project)
        t = TimettaConnect.objects.get(id=1)
        # Параметры
        _sheet = self.get_timesheet(user=useremail, date=week)
        _project = p.project_id
        _task = p.task_id
        _role = self.get_role(_sheet, _project)
        # Задачи
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
