from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Group
from django.db import models
from .models import Devotee, Sabha

def create_custom_permissions():
    """Create custom permissions for temple attendance system"""
    devotee_ct = ContentType.objects.get_for_model(Devotee)
    sabha_ct = ContentType.objects.get_for_model(Sabha)
    
    permissions = [
        ('can_view_sabha_type', 'Can view specific sabha types', devotee_ct),
        ('can_create_devotee', 'Can create devotee', devotee_ct),
        ('can_edit_devotee', 'Can edit devotee', devotee_ct),
        ('cannot_delete_devotee', 'Cannot delete devotee', devotee_ct),
        ('can_create_sabha_for_assigned_type', 'Can create sabha for assigned type', sabha_ct),
        ('can_mark_attendance', 'Can mark attendance', sabha_ct),
        ('can_view_reports', 'Can view reports (admin only)', sabha_ct),
        ('can_view_masked_mobile', 'Can view masked mobile numbers', devotee_ct),
    ]
    
    for codename, name, content_type in permissions:
        Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=content_type
        )

def create_user_groups():
    """Create user groups with appropriate permissions"""
    # Admin group
    admin_group, created = Group.objects.get_or_create(name='Temple Admin')
    if created:
        admin_perms = Permission.objects.filter(
            codename__in=[
                'can_view_sabha_type', 'can_create_devotee', 'can_edit_devotee',
                'can_create_sabha_for_assigned_type', 'can_mark_attendance', 'can_view_reports'
            ]
        )
        admin_group.permissions.set(admin_perms)
    
    # Regular user group
    user_group, created = Group.objects.get_or_create(name='Sabha User')
    if created:
        user_perms = Permission.objects.filter(
            codename__in=[
                'can_view_sabha_type', 'can_create_devotee', 'can_edit_devotee',
                'cannot_delete_devotee', 'can_mark_attendance', 'can_view_masked_mobile'
            ]
        )
        user_group.permissions.set(user_perms)

