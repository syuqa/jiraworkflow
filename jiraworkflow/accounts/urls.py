from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    # post views
    path('', views.home, name='home'),
    # Авторизация
    path('accounts/authentication', views.index, name='authentication'),
    path('accounts/login', views.login, name='login'),
    # path('social/', include('social_django.urls', namespace='social')),
    path('accounts/social/', include('allauth.urls')),
    path('accounts/login/out',views.loginout, name='loginout'),
    # Профиль
    path('profile', views.profile, name='profile'),
    path('profile/custom/filter/enable', views.custom_filters_enable,  name='custom_filters_enable'),
    path('profile/custom/filter/list', views.custom_filters_list, name='custom_filters_list'),
    path('profile/custom/task', views.custom_user_tasks, name='custom_user_tasks'),
    path('users', views.users, name='users'),
    path('users/form/<int:id>', views.userform, name='useredit'),
    path('users/delete', views.userdelete, name='userdelete'),
    path('users/synchronization/<int:id>', views.usersynchronization, name='usersynchronization'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    