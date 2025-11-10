# MongoDB Atlas Integration Guide

## Overview
Your Temple Attendance System is now configured to use MongoDB Atlas cloud storage for application data while keeping SQLite for Django's authentication and admin functionality.

## Configuration

### Connection Details
- **MongoDB URI**: `mongodb+srv://msm98:paras123@cluster0.4gnmc.mongodb.net/`
- **Database Name**: `temple_attendance`
- **Cluster**: Cluster0

### Architecture
- **MongoDB Atlas**: Stores devotees, sabhas, and attendance records
- **SQLite**: Handles Django admin, user authentication, and sessions

## Files Modified

1. **requirements.txt** - Added MongoDB dependencies:
   - `pymongo[srv]>=4.0`
   - `dnspython`

2. **temple_attendance/settings.py** - Added MongoDB configuration:
   ```python
   MONGODB_URI = 'mongodb+srv://msm98:paras123@cluster0.4gnmc.mongodb.net/...'
   MONGODB_NAME = 'temple_attendance'
   ```

3. **attendance/mongodb_utils.py** - Created MongoDB utility module with:
   - `get_mongodb()` - Get database connection
   - `MongoDBManager` - CRUD operations manager

## Usage

### Using MongoDB in Your Views

```python
from attendance.mongodb_utils import MongoDBManager

# Initialize manager for a collection
devotees_manager = MongoDBManager('devotees')

# Insert a document
devotees_manager.insert_one({
    'name': 'John Doe',
    'age': 25,
    'sabha_type': 'yuvak'
})

# Find documents
all_devotees = devotees_manager.find()
specific_devotee = devotees_manager.find_one({'name': 'John Doe'})

# Update a document
devotees_manager.update_one(
    {'name': 'John Doe'},
    {'age': 26}
)

# Delete a document
devotees_manager.delete_one({'name': 'John Doe'})

# Count documents
count = devotees_manager.count({'sabha_type': 'yuvak'})
```

### Available Methods

- `insert_one(document)` - Insert single document
- `insert_many(documents)` - Insert multiple documents
- `find_one(query)` - Find single document
- `find(query, sort, limit)` - Find multiple documents
- `update_one(query, update)` - Update single document
- `update_many(query, update)` - Update multiple documents
- `delete_one(query)` - Delete single document
- `delete_many(query)` - Delete multiple documents
- `count(query)` - Count documents

## Testing Connection

Run the test script to verify MongoDB connection:

```bash
python test_mongodb.py
```

Expected output:
```
[OK] MongoDB connected successfully!
[OK] Test document inserted successfully!
[OK] Test document retrieved
[OK] Test document deleted
[SUCCESS] MongoDB is working correctly!
```

## Existing Collections

Your MongoDB database already contains these collections from previous setup:
- `auth_user`
- `auth_permission`
- `auth_group`
- `attendance_devotee`
- `attendance_sabha`
- `attendance_attendance`
- `django_session`
- `django_migrations`
- `django_admin_log`
- `django_content_type`

## Next Steps

### Option 1: Continue Using Django ORM (Recommended for Stability)
Keep using Django models with SQLite for now. Your existing code will work without changes.

### Option 2: Migrate to Pure MongoDB
To fully migrate to MongoDB:

1. **Update Models** - Convert Django models to use MongoDB directly
2. **Update Views** - Replace ORM queries with MongoDBManager calls
3. **Migrate Data** - Export from SQLite and import to MongoDB

### Option 3: Hybrid Approach (Current Setup)
- Use SQLite for Django admin/auth (stable)
- Use MongoDB for new features and data storage
- Best of both worlds!

## Security Notes

⚠️ **Important**: Your MongoDB credentials are currently hardcoded in settings.py

### Recommended: Use Environment Variables

1. Create `.env` file:
```env
MONGODB_URI=mongodb+srv://msm98:paras123@cluster0.4gnmc.mongodb.net/
MONGODB_NAME=temple_attendance
```

2. Update settings.py:
```python
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI')
MONGODB_NAME = os.getenv('MONGODB_NAME', 'temple_attendance')
```

3. Install python-dotenv:
```bash
pip install python-dotenv
```

## Troubleshooting

### Connection Issues
- Verify MongoDB Atlas cluster is running
- Check IP whitelist in MongoDB Atlas (allow 0.0.0.0/0 for testing)
- Verify credentials are correct

### Import Errors
```bash
pip install pymongo dnspython --upgrade
```

### Test Connection
```bash
python test_mongodb.py
```

## MongoDB Atlas Dashboard

Access your database at: https://cloud.mongodb.com/
- View collections
- Monitor performance
- Manage users and security
- Set up backups

## Support

For MongoDB Atlas help:
- Documentation: https://docs.mongodb.com/
- Atlas Docs: https://docs.atlas.mongodb.com/

For Django integration:
- PyMongo Docs: https://pymongo.readthedocs.io/
