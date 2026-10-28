import os

from django.core.management.base import BaseCommand

from newsapp.models import CustomUser


class Command(BaseCommand):
    help = "Create or verify the production Django superuser from environment variables."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "").strip()
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "")

        if not username or not password:
            self.stdout.write("Superuser environment variables are not configured; skipping.")
            return

        user, created = CustomUser.objects.get_or_create(
            username=username,
            defaults={"email": email, "user_type": 1},
        )

        changed = False
        if not user.is_staff:
            user.is_staff = True
            changed = True
        if not user.is_superuser:
            user.is_superuser = True
            changed = True
        if not user.is_active:
            user.is_active = True
            changed = True
        if str(user.user_type) != "1":
            user.user_type = 1
            changed = True
        if email and user.email != email:
            user.email = email
            changed = True
        if created or not user.check_password(password):
            user.set_password(password)
            changed = True

        if changed:
            user.save()

        action = "Created" if created else "Verified"
        self.stdout.write(f"{action} superuser: {username}")
