import re
from django_logging import log as logger

from datetime import datetime, timedelta
from jinja2 import Template

from jira import JIRA
from .models import JitaConnect, JiraFilters, JiraExercise
from accounts.models import CustomUser


class JiraTasks:
    def __init__(self) -> None:
        self.filters = JiraFilters.objects.all()
        try:
            server = JitaConnect.objects.get(id=1)
            self.jira = JIRA(
                options={
                    'server': server.url
                    }, 
                basic_auth=(server.username, server.password), timeout=10)
            logger.info({"JiraSunc": {"Jira connect server": {"server": server.url, "result": str(self.jira)}}})
        except JitaConnect.DoesNotExist as e:
            raise Exception('JIRA: Отсутвуют настройки подключения')

    def jsql_parse(self, data, user, sdate=None, edate=None):
        # username, useremail, 
        # current_week_day_monday, current_week_day_tuesday, current_week_day_wednesday, current_week_day_thursday, current_week_day_friday, current_week_day_saturday, current_week_day_sunday
        # previous_week_day_monday, previous_week_day_tuesday, previous_week_day_wednesday, previous_week_day_thursday, previous_week_day_friday, previous_week_day_saturday, previous_week_day_sunday
        template = Template(data)
        return template.render(**self.get_week_days(), sdate=sdate, edate=edate, username=user.username, useremail=user.email)

    def get_week_days(self, today=datetime.today()):
        return {
            'today': today.strftime('%Y/%m/%d'),
            'current_week_day_monday': (today - timedelta(datetime.weekday(today))).strftime('%Y/%m/%d'),
            'current_week_day_tuesday': (today + timedelta(1 - datetime.weekday(today))).strftime('%Y/%m/%d'),
            'current_week_day_wednesday': (today + timedelta(2 - datetime.weekday(today))).strftime('%Y/%m/%d'),
            'current_week_day_thursday': (today + timedelta(3 - datetime.weekday(today))).strftime('%Y/%m/%d'),
            'current_week_day_friday': (today + timedelta(4 - datetime.weekday(today))).strftime('%Y/%m/%d'),
            'current_week_day_saturday': (today + timedelta(5 - datetime.weekday(today))).strftime('%Y/%m/%d'),
            'current_week_day_sunday': (today + timedelta(6 - datetime.weekday(today))).strftime('%Y/%m/%d')
        }

    def get_filters(self, user):
        if user.user_filter_custom:
            return user.user_filter.all()
        else:
            try:
                task = JiraExercise.objects.get(name='jira_all_sync_once_a_week')
                return task.filter.all()
            except JiraExercise.DoesNotExist:
                return []

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
        
        return int(hour), int(minute)


    def get_time_spent(self, time_spents, date, timeSpent):
        # print('time', timeSpent)
        old_time = time_spents.get(date)
        if old_time:
            hour, minute = self.parse_time(old_time)
            _hour, _minute = self.parse_time(timeSpent)
            # print('BASE TIME:', hour, 'h', minute, 'm', ', ADD TIME:', _hour, 'h', _minute, 'm')
            return f"{hour + _hour}h {minute + _minute}m"
        else:
            return timeSpent

    def get_worksheets(self, worklog, user):
        time_spents = {}
        for log in worklog:
            print('log:', log)
            #print('logAttr:', log.__dict__)
            print('autor:', log.author.name, ', user:', user.username)
            created =  datetime.strptime(log.started, '%Y-%m-%dT%H:%M:%S.%f%z')
            if log.author.name == user.username and datetime.now().year == created.year:
                date = created.strftime('%Y-%m-%d')
                print('date:', date, 'timeSpent', log.timeSpent)
                time_spents[date] = self.get_time_spent(time_spents, date, log.timeSpent)
        return time_spents

    def check_dictkey(self, dict, key):
        try:
             print(dict[key])
        except KeyError as e:
            dict

    def get_tasks(self, users, sdate=None, edate=None, filters=None):
        tasks = {}
        logger.info({"JiraSunc": {"users": [user.username for user in users]}})
        for user in users:
            filters = JiraFilters.objects.filter(id__in=filters) if filters else self.get_filters(user)
            logger.info({"JiraSunc": {"Get jira filters": {"user": user.username, "filters": [f.jsql for f in filters]}}})
            for filter in filters:
                # print('Filter', filter)
                jsql = self.jsql_parse(filter.jsql, user, sdate, edate)
                # print('JSQL', jsql)
                logger.info({"JiraSunc": {"Search user issues": {"user": user.username, "filter_jinja": filter.jsql, "filter_jsql": jsql}}})
                issues_list = self.jira.search_issues(jsql)
                # print('ISSUES', issues_list)
                logger.info({"JiraSunc": {"Tasks search worklog": {"user": user.username, 'issue_list': str(issues_list), }}})
                for issue in issues_list:
                    # print('worklogs:', issue.fields.worklog.worklogs)
                    worklog = self.get_worksheets(issue.fields.worklog.worklogs, user)
                    project = issue.get_field('project').key
                    logger.info({"JiraSunc": {"Get worklog":{"user": user.username, "issue": str(issue), "worklog": str(worklog)}}})
                    if worklog:
                        # print(worklog)
                        for date, time in worklog.items():
                            date_to_datetime = datetime.strptime(date, '%Y-%m-%d')
                            dates = self.get_week_days(date_to_datetime)
                            d =  datetime.strptime(dates.get('current_week_day_monday'), '%Y/%m/%d').strftime('%Y-%m-%d')
                            # print('WEEKDAY', d)

                            issue_info = {
                                    "projectname": issue.get_field('project').name,
                                    "worklog": {date: time},
                                    "status": issue.get_field('status').name,
                                    "summary": issue.get_field('summary'),
                                    "link": issue.permalink()
                                }
                            # print('ISSUE INFO', issue_info)
                            logger.info({"JiraSunc": {"Append list issues info": {"user": user.username, "useremail": user.email, "week": d, "project": project, "issue": issue.key, "issue_info": issue_info}}})
                            try:
                                worklog = tasks[user.email][d][project][issue.key]
                                # print(f'WORKLOG: {worklog}')
                                if worklog.get('worklog'):
                                    # print('WORKLOG EXIST')
                                    tasks[user.email][d][project][issue.key]['worklog'][date] = time
                                else:
                                    # print('WORKLOG NOT EXIST')
                                    tasks[user.email][d][project][issue.key] = issue_info
                            except KeyError as e:
                                # print('KEY ERROR', e.args, 'List:', tasks)
                                # Неделя
                                if e.args[0] == user.email:
                                    tasks[user.email] = {d: {project: {issue.key: issue_info}}}
                                elif e.args[0] == d:
                                    tasks[user.email][d] = {project: {issue.key: issue_info}}
                                # Дата
                                elif e.args[0] == project:
                                    tasks[user.email][d][project] = {issue.key: issue_info}
                                # Задача
                                elif e.args[0] == issue.key:
                                    tasks[user.email][d][project][issue.key] =  issue_info
        return tasks
