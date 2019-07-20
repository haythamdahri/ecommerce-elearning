"""
Django settings for WebPlatform project.

Generated by 'django-admin startproject' using Django 2.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from django.conf.urls import url

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '#ha!=(ccfx!b7xm3i%pp6ti4j_gz=fy6)@b1h0-a&hlh-088=q'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['haythamdahri.pythonanywhere.com', '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'paypal.standard.ipn',
    'Ecommerce',
    'widget_tweaks',
    'PIL',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ckeditor',
    'ckeditor_uploader',
    'responsive_images',
    'django.contrib.humanize'
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

ROOT_URLCONF = 'WebPlatform.urls'

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
                'Ecommerce.context_processors.global_vars',
            ],
        },
    },
]

WSGI_APPLICATION = 'WebPlatform.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
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

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

CKEDITOR_UPLOAD_PATH = "uploads/"

CKEDITOR_FILENAME_GENERATOR = 'utils.get_filename'

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': None,
        "width": '100%',
    },
}

LANGUAGES = [
#    ('de', _('German')),
   ('en', ('English')),
   ('fr', ('French')),
#    ('es', _('Spanish')),
#    ('pt', _('Portuguese'))
]


MARKDOWNX_EDITOR_RESIZABLE = True

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'haytham.dahri@gmail.com'
EMAIL_HOST_PASSWORD = 'Haytham2020'
EMAIL_USE_TLS = True

LOGIN_URL = "/ecommerce/account"
#-----------------Authentication backend -----------------
AUTHENTICATION_BACKENDS = ['Ecommerce.backends.EmailBackend']


#----------- PAYPAL CONFIGURATION -----------
PAYPAL_TEST = True
PAYPAL_RECEIVER_EMAIL = "Haythaminfo99@gmail.com"

#----------- PAYPAL MIN AND MAX AMOUNT -----------
MAX_AMOUNT = 10000
MIN_AMOUNT = 100
