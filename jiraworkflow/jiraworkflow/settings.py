"""
Django settings for jiraworkflow project.

Generated by 'django-admin startproject' using Django 2.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
from djangocodemirror.settings import *
from djangocodemirror.helper import codemirror_settings_update

# CODEMIRROR_MODES = codemirror_settings_update(CODEMIRROR_MODES, {'json': })

CODEMIRROR_THEMES = {
    'mdn-like': 'CodeMirror/theme/mdn-like.css'
}

CODEMIRROR_SETTINGS = codemirror_settings_update(CODEMIRROR_SETTINGS, {
    'lineNumber': False,
    'indent': 4,
    'json': True,
    'theme': 'mdn-like'
}, on=['css', 'python', 'javascript',], names=['css', 'python', 'javascript'])


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
FILE_CHARSET = 'UTF-8'

ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['http://*', 'https://*', 'http://192.168.1.36', ]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO','https')
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.yandex',
    # 'social_django',
    # 'rest_framework',
    # 'rest_framework.authtoken',
    # 'social.apps.django_app.default',
    'accounts',
    'Jira',
    'timetta',
    'crispy_forms',
    'django_json_widget',
    'codemirror2',
    'djangocodemirror',
    # 'ws4redis',
    'django_celery_results',
    'django_celery_beat',
    'multiselectfield',
    'django_logging',
]

MIDDLEWARE = [
    'django_logging.middleware.DjangoLoggingMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',

]

ROOT_URLCONF = 'jiraworkflow.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # 'ws4redis.context_processors.default',
                # 'social.apps.django_app.context_processors.backends',
                # 'social.apps.django_app.context_processors.login_redirect'
                # 'social_django.context_processors.backends',
                # 'social_django.context_processors.login_redirect',

            ],
            'libraries':{
                'customFilter': 'Jira.templatetags.custom_tags',
            }
        },
    },
]

WSGI_APPLICATION = 'jiraworkflow.wsgi.application'
# Авторизация

AUTH_USER_MODEL = 'accounts.CustomUser'
AUTHENTICATION_BACKENDS = (
    #'social_core.backends.yandex.YandexOAuth2',
    # 'account.backends.AuthBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend'
    )

# SOCIAL_AUTH_YANDEX_OAUTH2_AUTH_EXTRA_ARGUMENTS = {
#    'client_id': '72d60797b43a4ecc9c9899f3dc92575e',
#    'client_secret': 'd443f0b9286a4d599f0bfdd97b65163a',
#    'redirect_url': 'http://192.168.1.36/account/social/'
# }
# SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
# SOCIAL_AUTH_LOGIN_ERROR_URL = '/'
# SOCIAL_AUTH_RAISE_EXCEPTIONS = False
# SOCIAL_AUTH_USER_MODEL = AUTH_USER_MODEL
"""
SOCIALACCOUNT_PROVIDERS = {
    'yandex': {
        # For each OAuth based provider, either add a ``SocialApp``
        # (``socialaccount`` app) containing the required client
        # credentials, or list them here:
        'APP': {
            'client_id': '72d60797b43a4ecc9c9899f3dc92575e',
            'client_secret': '79e9b08a4b1d4f09940cfb92fb679e81',
            'key': '',
            'lang':'ru'
        },
        "SCOPE": [
        ]
    }
}
"""
LOGIN_URL = 'authentication'
LOGIN_REDIRECT_URL = 'home'
# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
"""
DATABASES = {
   'default': {
      'ENGINE': 'django.db.backends.sqlite3',
      'NAME': os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'database', 'db.sqlite3'),
   }
}
"""

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'database1',
        'USER': 'database1_role',
        'PASSWORD': 'database1_password',
        'HOST': 'database1',
        'PORT': '5432',
        'OPTIONS': {
            'client_encoding': 'UTF-8',
        },
    }
}

# CELERY RADIS
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = 'Europe/Moscow'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_RESULT_EXTENDED = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
    }
}

CELERY_CACHE_BACKEND = 'default'

# WEBSOCKET
# WEBSOCKET_URL = '/ws/'
# WS4REDIS_CONNECTION = {
#    'host': 'localhost',
#    'port': 6379,
#    'db': 3,
#    'password': os.environ.get("REDIS_PASSWORD"),
#}

#WS4REDIS_PREFIX = 'ws'


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'RU-ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'static')
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'), )
MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'media')

"""
REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',

    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAdminUser',
        'rest_framework.permissions.IsAuthenticated',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ]
}
"""

DJANGO_LOGGING = {
    "CONSOLE_LOG": True,
    "IGNORED_PATHS" : ['/admin', '/static', '/favicon.ico'],
}

"""
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    "filters": {
        "add_gae_log_level": {
            "()": "jiraworkflow.logging.AddGaeSeverityLevel"}
            },
    'formatters': {
        'console': {
            'format': '%(name)-12s %(levelname)-8s %(message)s'
        },
        'file': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        },
        "json": {"()": "pythonjsonlogger.jsonlogger.JsonFormatter"}
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            "formatter": "json",
            "filters": ["add_gae_log_level"],
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            "formatter": "json",
            "filters": ["add_gae_log_level"],
            'filename': 'debug.log'
        }
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['console', 'file']
        }
    }
}   

"""

# Отправка писем
EMAIL_USE_TLS = True if os.environ.get('EMAIL_USE_TLS') == 'True' else False
EMAIL_USE_SSL = True if os.environ.get('EMAIL_USE_SSL') == 'True' else False
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT'))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')

SITE_ID = 1
