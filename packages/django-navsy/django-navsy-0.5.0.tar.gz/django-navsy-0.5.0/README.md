[![Build Status](https://travis-ci.org/fabiocaccamo/django-navsy.svg?branch=master)](https://travis-ci.org/fabiocaccamo/django-navsy)
[![coverage](https://codecov.io/gh/fabiocaccamo/django-navsy/branch/master/graph/badge.svg)](https://codecov.io/gh/fabiocaccamo/django-navsy)
[![Code Health](https://landscape.io/github/fabiocaccamo/django-navsy/master/landscape.svg?style=flat)](https://landscape.io/github/fabiocaccamo/django-navsy/master)
[![Requirements Status](https://requires.io/github/fabiocaccamo/django-navsy/requirements.svg?branch=master)](https://requires.io/github/fabiocaccamo/django-navsy/requirements/?branch=master)
[![PyPI version](https://badge.fury.io/py/django-navsy.svg)](https://badge.fury.io/py/django-navsy)
[![Py versions](https://img.shields.io/pypi/pyversions/django-navsy.svg)](https://img.shields.io/pypi/pyversions/django-navsy.svg)
[![License](https://img.shields.io/pypi/l/django-navsy.svg)](https://img.shields.io/pypi/l/django-navsy.svg)

# django-navsy
django-navsy is a fast navigation system for lazy devs.

## Requirements
- Python 2.7, 3.4, 3.5, 3.6
- Django 1.8, 1.9, 1.10, 1.11

## Installation
1. Run ``pip install django-navsy`` or download manually [django-navsy](http://pypi.python.org/pypi/django-navsy), [django-autoslug](http://pypi.python.org/pypi/django-autoslug) and [python-slugify](http://pypi.python.org/pypi/python-slugify)
2. Add ``'navsy'`` and ``'autoslug'`` to ``settings.INSTALLED_APPS``
3. Add ``'navsy.urls'`` to ``urls.py``
4. Add ``'navsy.context_processors.data'`` to ``'context_processors'`` in ``settings.TEMPLATES``
4. Run ``python manage.py migrate navsy``
5. Run ``python manage.py collectstatic``
6. Restart your application server
7. Open the admin and enjoy :)

## URLs

#### single-language application
```python
from django.conf.urls import include, url

urlpatterns += [url(r'^', include('navsy.urls'))]
```
#### multi-language application
```python
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns

urlpatterns += [url(r'^i18n/', include('django.conf.urls.i18n'))]
urlpatterns += i18n_patterns(url(r'^', include('navsy.urls')))
```

## License
Released under [MIT License](LICENSE).
