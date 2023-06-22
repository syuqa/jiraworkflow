# Generated by Django 4.2.2 on 2023-06-15 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetta', '0010_alter_timettaprojects_meeting_template'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timettaconnect',
            name='projects_list',
        ),
        migrations.AlterField(
            model_name='timettaconnect',
            name='tokens',
            field=models.JSONField(blank=True, default=dict, verbose_name='Токены API'),
        ),
    ]
