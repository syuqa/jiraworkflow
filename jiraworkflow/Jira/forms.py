from django import forms
from .models import *
from django_celery_results.models import TaskResult
from django_json_widget.widgets import JSONEditorWidget
from djangocodemirror.fields import CodeMirrorField
class JiraConnectForm(forms.ModelForm):
    class Meta:
        model = JitaConnect
        fields = ('url', 'username', 'password')
        widgets = {
            'url': forms.TextInput(attrs={'placeholder':'Адрес сервера'}),
            'username': forms.TextInput(attrs={'placeholder': 'Имя пользователя'}),
            'password': forms.PasswordInput(attrs={'placeholder': 'Пароль или токен'}),
        }

class JiraFiltersForm(forms.ModelForm):
    class Meta:
        model = JiraFilters
        fields = ('name', 'jsql')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder':'Имя'}),
            'jsql': forms.Textarea(attrs={'placeholder': 'JSQL вырожение'})
        }
        
class JiraExerciseEnableForm(forms.ModelForm):
    class Meta:
        model = JiraExercise
        fields = ('enable',)
        widgets = {
            'enable': forms.CheckboxInput(),
        }

class JiraExerciseForm(forms.ModelForm):
    class Meta:

        time_choices = (
            ('00:00', '00:00'), 
            ('01:00', '01:00'),
            ('02:00', '02:00'), 
            ('03:00', '03:00'),
            ('04:00', '04:00'), 
            ('05:00', '05:00'),
            ('06:00', '06:00'), 
            ('07:00', '07:00'),
            ('08:00', '08:00'), 
            ('09:00', '09:00'),
            ('10:00', '10:00'), 
            ('11:00', '12:00'),
            ('13:00', '13:00'), 
            ('14:00', '14:00'),
            ('15:00', '15:00'), 
            ('16:00', '16:00'),
            ('17:00', '17:00'),
            ('18:00', '18:00'),
            ('19:00', '19:00'), 
            ('20:00', '20:00'),
            ('21:00', '21:00'), 
            ('22:00', '22:00'),
            ('23:00', '23:00'),
        )
        
        week_choices = (
            (1, 'Понедельник'),
            (2, 'Вторник'),
            (3, 'Среда'),
            (4, 'Четверг'),
            (5, 'Пятница'),
            (6, 'Cуббота'),
            (7, 'Воскресенье')
        )

        model = JiraExercise
        filter = forms.ModelMultipleChoiceField(
                            queryset=JiraFilters.objects.all(),
                            widget=forms.CheckboxSelectMultiple,
                            to_field_name='name')
        fields = ('enable', 'time', 'day_of_week', 'filter')
        widgets = {
            'time': forms.Select(choices=time_choices),
            'day_of_week': forms.SelectMultiple(choices=week_choices)
        }

class JiraSyncTraceback(forms.ModelForm):
    class Meta:
        model = TaskResult
        fields = ('traceback', )
        widgets = {
            'traceback': forms.Textarea()
        }

class JsonEditorForm(forms.Form):
    json = forms.CharField(widget=JSONEditorWidget)