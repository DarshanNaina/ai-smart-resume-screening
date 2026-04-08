#!/bin/bash
python manage.py migrate
python -m gunicorn resume_system.wsgi:application
