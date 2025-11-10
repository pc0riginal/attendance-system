import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'temple_attendance.settings')
django.setup()

from attendance.mongodb_utils import MongoDBManager

print("Setting up MongoDB collections...")

devotees_db = MongoDBManager('devotees')
sabhas_db = MongoDBManager('sabhas')
attendance_db = MongoDBManager('attendance_records')

print(f"Devotees: {devotees_db.count()} records")
print(f"Sabhas: {sabhas_db.count()} records")
print(f"Attendance: {attendance_db.count()} records")

print("\n[SUCCESS] MongoDB is ready!")
print("All new data will be stored in MongoDB Atlas cloud.")
