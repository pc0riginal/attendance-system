import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'temple_attendance.settings')
django.setup()

from django.conf import settings
from attendance.mongodb_utils import MongoDBManager, get_mongodb

print("Testing MongoDB Connection...")
print(f"MongoDB URI: {settings.MONGODB_URI}")
print(f"Database Name: {settings.MONGODB_NAME}")

mongodb = get_mongodb()

if mongodb is not None:
    print("[OK] MongoDB connected successfully!")
    
    # Test collections
    collections = mongodb.list_collection_names()
    print(f"\nExisting collections: {collections}")
    
    # Test insert
    test_manager = MongoDBManager('test_collection')
    result = test_manager.insert_one({'test': 'data', 'message': 'MongoDB Atlas connection test'})
    
    if result:
        print("\n[OK] Test document inserted successfully!")
        print(f"Inserted ID: {result.inserted_id}")
        
        # Test find
        doc = test_manager.find_one({'test': 'data'})
        print(f"[OK] Test document retrieved: {doc}")
        
        # Clean up
        test_manager.delete_one({'test': 'data'})
        print("[OK] Test document deleted")
    
    print("\n[SUCCESS] MongoDB is working correctly!")
else:
    print("[ERROR] MongoDB connection failed!")
