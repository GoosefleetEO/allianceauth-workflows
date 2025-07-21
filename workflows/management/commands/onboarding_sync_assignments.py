# Django
from django.core.management.base import BaseCommand

from ...models import ActionItem, Wizard


class Command(BaseCommand):
    help = "Syncing all the Models from Secure Group Filters"

    def handle(self, *args, **options):
        self.stdout.write("Syncing all task assignments")
        for w in Wizard.objects.filter(auto_assigned=True):
            for user in w.users:
                if not w.is_complete(user):
                    ActionItem.objects.update_or_create(user=user, wizard=w)
