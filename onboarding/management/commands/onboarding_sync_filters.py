# from allianceauth-auth-stats

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from ...models import CheckFilter
from ...signals import filters


class Command(BaseCommand):
    help = 'Syncing all the Models from Secure Group Filters'

    def handle(self, *args, **options):
        self.stdout.write("Syncing all the Models from Secure Group Filters")
        for _filter in filters.get_hooks():
            for filter in _filter.objects.all():
                if not CheckFilter.objects.filter(
                        content_type=ContentType.objects.get_for_model(
                            filter).id,
                        object_id=filter.id).exists():
                    CheckFilter.objects.create(filter_object=filter)