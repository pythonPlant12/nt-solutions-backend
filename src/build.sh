#!/usr/bin/env bash
# Exit on error
set -o errexit

chmod a+x build.sh

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

# Convert static asset files
# python ../src/django_nt_solutions/manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate
