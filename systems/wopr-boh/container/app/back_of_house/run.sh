#!/bin/bash 

PGPASSFILE=./.pgpass PGSERVICEFILE=./.pg_service.conf ./manage.py "$@"

