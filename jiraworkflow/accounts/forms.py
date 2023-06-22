from django import forms
from .models import *
from djangocodemirror.fields import CodeMirrorField
from djangocodemirror.widgets import CodeMirrorWidget
from Jira.models import JiraFilters, JiraExercise

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserAccountForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'is_superuser')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Логин'}),
            'email': forms.TextInput(attrs={'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Фамилия, Имя'}),
            'is_superuser': forms.CheckboxInput()
        }

class UserSynchronizationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('synchronization', )
        widgets = {
            'synchronization': forms.CheckboxInput()
        }


class UserSyncCustomFilter(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('user_filter_custom', ) 
        widgets = {
            'user_filter_custom': forms.CheckboxInput()
        }


class UserSyncFiters(forms.ModelForm):
    class Meta:
        model = CustomUser
        filter = forms.ModelMultipleChoiceField(
                    queryset=JiraFilters.objects.all(),
                    widget=forms.CheckboxSelectMultiple,
                    to_field_name='name')
        fields = ('user_filter', )


class GlobalSyncFiters(forms.ModelForm):
    class Meta:
        model = JiraExercise
        filter = forms.ModelMultipleChoiceField(
                    queryset=JiraFilters.objects.all(),
                    widget=forms.SelectMultiple(),
                    to_field_name='name'                    
                    )
        fields = ('filter', )
        
    
class UserSyncWeekTime(forms.ModelForm):
    class Meta:
       
        week_choices = (
            (1, 'Понедельник'),
            (2, 'Вторник'),
            (3, 'Среда'),
            (4, 'Четверг'),
            (5, 'Пятница'),
            (6, 'Cуббота'),
            (7, 'Воскресенье')
        )

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


        model = CustomUser
        fields = ('synchronization_custom', 'user_time', 'synchronization_day_of_week', )
        widgets = {
            'synchronization_custom': forms.CheckboxInput(),
            'synchronization_day_of_week': forms.SelectMultiple(choices=week_choices),
            'user_time': forms.Select(choices=time_choices)
        }

class JsonEditor(forms.Form):
    jj = CodeMirrorField(
        label="JSON", 
        required=True,
        config_name="javascript")
    
class YandexCalendarForm(forms.ModelForm):
     class Meta:
        model = CustomUser
        fields = ('synchronization_meetings', 'synchronization_meetings_key')
        widgets = {
            'synchronization_meetings': forms.CheckboxInput(),
            'synchronization_meetings_key': forms.TextInput(attrs={'placeholder': 'Токен доступа', 'type' :'password'}),
        }