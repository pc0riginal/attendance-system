# MongoDB Quick Reference Card

## Import
```python
from attendance.mongodb_utils import MongoDBManager
```

## Initialize
```python
devotees = MongoDBManager('devotees')
sabhas = MongoDBManager('sabhas')
attendance = MongoDBManager('attendance_records')
```

## Create (Insert)
```python
# Single document
devotees.insert_one({
    'name': 'John Doe',
    'age': 25,
    'sabha_type': 'yuvak'
})

# Multiple documents
devotees.insert_many([
    {'name': 'Person 1', 'age': 20},
    {'name': 'Person 2', 'age': 30}
])
```

## Read (Find)
```python
# Find all
all_devotees = devotees.find()

# Find with filter
yuvak = devotees.find({'sabha_type': 'yuvak'})

# Find one
devotee = devotees.find_one({'name': 'John Doe'})

# Find with sorting
sorted_devotees = devotees.find(
    query={'age': {'$gte': 18}},
    sort=[('age', 1)],  # 1 = ascending, -1 = descending
    limit=10
)
```

## Update
```python
# Update one
devotees.update_one(
    {'name': 'John Doe'},
    {'age': 26}
)

# Update many
devotees.update_many(
    {'sabha_type': 'yuvak'},
    {'is_active': True}
)
```

## Delete
```python
# Delete one
devotees.delete_one({'name': 'John Doe'})

# Delete many
devotees.delete_many({'is_active': False})
```

## Count
```python
# Count all
total = devotees.count()

# Count with filter
yuvak_count = devotees.count({'sabha_type': 'yuvak'})
```

## Query Operators
```python
# Greater than
devotees.find({'age': {'$gt': 18}})

# Greater than or equal
devotees.find({'age': {'$gte': 18}})

# Less than
devotees.find({'age': {'$lt': 60}})

# Less than or equal
devotees.find({'age': {'$lte': 60}})

# Not equal
devotees.find({'status': {'$ne': 'inactive'}})

# In array
devotees.find({'sabha_type': {'$in': ['yuvak', 'mahila']}})

# Regex (pattern matching)
devotees.find({'name': {'$regex': '^John'}})

# And condition
devotees.find({
    'age': {'$gte': 18},
    'sabha_type': 'yuvak'
})

# Or condition
devotees.find({
    '$or': [
        {'age': {'$lt': 18}},
        {'age': {'$gt': 60}}
    ]
})
```

## Common Patterns

### Mark Attendance
```python
attendance.insert_one({
    'devotee_id': 'abc123',
    'sabha_id': 'xyz789',
    'status': 'present',
    'date': '2025-01-09',
    'marked_at': datetime.now().isoformat()
})
```

### Get Attendance Report
```python
# Get all present devotees for a sabha
present = attendance.find({
    'sabha_id': 'xyz789',
    'status': 'present'
})

# Get devotee attendance history
history = attendance.find(
    {'devotee_id': 'abc123'},
    sort=[('date', -1)],
    limit=10
)
```

### Search Devotees
```python
# Search by name
results = devotees.find({
    'name': {'$regex': 'patel', '$options': 'i'}  # case-insensitive
})

# Search by multiple fields
results = devotees.find({
    '$or': [
        {'name': {'$regex': 'john', '$options': 'i'}},
        {'contact_number': {'$regex': '9876'}}
    ]
})
```

### Analytics
```python
# Count by sabha type
bal_count = devotees.count({'sabha_type': 'bal'})
yuvak_count = devotees.count({'sabha_type': 'yuvak'})
mahila_count = devotees.count({'sabha_type': 'mahila'})

# Attendance percentage
total_devotees = devotees.count()
present_count = attendance.count({'status': 'present'})
percentage = (present_count / total_devotees) * 100
```

## Test Connection
```bash
python test_mongodb.py
```

## Run Examples
```bash
python example_mongodb_usage.py
```

## MongoDB Atlas Dashboard
https://cloud.mongodb.com/

## Connection String
```
mongodb+srv://msm98:paras123@cluster0.4gnmc.mongodb.net/
```

## Database Name
```
temple_attendance
```
