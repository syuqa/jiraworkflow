# Generated by Django 4.2.2 on 2023-06-14 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetta', '0009_timettaprojects_meeting_template'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timettaprojects',
            name='meeting_template',
            field=models.CharField(default='{{summary}}', max_length=600, verbose_name='Сообщение в тиметте'),
        ),
    ]
