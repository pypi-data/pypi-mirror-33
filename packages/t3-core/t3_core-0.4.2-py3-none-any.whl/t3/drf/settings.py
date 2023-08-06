"""Base settings for a Django Rest Framework Project."""
import os
from t3.env import load_env
from t3.django.util import get_base_dir


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = get_base_dir()


# Get env dictionary.  This feeds from env, .env, and then vcap services
# For local dev, move .env.example to .env and play with settings
# In CI, a service.yaml is likely to be used
_env = load_env(dot_env_path=BASE_DIR)


# Create of merge INSTALLED_APPS
# print(globals().get('INSTALLED_APPS', []))
# INSTALLED_APPS = globals().get('INSTALLED_APPS', [])
# print(globals().get('INSTALLED_APPS', []))
DRF_INSTALLED_APPS = [
    'django_filters',
    'crispy_forms',
    'rest_framework',

    'drf_yasg',
]


# Rest Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'EXCEPTION_HANDLER': 't3.drf.views.enveloped_exception_handler',
    'PAGE_SIZE': 25,
}

DOCS_TITLE = os.getenv('DOCS_TITLE', 'T3 API')
DOCS_VERSION = os.getenv('DOCS_VERSION', 'v1')
