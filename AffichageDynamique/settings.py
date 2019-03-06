"""
Django settings for AffichageDynamique project.

Generated by 'django-admin startproject' using Django 2.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import dj_database_url
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'o1(en$lqa0@k*#we79=ooqpuk#%wzqgj2qk!^t43pxdu(=^w_8')


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_ENV', 'dev') == 'dev'

ALLOWED_HOSTS = [os.getenv('ALLOWED_HOSTS', "affichage.bde-insa-lyon.fr")]
if DEBUG:
    ALLOWED_HOSTS.extend(['127.0.0.1'])
    ALLOWED_HOSTS.extend(['localhost'])


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',
    'crispy_forms',
    'anymail',
    'bootstrap_datepicker_plus',
    'django_registration',
    'django_crontab'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'AffichageDynamique.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'AffichageDynamique.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(default='sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3'), conn_max_age=600)
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'fr-fr'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_L10N = True

USE_TZ = True
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

CRONJOBS = [
    ('0 3 */5 * *', 'app.cron.delete_old_content'),
    ('0 5 */5 * *', 'app.cron.delete_image_orphan')
]

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

MEDIA_ROOT  = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
LOGOUT_REDIRECT_URL = "/"
ACCOUNT_ACTIVATION_DAYS = 7

ANYMAIL = {
    # (exact settings here depend on your ESP...)
    "MAILGUN_API_KEY": os.getenv('MAILGUN_KEY',""),
    "MAILGUN_SENDER_DOMAIN": os.getenv('MAILGUN_DOMAIN', 'mg.bde-insa-lyon.fr'),  # your Mailgun domain, if needed
}

DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL',"affichage@mg.bde-insa-lyon.fr")
DEFAULT_GROUP_PK = os.getenv('DEFAULT_GROUP_PK', 0)
