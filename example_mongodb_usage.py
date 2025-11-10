"""
Example: Using MongoDB for Temple Attendance System

This file demonstrates how to use MongoDB instead of Django ORM
for devotees, sabhas, and attendance records.
"""

import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'temple_attendance.settings')
django.setup()

from attendance.mongodb_utils import MongoDBManager

# ============================================
# DEVOTEE OPERATIONS
# ============================================

devotees_db = MongoDBManager('devotees')

# Create a new devotee
new_devotee = {
    'name': 'Ramesh Patel',
    'contact_number': '9876543210',
    'age_group': 'adult',
    'sabha_type': 'yuvak',
    'address': '123 Temple Street',
    'join_date': datetime.now().isoformat(),
    'is_active': True
}

# Insert devotee
result = devotees_db.insert_one(new_devotee)
print(f"Devotee created with ID: {result.inserted_id}")

# Find all devotees
all_devotees = devotees_db.find()
print(f"\nTotal devotees: {len(all_devotees)}")

# Find devotees by sabha type
yuvak_devotees = devotees_db.find({'sabha_type': 'yuvak'})
print(f"Yuvak devotees: {len(yuvak_devotees)}")

# Find one devotee
devotee = devotees_db.find_one({'name': 'Ramesh Patel'})
print(f"\nFound devotee: {devotee}")

# Update devotee
devotees_db.update_one(
    {'name': 'Ramesh Patel'},
    {'contact_number': '9999999999'}
)
print("Devotee updated")

# ============================================
# SABHA OPERATIONS
# ============================================

sabhas_db = MongoDBManager('sabhas')

# Create a new sabha
new_sabha = {
    'date': datetime.now().isoformat(),
    'sabha_type': 'yuvak',
    'location': 'Main Hall',
    'start_time': '10:00',
    'end_time': '12:00',
    'description': 'Weekly Yuvak Sabha'
}

sabha_result = sabhas_db.insert_one(new_sabha)
print(f"\nSabha created with ID: {sabha_result.inserted_id}")

# Find today's sabhas
today_sabhas = sabhas_db.find(
    {'date': {'$gte': datetime.now().date().isoformat()}},
    sort=[('date', 1)]
)
print(f"Today's sabhas: {len(today_sabhas)}")

# ============================================
# ATTENDANCE OPERATIONS
# ============================================

attendance_db = MongoDBManager('attendance_records')

# Mark attendance
attendance_record = {
    'devotee_id': str(result.inserted_id),
    'devotee_name': 'Ramesh Patel',
    'sabha_id': str(sabha_result.inserted_id),
    'sabha_date': datetime.now().isoformat(),
    'status': 'present',
    'marked_at': datetime.now().isoformat(),
    'notes': 'On time'
}

attendance_result = attendance_db.insert_one(attendance_record)
print(f"\nAttendance marked with ID: {attendance_result.inserted_id}")

# Get attendance for a devotee
devotee_attendance = attendance_db.find(
    {'devotee_id': str(result.inserted_id)},
    sort=[('sabha_date', -1)]
)
print(f"Devotee attendance records: {len(devotee_attendance)}")

# Get attendance for a sabha
sabha_attendance = attendance_db.find({'sabha_id': str(sabha_result.inserted_id)})
print(f"Sabha attendance count: {len(sabha_attendance)}")

# ============================================
# ANALYTICS & REPORTS
# ============================================

# Count present devotees
present_count = attendance_db.count({'status': 'present'})
print(f"\nTotal present: {present_count}")

# Count by sabha type
yuvak_count = devotees_db.count({'sabha_type': 'yuvak'})
mahila_count = devotees_db.count({'sabha_type': 'mahila'})
bal_count = devotees_db.count({'sabha_type': 'bal'})

print(f"\nDevotee Distribution:")
print(f"  Yuvak: {yuvak_count}")
print(f"  Mahila: {mahila_count}")
print(f"  Bal: {bal_count}")

# ============================================
# BULK OPERATIONS
# ============================================

# Insert multiple devotees
bulk_devotees = [
    {
        'name': f'Devotee {i}',
        'contact_number': f'98765432{i:02d}',
        'age_group': 'adult',
        'sabha_type': 'general',
        'join_date': datetime.now().isoformat()
    }
    for i in range(1, 6)
]

bulk_result = devotees_db.insert_many(bulk_devotees)
print(f"\n{len(bulk_result.inserted_ids)} devotees inserted in bulk")

# ============================================
# CLEANUP (Optional)
# ============================================

# Delete test data
devotees_db.delete_one({'name': 'Ramesh Patel'})
devotees_db.delete_many({'name': {'$regex': '^Devotee '}})
sabhas_db.delete_one({'_id': sabha_result.inserted_id})
attendance_db.delete_one({'_id': attendance_result.inserted_id})

print("\nTest data cleaned up")
print("\n[SUCCESS] MongoDB operations completed!")
