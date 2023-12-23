# Swive

```shell
$ python -m venv venv
$ source venv/bin/activate
$ python -m pip install .
$ python -m pip install ".[dev]"
$ python manage.py makemigrations --settings=swive.settings.development 
$ python manage.py migrate --settings=swive.settings.development
$ python manage.py createsuperuser --settings=swive.settings.development
$ python manage.py runserver --settings=swive.settings.development
```
