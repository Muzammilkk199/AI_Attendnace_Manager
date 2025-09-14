from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Create an admin user for the attendance system'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username for the admin user', default='admin')
        parser.add_argument('--email', type=str, help='Email for the admin user', default='admin@attendance.com')
        parser.add_argument('--password', type=str, help='Password for the admin user', default='admin123')
        parser.add_argument('--first-name', type=str, help='First name for the admin user', default='Admin')
        parser.add_argument('--last-name', type=str, help='Last name for the admin user', default='User')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']

        try:
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'User "{username}" already exists!')
                )
                return

            # Create the superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            self.stdout.write(
                self.style.SUCCESS(f'Successfully created admin user "{username}"')
            )
            self.stdout.write(f'Username: {username}')
            self.stdout.write(f'Email: {email}')
            self.stdout.write(f'Password: {password}')
            self.stdout.write('')
            self.stdout.write('You can now login to the system using these credentials.')

        except IntegrityError:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" already exists!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating user: {str(e)}')
            )
