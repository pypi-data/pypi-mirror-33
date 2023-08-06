from datetime import timedelta

SECRET_KEY = '2^mza*qpug3+htv7jxecatc0w&rluw!b#2cf9r*+&3fj8a2i66'
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'authentication',
    'tests',
    'generic',
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'django-generic-rest.db',
    }
}
AUTH_USER_MODEL = 'authentication.User'
USE_TZ = True
ERROR_KEY = 'Error'
ROOT_URLCONF = 'tests.urls'

# Generic Token Authentication
TOKEN_LENGTH = 64
TOKEN_EXPIRY = timedelta(hours=1)
REFRESH_TOKEN_LENGTH = 128
REFRESH_TOKEN_EXPIRY = timedelta(days=1)