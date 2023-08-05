
# CosmicDB Django App

## Install

### Initial setup
```
virtualenv demoenv --no-site-packages
demoenv\Scripts\activate
pip install cosmicdb
django-admin startproject demo
```

### Usage

#### Add cosmicdb and requirements to your INSTALLED_APPS setting like this (your app must be first to override)
```
INSTALLED_APPS = (
    'YOURAPPHERE',
    'cosmicdb',
    'dal',
    'dal_select2',
    'crispy_forms',
    'django_tables2',
    ... (rest of django apps)
)
```

#### Add cosmicdb.urls to your urls.py like this (put cosmicdb urls last)
```
    from django.conf.urls import url, include

    urlpatterns = [
        ...
        url(r'^', include('cosmicdb.urls')),
    ]
```

#### Add cosmicdb settings to your settings.py like this::
```
LANGUAGE_CODE = 'en-au'
COSMICDB_SITE_TITLE = 'Demo Site'
COSMICDB_ALLOW_SIGNUP = True
AUTH_USER_MODEL = 'cosmicdb.CosmicUser'
LOGIN_URL = '/login/'
CRISPY_TEMPLATE_PACK = 'bootstrap3'
DJANGO_TABLES2_TEMPLATE = 'django_tables2/bootstrap-responsive.html'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'test@test.com'
EMAIL_HOST_PASSWORD = 'testpassword'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL_NAME = COSMICDB_SITE_TITLE
```

#### Run
```
python manage.py migrate

python manage.py collectstatic

python manage.py createsuperuser
```


## Dev Notes

### install required packages for packaging
```
pip install setuptools twine wheel
```

### adjust cosmicdb/__init__.py for version number
```
python setup.py sdist bdist_wheel
```
### replace the following line with version number
### twine upload dist/cosmicdb-VERSION_NUMBER*
```
twine upload dist/cosmicdb-0.0.1*
```
