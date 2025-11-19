from django.core.management.base import BaseCommand
from attendance.models import Attendance, Sabha, Devotee

class Command(BaseCommand):
    help = 'Clear all data from database'

    def handle(self, *args, **options):
        self.stdout.write('Clearing all data...')
        
        Attendance.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✓ Cleared all attendance records'))
        
        Sabha.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✓ Cleared all sabha records'))
        
        Devotee.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✓ Cleared all devotee records'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ All data cleared successfully!'))
