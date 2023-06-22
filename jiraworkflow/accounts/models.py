from django.db import models
from django.contrib.auth.models import AbstractUser
from multiselectfield import MultiSelectField


class CustomUser(AbstractUser):
   week_choices = (
            (1, 'Понедельник'),
            (2, 'Вторник'),
            (3, 'Среда'),
            (4, 'Четверг'),
            (5, 'Пятница'),
            (6, 'Cуббота'),
            (7, 'Воскресенье')
        )
   synchronization_custom = models.BooleanField(default=False)
   synchronization_meetings = models.BooleanField(default=False)
   synchronization_meetings_key = models.CharField('Токен доступа к Я.Календарю', max_length=50, null=True, blank=True)
   synchronization = models.BooleanField(default=False)
   synchronization_day_of_week = MultiSelectField('День запуска', choices=week_choices, max_length=7, default=7)
   user_time = models.CharField('Время запуска', max_length=5, default='23:00')
   user_filter = models.ManyToManyField('Jira.jirafilters', null=True, blank=True, verbose_name='Фильтр')
   user_filter_custom = models.BooleanField(default=False)

