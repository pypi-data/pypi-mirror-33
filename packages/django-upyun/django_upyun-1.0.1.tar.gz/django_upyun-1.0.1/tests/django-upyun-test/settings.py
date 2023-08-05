import os
import sys
import uuid

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(BASE_DIR))

SECRET_KEY = "test"

USE_TZ = True
TIME_ZONE = 'UTC'

# upyun settings
UPY_SERVICE = "test-django-11111"
UPY_USERNAME = "django"
UPY_PASSWORD = "1596321abc"
UPY_SERVICE_URL = "http://test.lanmang.me"
UPY_NEED_COVERAGE = False  # or False
UPY_SAVE_FULL_URL = False  # or False

MEDIA_PREFIX = 'media/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
ADMIN_MEDIA_PREFIX = '/static/admin'

STATIC_PREFIX = 'static/'
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

DEFAULT_FILE_STORAGE = 'django_upyun.backends.UpYunMediaStorage'
STATICFILES_STORAGE = 'django_upyun.backends.UpYunStaticStorage'

# Application definition

INSTALLED_APPS = (
    "django.contrib.staticfiles",
    "django_upyun",
)


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}
