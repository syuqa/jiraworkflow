from django import forms
from .models import *

class TimettaConnectForm(forms.ModelForm):
    class Meta:
        model = TimettaConnect
        fields = ('url', 'username', 'password')
        widgets = {
            'url': forms.TextInput(attrs={'placeholder':'Адрес сервера'}),
            'username': forms.TextInput(attrs={'placeholder': 'Имя пользователя'}),
            'password': forms.PasswordInput(attrs={'placeholder': 'Пароль или токен'}),
        }

class TimettaProjectsForm(forms.ModelForm):
    class Meta:
        model = TimettaProjects
        fields = ('jira_tag', 'project_id', 'task_id')
        widgets = {
            'jira_tag': forms.TextInput(attrs={'placeholder':'Тег'}),
            'project_id': forms.TextInput(attrs={'placeholder': 'ID проекта'}),
            'task_id': forms.TextInput(attrs={'placeholder': 'ID задачи'}),
        }

class TimettaSimple(forms.ModelForm):
    class Meta:
        model=TimettaConnect
        fields = ('simple', )
        widgets = {
            'simple': forms.Textarea(attrs={'placeholder': 'Шаблон'})
        }