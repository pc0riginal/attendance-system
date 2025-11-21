from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from attendance.models import Devotee, Sabha, UserProfile

class Command(BaseCommand):
    help = 'Setup custom permissions and user groups for temple attendance system'

    def handle(self, *args, **options):
        # Create custom permissions
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
            perm, created = Permission.objects.get_or_create(
                codename=codename,
                name=name,
                content_type=content_type
            )
            if created:
                self.stdout.write(f'Created permission: {name}')
        
        # Create user groups
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
            self.stdout.write('Created Temple Admin group')
        
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
            self.stdout.write('Created Sabha User group')
        
        # Create UserProfile for existing users without one
        for user in User.objects.all():
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={'allowed_sabha_types': ['bal', 'yuvak', 'mahila', 'sanyukt']}
            )
            if created:
                self.stdout.write(f'Created profile for user: {user.username}')
        
        self.stdout.write(self.style.SUCCESS('Successfully setup permissions and groups'))