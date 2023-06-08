from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    # post views
    path('', views.timetta, name='timetta'),
    path('projects/<int:id>', views.projects, name='projects'),
    path('tasks/<str:project>', views.tasks, name='tasks'),
    path('simple/', views.simple, name='simple')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    