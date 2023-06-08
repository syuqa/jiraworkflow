import logging
import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as _login
from django.contrib.auth.decorators import login_required, user_passes_test
from django_celery_results.models import TaskResult

# TaskResult
from accounts.models import CustomUser
from Jira.models import JiraExercise
from Jira.forms import JiraExerciseForm
from .forms import *

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'accounts/index.html')


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

def loginout(request):
    logout(request)
    return redirect('login')



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
        'TaskResult': TaskResult.objects.filter(task_name='Jira: Выгрузка задач')
    }
    return render(request, 'jirausers/profile.html', context)

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
        logger.debug(users)
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

    