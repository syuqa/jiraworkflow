from django.db import models

# Create your models here.
class TimettaConnect(models.Model):
    url = models.CharField('Адрес сервера', max_length=300)
    username = models.CharField('Имя пользователя', max_length=300)
    password = models.CharField('Пароль или токен', max_length=50)
    tokens = models.JSONField('Токены API', blank=True, default=dict)
    simple = models.TextField('Шаблон', default="{{ issue }}: {{ issue_link }}")
    

class CalendarSummary(models.Model):
    summary = models.CharField('Задание', max_length=400)

class TimettaProjects(models.Model):
    jira_tag = models.CharField('Сокращенное имя, из Jira', max_length=50)
    name = models.CharField('Наименование проекта', max_length=300)
    project_id = models.CharField('Наименование проекта', max_length=300)
    task = models.CharField('Задача', max_length=300)
    task_id = models.CharField('ID проекта', max_length=300)
    meeting_summary = models.CharField('Заголовок митинг', max_length=600, null=True, blank=True)
    meeting_task_id = models.CharField('Задача митинга', max_length=300, null=True, blank=True)
    meeting_template = models.CharField('Сообщение в тиметте', max_length=600, default="{{summary}}")
    
