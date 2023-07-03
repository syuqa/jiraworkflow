import logging
import datetime

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from .forms import TimettaConnectForm, TimettaProjectsForm, TimettaSimple
from .models import TimettaConnect, TimettaProjects
from .processor import TimettaHTTPRequests

logger = logging.getLogger(__name__)
now = datetime.datetime.now()
# Create your views here.

def timetta(request):
    if request.method == 'POST':
        form = TimettaConnectForm(request.POST)
        if form.is_valid():
            try:
                timetta = TimettaConnect.objects.get(id=1)
                f = TimettaConnectForm(request.POST, instance=timetta)
                f.save()
            except TimettaConnect.DoesNotExist as e:
                form.save()

            return HttpResponse(status=200)
        else:
            return JsonResponse({"msg": form.errors.as_data()}, status=500,content_type="application/json")
    else:

        try:
            timetta = TimettaConnect.objects.get(id=1)
            form = TimettaConnectForm(instance=timetta)
            exist=True
        except TimettaConnect.DoesNotExist as e:
            form = TimettaConnectForm()
            exist=False
        constext = {
            'timettaform': form,
            'projects': TimettaProjects.objects.all(),
            'exist': exist
        }
        
    return render(request, 'timetta/index.html', constext)


def projects(request, id):
    if request.method == 'POST':
        form = TimettaProjectsForm(request.POST)
        if form.is_valid():
            try:
                project = TimettaProjects.objects.get(id=id)
                f = TimettaProjectsForm(request.POST, instance=project)
                f.save()
            except TimettaProjects.DoesNotExist:
                form.save()

            return HttpResponse(status=200)
        else:
            return JsonResponse({"msg": form.errors.as_data()}, status=500,content_type="application/json")
    else:

        try: 
            project = TimettaProjects.objects.get(id=id)
            form = TimettaProjectsForm(instance=project)
        except TimettaProjects.DoesNotExist:
            form = TimettaProjectsForm()

        try:
            wp = TimettaHTTPRequests()
            project_list = wp.projects()
            try:
                project_resurses = wp.get_resource_project(request.user.email, f'{now.year}-01-01', f'{now.year}-12-01')
                print(project_resurses)
            except Exception as e:
                print(e)
                project_resurses = {'value': []}
        except Exception as e:
            print(e)
            project_resurses = {'value': []}
            project_list = {'value': []}

        context = {
            'form': form,
            'id': id,
            'project_resurses': [p.get('projectId') for p in project_resurses.get('value')],
            'project_list': project_list.get('value'),
            'totip_meeting_summary': """
            <h3>Заголовок события в Я.Календаре</h3>
                <p>Поддерживает следующие форматы:</p>
              <ol>
                <li>Заголовоки целеком через точку с запятой - ";"</li>
                <li>Ключивые слова, через запяту</li>
                <li>Кортеж ключевых слов, через ;</li>
              </ol>
            <h3>Примеры</h3>
            <ol>
                <li><i>Встерча по проекту SMPL;Статус по проету SMPL</i></li>
                <li><i>встреча,smpl</i></li>
                <li><i>встреча,smpl;статус,smpl</i></li>
            </ol>
            """
        }

        return render(request, 'timetta/project_form.html', context)
    

def tasks(request, project):
    
    try:
        wp = TimettaHTTPRequests()
        task_list = wp.get_tasks(project=project)
    except:
        task_list = {'value': []}

    context = {
        'tasks': task_list.get('value')
    }
    return render(request, 'timetta/tasks_list.html', context)


def simple(request):
    if request.method == 'POST':
        form = TimettaSimple(request.POST)
        if form.is_valid():
            try:
                account = TimettaConnect.objects.get(id=1)
                f = TimettaSimple(request.POST, instance=account)
                f.save()
            except TimettaConnect.DoesNotExist:
                form.save()

            return HttpResponse(status=200)
        else:
            return JsonResponse({"msg": form.errors.as_data()}, status=500,content_type="application/json")
    else:
        try:
            account = TimettaConnect.objects.get(id=1)
            form = TimettaSimple(instance=account)
        except TimettaConnect.DoesNotExist:
            form = TimettaSimple()
        context = {
            'form': form
        }
        return render(request, 'timetta/simple_form.html', context)