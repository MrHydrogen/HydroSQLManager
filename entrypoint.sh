#!/bin/sh

set -e

/wait-for.sh $DB_HOST:$DB_PORT
python manage.py migrate
exec uwsgi --ini /uwsgi.conf