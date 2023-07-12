import logging
import json
from datetime import datetime

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as _login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import update_session_auth_hash

from django_celery_results.models import TaskResult

# TaskResult
from accounts.models import CustomUser
from Jira.models import JiraExercise
from Jira.forms import JiraExerciseForm, NotificationForm
from Jira.processor import JiraTasks
from timetta.tasks import custom_sync as task_custom_sync
from django.core.mail import send_mail
from .forms import *
from django.conf import settings

# send_mail(subject="Tess", message="Hello", recipient_list=['k-5.45mm@yandex.ru'])
# send_mail(subject="Tess", message="Hello", recipient_list=['k-5.45mm@yandex.ru'], from_email=settings.DEFAULT_FROM_EMAIL)

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'accounts/index.html')


def remove_current_user(request):
    try:
        request.user.delete()
        return HttpResponse(status=200)
    except Exception as e:
        return JsonResponse({"msg": str(e)}, status=500, content_type="application/json")

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    _login(request, user)
                    return redirect('home')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form} )

@login_required
def loginout(request):
    logout(request)
    return redirect('login')

@login_required
def repassword(request):
    if request.method == 'POST':
        form = SetPasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return HttpResponse(status=200)
        else:
            return JsonResponse({"msg": json.loads(form.errors.as_json())}, status=500, content_type="application/json")

@login_required      
def notification(request):
    if request.method == 'POST':
        form = NotificationForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return HttpResponse(status=200)
        else:
            return JsonResponse({"msg": json.loads(form.errors.as_json())}, status=500, content_type="application/json")

@login_required
def settings(request):
    if request.method == 'POST':
        form = AccountSettingLogin(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return HttpResponse(status=200)
        else:
            return JsonResponse({"msg": str(form.errors.as_json())}, status=500, content_type="application/json") 
    context = {
        "loginForm": AccountSettingLogin(instance=request.user),
        "passForm": SetPasswordForm(request.user),
        "notificationForm": NotificationForm(instance=request.user)
    }
    return render(request, 'accounts/setting.html', context)


@login_required
def home(request):
    return render(request, 'jirausers/index.html', {'form': JsonEditor()})

@login_required
def profile(request):
    #
    try:
        f = GlobalSyncFiters(instance=JiraExercise.objects.get(name='jira_all_sync_once_a_week'))
    except JiraExercise.DoesNotExist:
        f = GlobalSyncFiters()
    #
    try:
        g = JiraExerciseForm(instance=JiraExercise.objects.get(name='jira_all_sync_once_a_week'))
    except JiraExercise.DoesNotExist:
        g  = JiraExerciseForm()

    context = {
        'sync': UserSynchronizationForm(instance=request.user),
        'jira': {
            'filters': {
                'global': f,
                'custom': {
                    'enable' : UserSyncCustomFilter(instance=request.user),
                    'list': UserSyncFiters(instance=request.user)
                } 
            },
            'syncweektime':{
                'custom': UserSyncWeekTime(instance=request.user),
                'global': g
            }
        },
        'meetings': YandexCalendarForm(instance=request.user),
        'TaskResult': TaskResult.objects.filter(task_name__in=('Jira: Выгрузка задач', 'Выборочная синхронизация'))[:5]
    }
    return render(request, 'jirausers/profile.html', context)

@login_required
def yandex_calendar(request):
    if request.method == 'POST':
        try:
            form = YandexCalendarForm(request.POST, instance=request.user)
            form.save()
            return HttpResponse(status=200)
        except Exception as e:
            return JsonResponse({"msg": str(e)}, status=500, content_type="application/json") 


@user_passes_test(lambda u: u.is_superuser)
def users(request):
    if request.method == 'POST':
        pass

    else:
        context = {
            'users': CustomUser.objects.all()
        }
        return render(request, 'jirausers/userlist.html', context)

@login_required
def custom_filters_enable(request):
    if request.method == 'POST':
       form =  UserSyncCustomFilter(request.POST)
       if form.is_valid():
           f = UserSyncCustomFilter(request.POST, instance=CustomUser.objects.get(id=request.user.id))
           r = f.save()
           print(r.synchronization, form.data.keys())
           return HttpResponse(status=200)
       else:
           return JsonResponse({"msg": str(form.errors.as_data())}, status=500, content_type="application/json") 

@login_required
def custom_filters_list(request):
    if request.method == 'POST':
       form =  UserSyncFiters(request.POST)
       if form.is_valid():
           f = UserSyncFiters(request.POST, instance=request.user)
           f.save()
           return HttpResponse(status=200)
       else:
           return JsonResponse({"msg": str(form.errors.as_data())}, status=500, content_type="application/json") 

@login_required
def custom_user_tasks(request):
    if request.method == 'POST':
       form =  UserSyncWeekTime(request.POST)
       if form.is_valid():
           f = UserSyncWeekTime(request.POST, instance=request.user)
           f.save()
           return HttpResponse(status=200)
       else:
           return JsonResponse({"msg": str(form.errors.as_data())}, status=500, content_type="application/json") 

@login_required
def userform(request, id=0):
    if request.method == 'POST':
        form = UserAccountForm(request.POST)
        try:
            user = CustomUser.objects.get(id=id)
            print(user)
            f = UserAccountForm(request.POST, instance=user)
            f.save()
            return HttpResponse(status=200)
        except CustomUser.DoesNotExist as e:
            print(e)
            form.save()
            return HttpResponse(status=200)
        except BaseException as e:
            return JsonResponse({"msg": str(form.errors.as_data())}, status=500, content_type="application/json") 
    else:
        try:
            user = CustomUser.objects.get(id=id)
            form = UserAccountForm(instance=user)
        except CustomUser.DoesNotExist as e:
            form = UserAccountForm()
            
        context = {
            'id': id,
            'form': form,
        }
        return render(request, 'jirausers/userform.html', context)
    

@login_required
def userdelete(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode())
        if data.get('users'):
            for user in data.get('users'):
                try:
                    CustomUser.objects.get(id=user).delete()
                except CustomUser.DoesNotExist as e:
                    return JsonResponse({"msg":e}, status=400,content_type="application/json")
            return JsonResponse({"msg":"ok"}, status=200,content_type="application/json")


@login_required
def usersynchronization(request, id):
    if request.method == 'POST':
        form = UserSynchronizationForm(request.POST)
        if form.is_valid():
            try:
                user = CustomUser.objects.get(id=id)
                f = UserSynchronizationForm(request.POST, instance=user)
                f.save()
            except CustomUser.DoesNotExist as e:
                return JsonResponse({"msg": e}, status=500,content_type="application/json")
            return HttpResponse(status=200)
        else:
            return JsonResponse({"msg": form.errors.as_data()}, status=500,content_type="application/json")

    
@login_required
def custom(request):
    if request.method == 'GET':
        context = {
            "filters": JiraFilters.objects.all() #GlobalSyncFiters()
        }
        return render(request, 'jirausers/custom-sync.html', context)
    
@login_required
def custom_tasks(request):
    if request.method == 'GET':
        filters = request.GET.get('filters')
        sdate = request.GET.get('sdate')
        edate = request.GET.get('edate')
        mitings = request.GET.get('mitings')
        # print(filters, sdate, edate, mitings)
        jira = JiraTasks()
        tasks= jira.get_tasks([request.user], sdate=sdate, edate=edate, filters=filters.split(','))
        # print('TASKS', tasks)
        context = {
            "tasks": tasks if tasks == {} else tasks[request.user.email]
        }
        # print('TYPE', type(context.get('tasks')), 'TASKS', context.get('tasks'))
        return render(request, 'jirausers/custom-sunc-list.html', context)

@login_required
def custom_sync(request):
    if request.method == 'POST':
        try:
            tasklist = json.loads(request.body.decode())
            sdate = datetime.strptime(tasklist.get('dates')[0], '%Y-%m-%dT%H:%M:%S.%f%z')
            edate = datetime.strptime(tasklist.get('dates')[1], '%Y-%m-%dT%H:%M:%S.%f%z')
            print('SYNCDATES', sdate, edate)
            task_custom_sync.apply_async(
                kwargs={"issues": {request.user.email: tasklist.get('task')}, "username" : request.user.username, "mitings": tasklist.get('miting'), "method": tasklist.get('metrhod'), "dates": [sdate, edate]})
            return JsonResponse({"msg": "Задание запущено"}, status=200,content_type="application/json")
        except Exception as e:
            print(e)
            return JsonResponse({"msg": str(e)}, status=500,content_type="application/json")
        