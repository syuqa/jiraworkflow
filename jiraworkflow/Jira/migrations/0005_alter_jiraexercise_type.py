# Generated by Django 4.2.2 on 2023-06-14 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Jira', '0004_alter_jiraexercise_time_alter_jiraexercise_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jiraexercise',
            name='type',
            field=models.CharField(choices=[('daily', 'Ежедневно'), ('monthly', 'Раз в неделю')], default='monthly', max_length=10, verbose_name='Тип'),
        ),
    ]
