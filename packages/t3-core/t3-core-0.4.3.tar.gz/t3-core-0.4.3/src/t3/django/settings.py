import os
import importlib
from t3.env import load_env
from t3.django.util import get_base_dir


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = get_base_dir()


# Get env dictionary.  This feeds from env, .env, and then vcap services
# For local dev, move .env.example to .env and play with settings
# In CI, a service.yaml is likely to be used
_env = load_env(dot_env_path=BASE_DIR)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if str(os.getenv('DJANGO_DEBUG', 'false')).lower() == 'true' else False

# Store this as a comma delimited list (eg. localhost,127.0.0.1)
ALLOWED_HOSTS = os.environ['DJANGO_ALLOWED_HOSTS'].split(',')


# Create of merge INSTALLED_APPS
# INSTALLED_APPS = globals().get('INSTALLED_APPS', [])
CORE_INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd Party Packages
    'django_prometheus',
    'storages',
    'django_extensions'
]


# Django Middleware
MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',

    # 3rd Party Middleware
    'log_request_id.middleware.RequestIDMiddleware',
]

# Django Templates
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
            ],
        },
    },
]


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('DB_NAME', os.path.join(BASE_DIR, 'db.sqlite3')),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': int(os.environ.get('DB_PORT')) if os.environ.get('DB_PORT') else None,
        'TEST': {
            'ENGINE': os.environ.get('DB_TEST_ENGINE', 'django.db.backends.sqlite3'),
            'NAME': os.environ.get('DB_TEST_NAME', os.path.join(BASE_DIR, 'db.sqlite3')),
            'USER': os.environ.get('DB_TEST_USER'),
            'PASSWORD': os.environ.get('DB_TEST_PASSWORD'),
            'HOST': os.environ.get('DB_TEST_HOST'),
            'PORT': int(os.environ.get('DB_TEST_PORT')) if os.environ.get('DB_TEST_PORT') else None,
        }
    },
}

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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# ############################################################################
# T3 Specific Configs
# ############################################################################
try:
    PROJECT_PACKAGE = os.environ['DJANGO_SETTINGS_MODULE'].split('.')[0]
except KeyError:
    PROJECT_PACKAGE = None

LOGGING_LEVEL = os.getenv('DJANGO_LOGGING_LEVEL', 'INFO')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'request_id': {
            '()': 'log_request_id.filters.RequestIDFilter'
        }
    },
    'formatters': {
        'simple': {
            'format': u'%(asctime)s [%(levelname)-8s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': u'%(asctime)s [%(levelname)-8s] %(message)s',
        },
        'json': {
            '()': 't3.django.log.DjangoJsonFormatter',
        },
        'json_pretty': {
            '()': 't3.django.log.DjangoJsonPrettyFormatter',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json_pretty',
            'stream': 'ext://sys.stdout',
            'filters': ['request_id'],
        },
    },
    'loggers': {
        't3': {
            'level': LOGGING_LEVEL,
            'handlers': ['console'],
            'propagate': False,
        },
        'django': {
            'level': LOGGING_LEVEL,
            'handlers': ['console'],
            'propagate': False,
        },
    },
}

if PROJECT_PACKAGE:
    LOGGING['loggers'][PROJECT_PACKAGE] = LOGGING['loggers']['t3']

# Log header stuff
# https://github.com/dabapps/django-log-request-id
LOG_REQUEST_ID_HEADER = "HTTP_X_REQUEST_ID"
GENERATE_REQUEST_ID_IF_NOT_IN_HEADER = True
REQUEST_ID_RESPONSE_HEADER = "RESPONSE_HEADER_NAME"
REQUEST_ID_RESPONSE_HEADER = "X-Response-Id"


# URL Prefix Stuff
URL_PREFIX = os.getenv('URL_PREFIX', '')
if URL_PREFIX != '':
    # Make sure URL_PREFIX ends with a '/'
    if not URL_PREFIX.endswith('/'):
        URL_PREFIX = URL_PREFIX + '/'
    # Make sure URL_PREFIX doesn't start with '/'
    if URL_PREFIX.startswith('/'):
        URL_PREFIX = URL_PREFIX[1:]


# ############################################################################
# AWS Configs
# ############################################################################
AWS_STORAGE = False if str(os.getenv('AWS_STORAGE', 'true')).lower() == 'false' else True
AWS_LOGGING = False if str(os.getenv('AWS_LOGGING', 'true')).lower() == 'false' else True

# Shared AWS Configs
if AWS_STORAGE or AWS_LOGGING:
    AWS_SERVICE_NAME = os.environ['AWS_SERVICE_NAME']
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    AWS_REGION_NAME = os.environ['AWS_REGION_NAME']

# AWS S3 Storage
if AWS_STORAGE:
    AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
    AWS_AUTO_CREATE_BUCKET = True
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', AWS_REGION_NAME)

    AWS_S3_OBJECT_PARAMETERS = {
        'Expires': 'Thu, 31 Dec 2099 20:00:00 GMT',
        'CacheControl': 'max-age=94608000',
    }

    # Default media bucket
    DEFAULT_FILE_STORAGE = 't3.django.storages.MediaStorage'
    MEDIAFILES_BUCKET = os.getenv('AWS_MEDIAFILES_BUCKET', AWS_STORAGE_BUCKET_NAME)
    MEDIAFILES_LOCATION = os.getenv('AWS_MEDIAFILES_LOCATION', AWS_SERVICE_NAME + '/' + 'media')

    # Default static bucket
    STATICFILES_STORAGE = 't3.django.storages.StaticStorage'
    STATICFILES_BUCKET = os.getenv('AWS_STATICFILES_BUCKET', AWS_STORAGE_BUCKET_NAME)
    STATICFILES_LOCATION = os.getenv('AWS_STATICFILES_LOCATION', AWS_SERVICE_NAME + '/' + 'static')
else:
    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/2.0/howto/static-files/
    STATIC_URL = os.getenv('STATIC_URL', '/{}static/'.format(URL_PREFIX))


# AWS CloudWatch Logging
if AWS_LOGGING:
    Session = importlib.import_module('boto3.session').Session

    # Add handler for CloudWatch (watchtower)
    AWS_DEFAULT_REGION = AWS_REGION_NAME
    LOGGING['handlers']['watchtower'] = {
        'formatter': 'json',
        'class': 'watchtower.django.DjangoCloudWatchLogHandler',
        'log_group': 'django',
        'stream_name': AWS_SERVICE_NAME,
        'filters': ['request_id'],
    }

    # Log using watchtower handler
    LOGGING['loggers']['t3']['handlers'] = ['console', 'watchtower']
    LOGGING['loggers']['django']['handlers'] = ['console', 'watchtower']

    if PROJECT_PACKAGE:
        LOGGING['loggers'][PROJECT_PACKAGE] = LOGGING['loggers']['t3']

# Django Extensions
SHELL_PLUS = "ipython"
IPYTHON_KERNEL_DISPLAY_NAME = "Django Shell-Plus"
