from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from attendance.models import UserProfile

class Command(BaseCommand):
    help = 'Create a test user with specific sabha permissions'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username for the test user')
        parser.add_argument('--sabha-types', nargs='+', default=['bal'], 
                          help='Allowed sabha types (bal, yuvak, mahila, sanyukt)')
        parser.add_argument('--password', type=str, default='testpass123',
                          help='Password for the test user')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        sabha_types = options['sabha_types']
        
        # Validate sabha types
        valid_types = ['bal', 'yuvak', 'mahila', 'sanyukt']
        for sabha_type in sabha_types:
            if sabha_type not in valid_types:
                self.stdout.write(
                    self.style.ERROR(f'Invalid sabha type: {sabha_type}. Valid types: {valid_types}')
                )
                return
        
        # Create or get user
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@temple.com',
                'first_name': username.title(),
                'is_staff': True,  # Allow admin access
            }
        )
        
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Created user: {username}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'User {username} already exists')
            )
        
        # Update user profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.allowed_sabha_types = sabha_types
        profile.save()
        
        self.stdout.write(
            self.style.SUCCESS(f'Set sabha permissions for {username}: {sabha_types}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Login credentials - Username: {username}, Password: {password}')
        )