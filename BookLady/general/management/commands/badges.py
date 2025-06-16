from django.core.management.base import BaseCommand
from general.models import Badge

class Command(BaseCommand):
    Badge.objects.all().delete()
    help = 'Populate database with initial badges'

    def handle(self, *args, **kwargs):
        badges_data = [
            {"description": "Read 5 Books", "target_books": 5, "target_pages": 0, "image": "badges/5BooksBadge.png"},
            {"description": "Read 10 Books", "target_books": 10, "target_pages": 0, "image": "badges/10BooksBadge.png"},
            {"description": "Read 20 Books", "target_books": 20, "target_pages": 0, "image": "badges/20BooksBadge.png"},
            {"description": "Read 1000 Pages", "target_books": 0, "target_pages": 1000, "image": "badges/1000PagesBadge.png"},
            {"description": "Read 2000 Pages", "target_books": 0, "target_pages": 2000, "image": "badges/2000PagesBadge.png"},
        ]

        for badge_data in badges_data:
            badge = Badge.objects.create(
                description=badge_data["description"],
                target_books=badge_data["target_books"],
                target_pages=badge_data["target_pages"],
                image=badge_data["image"]
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created badge: {badge}'))
