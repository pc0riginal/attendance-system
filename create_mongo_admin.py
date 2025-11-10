import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'temple_attendance.settings')
django.setup()

from django.contrib.auth.models import User

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@temple.com', 'admin123')
    print("Admin user created successfully!")
    print("Username: admin")
    print("Password: admin123")
else:
    print("Admin user already exists!")
