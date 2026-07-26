from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Creates a permanent superadmin account for Darkshadow'

    ADMIN_USERNAME = 'admin'
    ADMIN_EMAIL = 'admin@gmail.com'
    ADMIN_PASSWORD = '123456'

    def handle(self, *args, **kwargs):
        if User.objects.filter(username=self.ADMIN_USERNAME).exists():
            user = User.objects.get(username=self.ADMIN_USERNAME)
            user.email = self.ADMIN_EMAIL
            user.set_password(self.ADMIN_PASSWORD)
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.save()
            self.stdout.write(self.style.WARNING(
                f'Superadmin already existed — credentials refreshed.'
            ))
        else:
            User.objects.create_superuser(
                username=self.ADMIN_USERNAME,
                email=self.ADMIN_EMAIL,
                password=self.ADMIN_PASSWORD,
            )
            self.stdout.write(self.style.SUCCESS(
                f'Superadmin created successfully!'
            ))
        self.stdout.write(self.style.SUCCESS(
            f'  Username : {self.ADMIN_USERNAME}\n'
            f'  Email    : {self.ADMIN_EMAIL}\n'
            f'  Password : {self.ADMIN_PASSWORD}\n'
            f'  URL      : /admin/'
        ))
