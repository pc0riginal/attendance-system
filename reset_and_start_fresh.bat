@echo off
echo Stopping all Python processes...
taskkill /F /IM python.exe 2>nul

timeout /t 2 /nobreak >nul

echo Deleting old database...
if exist db.sqlite3 del db.sqlite3

echo Running migrations...
python manage.py migrate

echo.
echo ========================================
echo Database reset complete!
echo Run: python manage.py createsuperuser
echo Then: python manage.py runserver
echo ========================================
