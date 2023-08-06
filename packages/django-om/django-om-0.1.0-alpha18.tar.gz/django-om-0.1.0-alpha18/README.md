# Om.next query parser for Django

## Installation

```bash
sudo pip install django-om
```

## Usage

Add "django-om" to `INSTALLED_APPS`:

```python
INSTALLED_APPS += ('django-om',)
```

and then include the parser endpoint in your urls.py:

```python
url(r'^api/, include('django_om.urls')),
```

You then need to define `DJANGO_OM` in settings.py with a 'PARSER' key.
It should be the full path to a module within your own codebase:

```python
DJANGO_OM = {
  'PARSER': 'myapp.api.parser'
}
```

Inside this module you define an object, which tells the parser what to do
when it encounters certain reads or mutations (keywords or symbols):

```python
from myapp.utils import do_login

def report(request, params=None):
    return {'uniques': 100, 'active': 2}

def login(request, params):
    do_login(params['username'], params['password'])

PARSER = {
    'READS': {
        'reports': report,
    },
    'MUTATIONS': {
        'user/login': charge_login
    }
}

```

## Authorization

If a model requires authorization, you should define an `authorize_for(user)` method on the model's queryset.

## Additional settings

These are the default values:

```python
DJANGO_OM = {
  ...
  'PAGE_SIZE': 20,
  'TRANSIT_ENCODING': 'json'
}
```
