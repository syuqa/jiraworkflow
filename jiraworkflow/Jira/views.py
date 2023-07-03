import logging
import json

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse
from .tasks import jira_sync
from .forms import JiraConnectForm, JiraFiltersForm, JiraExerciseForm, JiraSyncTraceback, JsonEditorForm, JiraExerciseEnableForm
from .models import JitaConnect, JiraFilters, JiraExercise
from django_celery_results.models import TaskResult
from accounts.forms import JsonEditor

logger = logging.getLogger(__name__)

# Create your views here.
@login_required
def jira(request):
    if request.method == 'POST':
        form = JiraConnectForm(request.POST)
        if form.is_valid():
            try:
                jira = JitaConnect.objects.get(id=1)
                f = JiraConnectForm(request.POST, instance=jira)
                f.save()
            except JitaConnect.DoesNotExist as e:
                form.save()

            return HttpResponse(status=200)
        else:
           return JsonResponse({"msg": form.errors.as_data()}, status=500,content_type="application/json")
    
    else:
        try:
            form = JiraConnectForm(instance=JitaConnect.objects.get(id=1))
        except JitaConnect.DoesNotExist as e:
            form = JiraConnectForm()

        try: 
            jiraexercise = JiraExerciseForm(instance=JiraExercise.objects.get(name='jira_all_sync_once_a_week'))
            jiraexercise_enable = JiraExerciseEnableForm(instance=JiraExercise.objects.get(name='jira_all_sync_once_a_week'))
            jiraexercise_exixt = True
        except JiraExercise.DoesNotExist as e:
            jiraexercise = JiraExerciseForm()
            jiraexercise_enable = JiraExerciseEnableForm()
            jiraexercise_exixt = False

        constext = {
            'jiraform': form,
            'jiraexercise_enable': jiraexercise_enable,
            'jiraexercise_exist': jiraexercise_exixt,
            'jiraexercise': jiraexercise,
            'jirafilter': JiraFilters.objects.all(),
            'TaskResult': TaskResult.objects.filter(task_name__in=('Jira: Выгрузка задач', 'Выборочная синхронизация'))[:5]
            
        }
        print(constext)
    return render(request, 'jira/index.html', constext)

@login_required
def filter(request, id):
    if request.method == 'POST':
        form = JiraFiltersForm(request.POST)
        try:
            if id == 0:
                form.save()
            else:
                try:
                    filtr = JiraFilters.objects.get(id=int(id))
                    f = JiraFiltersForm(request.POST, instance=filtr)
                    f.save()
                except JiraFilters.DoesNotExist as e:
                    return JsonResponse({"msg": e}, status=500,content_type="application/json")

            return HttpResponse(status=200)
        except BaseException as e:
            return JsonResponse({"msg": e}, status=500,content_type="application/json")
        
    else:
        try:
            form = JiraFiltersForm(instance=JiraFilters.objects.get(id=id))
        except JiraFilters.DoesNotExist as e:
            form = JiraFiltersForm()
        constext = {
            'form': form,
            'id': id
        }
        return render(request, 'jira/dialog_jirafilter.html', constext)
    
@login_required 
def exercise(request):
    if request.method == 'POST':
        form = JiraExerciseForm(request.POST)
        if form.is_valid():
            try:
                form = JiraExercise.objects.get(name = 'jira_all_sync_once_a_week')
                f = JiraExerciseForm(request.POST, instance=form)
                f.save()
            except JiraExercise.DoesNotExist as e:
                form = JiraExerciseForm(request.POST, instance=JiraExercise.objects.create(name='jira_all_sync_once_a_week'))
                form.save()
                logger.error(e)

            return HttpResponse(status=200)
        else:
            return JsonResponse({"msg": form.errors.as_data()}, status=500,content_type="application/json")
        
@login_required 
def exercis_enable(request):
    if request.method == 'POST':
        form = JiraExerciseEnableForm(request.POST)
        if form.is_valid():
            try:
                form = JiraExercise.objects.get(name = 'jira_all_sync_once_a_week')
                f = JiraExerciseEnableForm(request.POST, instance=form)
                f.save()
            except JiraExercise.DoesNotExist as e:
                form = JiraExerciseEnableForm(request.POST, instance=JiraExercise.objects.create(name='jira_all_sync_once_a_week'))
                form.save()
                logger.error(e)

            return HttpResponse(status=200)
        else:
            return JsonResponse({"msg": form.errors.as_data()}, status=500,content_type="application/json")

@login_required
def worklog(request, task):
    users = []
    try:
        u = TaskResult.objects.get(task_id=task).result
        if request.user.is_superuser:
            users = json.loads(u)
        else: 
            for usename, data in json.loads(u).items():
                print('USER', usename, request.user.email)
                if usename == request.user.email:
                    users = {usename: data}
    except TaskResult.DoesNotExist as e:
        print(task, 'not exsist', e)
    context = {
        'task': task,
        'users': [*users.keys()],
        'weeks': { user: [*week.keys()] for user, week in users.items()},
        'data': users,
        'jsoneditor': JsonEditorForm()
    }
    print(context)
    return render(request, 'jira/wokrlog.html', context)


@login_required
def worktrace(request, task):
    try:
        t = TaskResult.objects.get(task_id=task)
        form = JiraSyncTraceback(instance=t)
    except TaskResult.DoesNotExist:
        form = JiraSyncTraceback()
    constext = {
        'form': form
    }
    return render(request, 'jira/wokrtrace.html', constext)


@user_passes_test(lambda u: u.is_superuser)
def sync(request):
    jira_sync.apply_async(kwargs={"username": request.user.username})
    return HttpResponse(status=200)