from django.db import models

# Create your models here.
class TimettaConnect(models.Model):
    url = models.CharField('Адрес сервера', max_length=300)
    username = models.CharField('Имя пользователя', max_length=300)
    password = models.CharField('Пароль или токен', max_length=50)
    tokens = models.JSONField('Токены API', default=dict)
    projects_list = models.JSONField('Проекты', default=dict)
    simple = models.TextField('Шаблон', default="{{ issue }}: {{ issue_link }}")

class TimettaProjects(models.Model):
    jira_tag = models.CharField('Сокращенное имя, из Jira', max_length=50)
    name = models.CharField('Наименование проекта', max_length=300)
    project_id = models.CharField('Наименование проекта', max_length=300)
    task = models.CharField('Задача', max_length=300)
    task_id = models.CharField('ID проекта', max_length=300)