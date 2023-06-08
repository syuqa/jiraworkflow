from django.db import models
from multiselectfield import MultiSelectField

# Create your models here.

class JitaConnect(models.Model):
    url = models.CharField('Адрес сервера', max_length=300)
    username = models.CharField('Имя пользователя', max_length=300)
    password = models.CharField('Пароль или токен', max_length=50)


class JiraFilters(models.Model):
    name = models.CharField('Имя', max_length=300)
    jsql = models.CharField('Запрос', max_length=500)

    def __str__(self) -> str:
        return self.name

class JiraExercise(models.Model):
    type_choices = {
        ('daily', 'Ежедневно'),
        ('monthly', 'Раз в неделю'),
    }
    week_choices = (
            (1, 'Понедельник'),
            (2, 'Вторник'),
            (3, 'Среда'),
            (4, 'Четверг'),
            (5, 'Пятница'),
            (6, 'Cуббота'),
            (7, 'Воскресенье')
        )
    name = models.CharField('Имя', max_length=50, null=True, blank=True)
    enable = models.BooleanField(default=False)
    day_of_week = MultiSelectField('Время запуска', choices=week_choices, max_length=7, default=5)
    type = models.CharField('Тип', max_length=10, choices=type_choices, default='monthly')
    time = models.CharField('Время запуска', max_length=5, default='23:00')
    filter = models.ManyToManyField(JiraFilters, null=True, verbose_name='Фильтр')
