# Generated by Django 4.2.1 on 2023-06-05 01:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_customuser_synchronization_day_of_week_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='time',
            new_name='user_time',
        ),
    ]
