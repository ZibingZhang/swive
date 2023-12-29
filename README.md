# Swive

## Purpose

This Django app enables swim and dive coaches to make entries for meets.
View it at https://entries.needhamswive.com.

## Motivation

As of the 2023 &ndash; 2024 school year, the [MIAA](https://miaa.net/) has started using third-party software that enables coaches to view other team's meet entries.
Not all coaches know about this, but it gives coaches who know about this an unfair advantage as they can make their lineups around what other teams have submitted.
This app solves this issue by providing a platform to create user entries without the ability to view other team's entries until they are published.

## Local Development

```shell
# Create and activate a virtual environment
$ python -m venv venv
$ python venv/bin/activate
# Install dependencies
$ python -m pip install --upgrade pip
$ python -m pip install '.[dev]'
# Use development settings
$ export DJANGO_SETTINGS_MODULE='swive.settings.development'
# Initialize the database
$ python manage.py makemigrations
$ python manage.py migrate
# Create a superuser
$ python manage.py createsuperuser
# Start the server
$ python manage.py runserver
```
