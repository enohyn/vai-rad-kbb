"""Create a demo user. Usage: python manage.py seed_demo_user (idempotent)."""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Create (or confirm) the demo/login user."

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            default=os.environ.get("DEMO_EMAIL", "demo@kanban.test"),
        )
        parser.add_argument(
            "--password",
            default=os.environ.get("DEMO_PASSWORD", "demoPass123!"),
        )
        parser.add_argument(
            "--first-name",
            default=os.environ.get("DEMO_FIRST_NAME", "Demo"),
        )
        parser.add_argument(
            "--last-name",
            default=os.environ.get("DEMO_LAST_NAME", "User"),
        )

    def handle(self, *args, **options):
        email = options["email"]
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f"User {email} already exists."))
            return
        User.objects.create_user(
            email=email,
            password=options["password"],
            first_name=options["first_name"],
            last_name=options["last_name"],
        )
        self.stdout.write(self.style.SUCCESS(f"Created demo user {email}."))