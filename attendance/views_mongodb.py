from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from bson import ObjectId
import csv
import json

from .mongodb_utils import MongoDBManager

# Initialize MongoDB managers
devotees_db = MongoDBManager('devotees')
sabhas_db = MongoDBManager('sabhas')
attendance_db = MongoDBManager('attendance_records')

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid credentials')
    return render(request, 'registration/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    total_devotees = devotees_db.count()
    recent_sabhas_raw = sabhas_db.find(sort=[('date', -1)], limit=5)
    recent_sabhas = []
    for sabha in recent_sabhas_raw:
        sabha['id'] = str(sabha['_id'])
        sabha['get_sabha_type_display'] = sabha.get('sabha_type', '').title() + ' Sabha'
        recent_sabhas.append(sabha)
    
    total_attendance_records = attendance_db.count()
    present_records = attendance_db.count({'status': 'present'})
    attendance_rate = round((present_records / total_attendance_records * 100) if total_attendance_records > 0 else 0)
    
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    this_week_sabhas = sabhas_db.count({
        'date': {'$gte': week_start.isoformat(), '$lte': week_end.isoformat()}
    })
    
    context = {
        'total_devotees': total_devotees,
        'recent_sabhas': recent_sabhas,
        'attendance_rate': attendance_rate,
        'this_week_sabhas': this_week_sabhas,
    }
    return render(request, 'attendance/dashboard.html', context)

@login_required
def devotee_list(request):
    search_query = request.GET.get('search', '')
    
    query = {}
    if search_query:
        query = {'$or': [
            {'name': {'$regex': search_query, '$options': 'i'}},
            {'contact_number': {'$regex': search_query}}
        ]}
    
    devotees_raw = devotees_db.find(query, sort=[('name', 1)])
    devotees = []
    for devotee in devotees_raw:
        devotee['id'] = str(devotee['_id'])
        devotee['get_sabha_type_display'] = devotee.get('sabha_type', '').title()
        devotees.append(devotee)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        devotees_data = [{
            'id': str(d['_id']),
            'name': d['name'],
            'contact_number': d['contact_number'],
            'sabha_type_display': d['sabha_type'].title(),
            'age_group': d.get('age_group', 'N/A'),
            'join_date': d['join_date'],
            'photo_url': d.get('photo_url', '')
        } for d in devotees]
        
        return JsonResponse({'devotees': devotees_data, 'total_count': len(devotees_data)})
    
    return render(request, 'attendance/devotee_list.html', {
        'page_obj': devotees,
        'search_query': search_query,
        'total_count': len(devotees)
    })

@login_required
def devotee_add(request):
    if request.method == 'POST':
        devotee_data = {
            'name': request.POST.get('name'),
            'contact_number': request.POST.get('contact_number'),
            'age_group': request.POST.get('age_group'),
            'sabha_type': request.POST.get('sabha_type'),
            'address': request.POST.get('address'),
            'join_date': request.POST.get('join_date'),
            'photo_url': request.POST.get('photo_url', ''),
            'created_at': datetime.now().isoformat()
        }
        devotees_db.insert_one(devotee_data)
        messages.success(request, 'Devotee added successfully!')
        return redirect('devotee_list')
    
    return render(request, 'attendance/devotee_form.html', {'title': 'Add Devotee', 'today': datetime.now().date().isoformat()})

@login_required
def devotee_detail(request, pk):
    devotee = devotees_db.find_one({'_id': ObjectId(pk)})
    if not devotee:
        messages.error(request, 'Devotee not found')
        return redirect('devotee_list')
    devotee['id'] = str(devotee['_id'])
    devotee['pk'] = str(devotee['_id'])
    devotee['get_sabha_type_display'] = devotee.get('sabha_type', '').title()
    return render(request, 'attendance/devotee_detail.html', {'devotee': devotee})

@login_required
def devotee_edit(request, pk):
    devotee = devotees_db.find_one({'_id': ObjectId(pk)})
    if not devotee:
        messages.error(request, 'Devotee not found')
        return redirect('devotee_list')
    
    if request.method == 'POST':
        update_data = {
            'name': request.POST.get('name'),
            'contact_number': request.POST.get('contact_number'),
            'age_group': request.POST.get('age_group'),
            'sabha_type': request.POST.get('sabha_type'),
            'address': request.POST.get('address'),
            'join_date': request.POST.get('join_date'),
            'photo_url': request.POST.get('photo_url', ''),
            'updated_at': datetime.now().isoformat()
        }
        devotees_db.update_one({'_id': ObjectId(pk)}, update_data)
        messages.success(request, 'Devotee updated successfully!')
        return redirect('devotee_detail', pk=pk)
    
    return render(request, 'attendance/devotee_form.html', {'devotee': devotee, 'title': 'Edit Devotee', 'today': datetime.now().date().isoformat()})

@login_required
def sabha_list(request):
    sabhas_raw = sabhas_db.find(sort=[('date', -1)])
    sabhas = []
    for sabha in sabhas_raw:
        sabha['id'] = str(sabha['_id'])
        sabha['get_sabha_type_display'] = sabha.get('sabha_type', '').title() + ' Sabha'
        sabhas.append(sabha)
    return render(request, 'attendance/sabha_list.html', {'sabhas': sabhas})

@login_required
def sabha_add(request):
    if request.method == 'POST':
        sabha_data = {
            'date': request.POST.get('date'),
            'sabha_type': request.POST.get('sabha_type'),
            'location': request.POST.get('location'),
            'start_time': request.POST.get('start_time'),
            'end_time': request.POST.get('end_time'),
            'created_at': datetime.now().isoformat()
        }
        sabhas_db.insert_one(sabha_data)
        messages.success(request, 'Sabha created successfully!')
        return redirect('sabha_list')
    
    return render(request, 'attendance/sabha_form.html', {'title': 'Create Sabha', 'today': datetime.now().date().isoformat()})

@login_required
def mark_attendance(request, sabha_id):
    sabha = sabhas_db.find_one({'_id': ObjectId(sabha_id)})
    if not sabha:
        messages.error(request, 'Sabha not found')
        return redirect('sabha_list')
    sabha['id'] = str(sabha['_id'])
    sabha['get_sabha_type_display'] = sabha.get('sabha_type', '').title() + ' Sabha'
    
    search_query = request.GET.get('search', '')
    query = {'sabha_type': sabha['sabha_type']}
    
    if search_query:
        query = {
            '$and': [
                {'sabha_type': sabha['sabha_type']},
                {'$or': [
                    {'name': {'$regex': search_query, '$options': 'i'}},
                    {'contact_number': {'$regex': search_query}}
                ]}
            ]
        }
    
    devotees_raw = devotees_db.find(query, sort=[('name', 1)])
    devotees = []
    for devotee in devotees_raw:
        devotee['id'] = str(devotee['_id'])
        devotee['get_sabha_type_display'] = devotee.get('sabha_type', '').title()
        devotees.append(devotee)
    
    if request.method == 'POST':
        for devotee in devotees:
            devotee_id = str(devotee['_id'])
            status = request.POST.get(f'status_{devotee_id}', 'absent')
            notes = request.POST.get(f'notes_{devotee_id}', '')
            
            existing = attendance_db.find_one({
                'devotee_id': devotee_id,
                'sabha_id': sabha_id
            })
            
            if existing:
                attendance_db.update_one(
                    {'_id': existing['_id']},
                    {'status': status, 'notes': notes, 'updated_at': datetime.now().isoformat()}
                )
            else:
                attendance_db.insert_one({
                    'devotee_id': devotee_id,
                    'devotee_name': devotee['name'],
                    'sabha_id': sabha_id,
                    'sabha_date': sabha['date'],
                    'sabha_type': sabha['sabha_type'],
                    'status': status,
                    'notes': notes,
                    'marked_at': datetime.now().isoformat()
                })
        
        messages.success(request, 'Attendance marked successfully!')
        return redirect('sabha_list')
    
    # Auto-create absent records for all devotees if not exists
    for devotee in devotees:
        devotee_id = str(devotee['_id'])
        existing = attendance_db.find_one({'devotee_id': devotee_id, 'sabha_id': sabha_id})
        if not existing:
            attendance_db.insert_one({
                'devotee_id': devotee_id,
                'devotee_name': devotee['name'],
                'sabha_id': sabha_id,
                'sabha_date': sabha['date'],
                'sabha_type': sabha['sabha_type'],
                'status': 'absent',
                'notes': '',
                'marked_at': datetime.now().isoformat()
            })
    
    existing_attendance = {
        att['devotee_id']: att for att in attendance_db.find({'sabha_id': sabha_id})
    }
    
    context = {
        'sabha': sabha,
        'devotees': devotees,
        'page_obj': devotees,
        'existing_attendance': existing_attendance,
        'search_query': search_query,
        'total_count': len(devotees)
    }
    return render(request, 'attendance/mark_attendance.html', context)

@login_required
def attendance_analytics(request):
    from collections import defaultdict
    from datetime import timedelta
    
    # Get filters
    sabha_type = request.GET.get('sabha_type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Build query
    query = {}
    if sabha_type:
        query['sabha_type'] = sabha_type
    if date_from:
        query.setdefault('sabha_date', {})['$gte'] = date_from
    if date_to:
        query.setdefault('sabha_date', {})['$lte'] = date_to
    
    # Get all attendance records
    records = attendance_db.find(query)
    
    # Aggregate data
    sabha_counts = defaultdict(int)
    weekly_data = defaultdict(lambda: defaultdict(int))
    monthly_trend = defaultdict(int)
    date_intensity = defaultdict(int)
    
    for record in records:
        if record['status'] == 'present':
            sabha_counts[record['sabha_type']] += 1
            date_intensity[record['sabha_date']] += 1
            
            # Monthly trend (last 3 months)
            try:
                date_obj = datetime.fromisoformat(record['sabha_date'])
                month_key = date_obj.strftime('%Y-%m')
                monthly_trend[month_key] += 1
            except:
                pass
    
    # Prepare response
    data = {
        'sabha_counts': dict(sabha_counts),
        'monthly_trend': dict(sorted(monthly_trend.items())),
        'date_intensity': dict(date_intensity),
        'total': sum(sabha_counts.values())
    }
    
    return JsonResponse(data)

@login_required
def attendance_report(request):
    sabha_type = request.GET.get('sabha_type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    query = {}
    if sabha_type:
        query['sabha_type'] = sabha_type
    if date_from:
        query.setdefault('sabha_date', {})['$gte'] = date_from
    if date_to:
        query.setdefault('sabha_date', {})['$lte'] = date_to
    
    attendance_records = attendance_db.find(query, sort=[('sabha_date', -1)])
    
    context = {
        'attendance_records': attendance_records,
        'sabha_types': [('bal', 'Bal Sabha'), ('yuvak', 'Yuvak Sabha'), ('mahila', 'Mahila Sabha'), ('sanyukt', 'Sanyukt Sabha')],
        'filters': {'sabha_type': sabha_type, 'date_from': date_from, 'date_to': date_to}
    }
    return render(request, 'attendance/attendance_report.html', context)

@login_required
def export_attendance(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Devotee Name', 'Sabha Type', 'Date', 'Status', 'Notes'])
    
    sabha_type = request.GET.get('sabha_type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    query = {}
    if sabha_type:
        query['sabha_type'] = sabha_type
    if date_from:
        query.setdefault('sabha_date', {})['$gte'] = date_from
    if date_to:
        query.setdefault('sabha_date', {})['$lte'] = date_to
    
    for attendance in attendance_db.find(query):
        writer.writerow([
            attendance['devotee_name'],
            attendance['sabha_type'].title(),
            attendance['sabha_date'],
            attendance['status'].title(),
            attendance.get('notes', '')
        ])
    
    return response

@login_required
def upload_devotees(request):
    from .forms import DevoteeUploadForm
    from .utils import process_excel_file
    import tempfile
    import os
    
    if request.method == 'POST':
        form = DevoteeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = form.cleaned_data['excel_file']
            sabha_type_filter = form.cleaned_data.get('sabha_type_filter')
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                for chunk in excel_file.chunks():
                    tmp_file.write(chunk)
                tmp_file_path = tmp_file.name
            
            try:
                result, error = process_excel_file(tmp_file_path, sabha_type_filter)
                
                if error:
                    messages.error(request, error)
                    return render(request, 'attendance/upload_devotees.html', {'form': form})
                
                valid_rows = result['valid_rows']
                errors = result['errors']
                
                if errors:
                    context = {
                        'form': form,
                        'errors': errors,
                        'total_rows': len(valid_rows) + len(errors),
                        'valid_count': len(valid_rows),
                        'error_count': len(errors)
                    }
                    return render(request, 'attendance/upload_devotees.html', context)
                
                # Save to MongoDB
                created_count = 0
                updated_count = 0
                for row in valid_rows:
                    # Convert date to string
                    if 'join_date' in row and hasattr(row['join_date'], 'isoformat'):
                        row['join_date'] = row['join_date'].isoformat()
                    
                    existing = devotees_db.find_one({'contact_number': row['contact_number']})
                    if existing:
                        devotees_db.update_one({'_id': existing['_id']}, row)
                        updated_count += 1
                    else:
                        row['created_at'] = datetime.now().isoformat()
                        devotees_db.insert_one(row)
                        created_count += 1
                
                messages.success(request, f'Successfully imported {created_count} new devotees and updated {updated_count} existing devotees!')
                return redirect('devotee_list')
                
            finally:
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
    else:
        form = DevoteeUploadForm()
    
    return render(request, 'attendance/upload_devotees.html', {'form': form})

@login_required
@require_POST
def save_individual_attendance(request):
    try:
        data = json.loads(request.body)
        sabha_id = data.get('sabha_id')
        devotee_id = data.get('devotee_id')
        status = data.get('status', 'absent')
        notes = data.get('notes', '')
        
        sabha = sabhas_db.find_one({'_id': ObjectId(sabha_id)})
        devotee = devotees_db.find_one({'_id': ObjectId(devotee_id)})
        
        if not sabha or not devotee:
            return JsonResponse({'success': False, 'error': 'Sabha or Devotee not found'})
        
        existing = attendance_db.find_one({'devotee_id': devotee_id, 'sabha_id': sabha_id})
        
        if existing:
            attendance_db.update_one(
                {'_id': existing['_id']},
                {'status': status, 'notes': notes, 'updated_at': datetime.now().isoformat()}
            )
        else:
            attendance_db.insert_one({
                'devotee_id': devotee_id,
                'devotee_name': devotee['name'],
                'sabha_id': sabha_id,
                'sabha_date': sabha['date'],
                'sabha_type': sabha['sabha_type'],
                'status': status,
                'notes': notes,
                'marked_at': datetime.now().isoformat()
            })
        
        return JsonResponse({'success': True, 'message': 'Attendance saved'})
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)})
