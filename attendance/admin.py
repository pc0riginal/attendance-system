from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import Devotee, Sabha, Attendance
from .models import UserProfile
import json

class UserAdmin(BaseUserAdmin):
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(id=request.user.id)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_allowed_sabha_types')
    list_filter = ('allowed_sabha_types',)
    search_fields = ('user__username',)
    
    def get_allowed_sabha_types(self, obj):
        return ', '.join(obj.allowed_sabha_types) if obj.allowed_sabha_types else 'None'
    get_allowed_sabha_types.short_description = 'Allowed Sabha Types'
    
    def has_module_permission(self, request):
        return request.user.is_superuser

class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0
    readonly_fields = ('marked_at',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Filter by user's allowed sabha types
        try:
            profile = request.user.userprofile
            allowed_types = profile.allowed_sabha_types
            return qs.filter(sabha__sabha_type__in=allowed_types)
        except:
            return qs.none()

@admin.register(Devotee)
class DevoteeAdmin(admin.ModelAdmin):
    list_display = ('devotee_id', 'name', 'masked_contact', 'sabha_type', 'devotee_type', 'join_date')
    list_filter = ('sabha_type', 'devotee_type', 'gender')
    search_fields = ('name', 'devotee_id', 'contact_number')
    readonly_fields = ('devotee_id',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('devotee_id', 'name', 'contact_number', 'devotee_type')
        }),
        ('Personal Details', {
            'fields': ('date_of_birth', 'gender', 'age', 'sabha_type')
        }),
        ('Address', {
            'fields': ('address_line', 'landmark', 'zone')
        }),
        ('Other', {
            'fields': ('join_date', 'photo_url')
        }),
    )
    
    def masked_contact(self, obj):
        if self.request.user.is_superuser:
            return obj.contact_number
        # Show only last 5 digits for regular users
        if len(obj.contact_number) >= 5:
            return '*' * (len(obj.contact_number) - 5) + obj.contact_number[-5:]
        return obj.contact_number
    masked_contact.short_description = 'Contact Number'
    
    def get_queryset(self, request):
        self.request = request
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            profile = request.user.userprofile
            allowed_types = profile.allowed_sabha_types
            return qs.filter(sabha_type__in=allowed_types)
        except:
            return qs.none()
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            # Limit sabha_type choices for regular users
            try:
                profile = request.user.userprofile
                allowed_types = profile.allowed_sabha_types
                sabha_choices = [(t, t.title()) for t in allowed_types]
                form.base_fields['sabha_type'].choices = sabha_choices
            except:
                pass
        return form

@admin.register(Sabha)
class SabhaAdmin(admin.ModelAdmin):
    list_display = ('date', 'sabha_type', 'location', 'mandal', 'xetra', 'created_by', 'created_at')
    list_filter = ('sabha_type', 'mandal', 'xetra', 'date', 'created_by')
    search_fields = ('location', 'mandal', 'xetra')
    date_hierarchy = 'date'
    readonly_fields = ('created_by', 'created_at')
    inlines = [AttendanceInline]
    
    fieldsets = (
        ('Sabha Details', {
            'fields': ('date', 'sabha_type', 'location')
        }),
        ('Organization', {
            'fields': ('mandal', 'xetra')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time')
        }),
        ('Audit Info', {
            'fields': ('created_by', 'created_at')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Filter by user's allowed sabha types
        try:
            profile = request.user.userprofile
            allowed_types = profile.allowed_sabha_types
            return qs.filter(sabha_type__in=allowed_types)
        except:
            return qs.none()
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            # Limit sabha_type choices for regular users
            try:
                profile = request.user.userprofile
                allowed_types = profile.allowed_sabha_types
                sabha_choices = [(t, t.title()) for t in allowed_types]
                form.base_fields['sabha_type'].choices = sabha_choices
            except:
                pass
        return form

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('devotee', 'sabha', 'status', 'marked_at')
    list_filter = ('status', 'sabha__sabha_type', 'sabha__date')
    search_fields = ('devotee__name', 'devotee__devotee_id')
    date_hierarchy = 'marked_at'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Filter by user's allowed sabha types
        try:
            profile = request.user.userprofile
            allowed_types = profile.allowed_sabha_types
            return qs.filter(sabha__sabha_type__in=allowed_types)
        except:
            return qs.none()

# Custom admin site configuration
admin.site.site_header = "🏛️ Temple Attendance Management"
admin.site.site_title = "Temple Admin"
admin.site.index_title = "Temple Attendance Administration"