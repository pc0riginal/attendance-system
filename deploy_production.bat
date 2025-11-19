@echo off
echo Deploying to production...
set DJANGO_SETTINGS_MODULE=production_settings

echo Running migrations...
python manage.py migrate --settings=production_settings

echo Creating superuser (if needed)...
python manage.py createsuperuser --settings=production_settings

echo Done!
