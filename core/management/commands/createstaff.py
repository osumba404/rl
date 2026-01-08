from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Profile

class Command(BaseCommand):
    help = 'Create a staff user for admin access'

    def handle(self, *args, **options):
        username = 'admin'
        email = 'admin@example.com'
        password = 'admin123'
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(f'User {username} already exists')
            return
            
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        
        Profile.objects.create(user=user, verified_status=True)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created staff user: {username} / {password}')
        )