import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-no-29d+tn2wcnp5))8tz(u6kgzfx(jp6705a6rvw3&(ocsc2=#'


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

#For production enable debug to False
# DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = ['*'] 


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'chatbot',
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

ROOT_URLCONF = 'wbot.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # For template rendering
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'wbot.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases


# SQLite was here for testing purposes
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# In production we've to configure MySQL}



# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'

# For css rendering
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]


# During production set it to:
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # For collectstatic
# Dont forget to run : python manage.py collectstatic



# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# settings.py

# META_VERIFY_TOKEN = "6ab1d155-e097-4dde-bf4d-8093efb4d503"
# # This is a permanent Access Token for meta API
# META_ACCESS_TOKEN = "EAAZAFqfHtSVABPOZCvLJqq3aw40M9QFsZBW7zj8T9LpyCLtHHVrCLUbboTpmJoQrhjgDFVrsNFZCsfy042XKiwZBg3ZBgfAYaGoxHleEjbbKkhylTyrjsL1SuZCdjjNf25M8f8iKvVQF1B4NMcpZCNK52gJClu2CPXWrCTyB2BnAuXBcF13ARGiX41axehwl7NMJzgZDZD"
# META_PHONE_NUMBER_ID = "642396845634719"


#From .env config
META_APP_ID = config('META_APP_ID')
META_APP_SECRET = config('META_APP_SECRET')
META_VERIFY_TOKEN = config('META_VERIFY_TOKEN')
META_ACCESS_TOKEN = config('META_ACCESS_TOKEN') #Permanent Token
META_PHONE_NUMBER_ID = config('META_PHONE_NUMBER_ID')

# META_API_URL = config(f'META_API_URL')
