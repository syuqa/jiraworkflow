from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    # post views
    path('', views.jira, name='jira'),
    path('sync', views.sync, name='sync'),
    path('filter/<int:id>', views.filter, name='filter'),
    path('exercise', views.exercise, name='exercise'),
    path('exercise/enable', views.exercis_enable, name='exercise_enable'),
    path('worklog/<str:task>', views.worklog, name='worklog'),
    path('worklog/trace/<str:task>', views.worktrace, name='worklog')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
