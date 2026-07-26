from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

ADMIN_USERNAME = 'admin'
ADMIN_EMAIL = 'admin@gmail.com'
ADMIN_PASSWORD = '123456'


class Command(BaseCommand):
    help = 'Creates/resets the permanent superadmin account for Darkshadow'

    def handle(self, *args, **kwargs):
        user, created = User.objects.get_or_create(username=ADMIN_USERNAME)
        user.email = ADMIN_EMAIL
        user.set_password(ADMIN_PASSWORD)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.first_name = 'Admin'
        user.last_name = 'Darkshadow'
        user.save()

        action = 'Created' if created else 'Reset'
        self.stdout.write(self.style.SUCCESS(
            f'{action} superadmin successfully!\n'
            f'  Username : {ADMIN_USERNAME}\n'
            f'  Email    : {ADMIN_EMAIL}\n'
            f'  Password : {ADMIN_PASSWORD}\n'
            f'  Panel    : /ds-admin/'
        ))
