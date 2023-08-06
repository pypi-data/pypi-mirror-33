import os

DEBUG = True

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        #'NAME': os.path.join(BASE_DIR, 'db_django.sqlite3'),
    }
}

INSTALLED_APPS = ('orm_only',)

SECRET_KEY = 'SECRET_KEY'