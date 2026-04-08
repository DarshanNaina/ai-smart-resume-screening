from django.core.management.base import BaseCommand

from core.models import Job, Organization, User


class Command(BaseCommand):
    help = "Seed demo organization, HR, candidate, and jobs."

    def handle(self, *args, **options):
        org, _ = Organization.objects.get_or_create(
            name="Demo Organization",
            defaults={"email": "demo-org@example.com", "is_approved": True},
        )
        if not org.is_approved:
            org.is_approved = True
            org.save(update_fields=["is_approved"])

        admin, created = User.objects.get_or_create(
            username="admin_demo",
            defaults={"email": "admin_demo@example.com", "role": User.ROLE_ADMIN, "is_staff": True, "is_superuser": True},
        )
        if created:
            admin.set_password("AdminDemo@123")
            admin.save()

        hr, created = User.objects.get_or_create(
            username="hr_demo",
            defaults={"email": "hr_demo@example.com", "role": User.ROLE_HR, "organization": org},
        )
        if created:
            hr.set_password("HrDemo@123")
            hr.save()

        client, created = User.objects.get_or_create(
            username="client_demo",
            defaults={"email": "client_demo@example.com", "role": User.ROLE_CLIENT},
        )
        if created:
            client.set_password("ClientDemo@123")
            client.save()

        Job.objects.get_or_create(
            organization=org,
            title="Junior Data Scientist",
            defaults={
                "description": "Python, Machine Learning, SQL, Pandas, Communication",
                "min_experience": 1,
                "is_active": True,
                "created_by": hr,
            },
        )
        Job.objects.get_or_create(
            organization=org,
            title="Backend Python Developer",
            defaults={
                "description": "Python, Django, REST API, PostgreSQL, Git, Docker",
                "min_experience": 2,
                "is_active": True,
                "created_by": hr,
            },
        )

        self.stdout.write(self.style.SUCCESS("Demo seed complete."))
        self.stdout.write("Users: admin_demo / hr_demo / client_demo")
        self.stdout.write("Passwords: AdminDemo@123 | HrDemo@123 | ClientDemo@123")
