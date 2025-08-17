#!/bin/bash

gunicorn ouaf.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --timeout 60
