import logging

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models.signals import m2m_changed, post_save, pre_delete
from django.dispatch import Signal, receiver

from allianceauth import hooks

from allianceauth.authentication.models import CharacterOwnership, UserProfile

from . import models

from .models import Wizard, ActionItem

# signals go here
logger = logging.getLogger(__name__)

@receiver(m2m_changed, sender=User.groups.through)
def group_trigger(sender, instance, **kwargs):
    if isinstance(instance, User):
        _update_action_items(instance)

@receiver(post_save, sender=CharacterOwnership)
def char_trigger(sender, instance, **kwargs):
    _update_action_items(instance.user)

@receiver(post_save, sender=UserProfile)
def state_trigger(sender, instance, **kwargs):
    _update_action_items(instance.user)

def _update_action_items(user: User):

    assigned_wizards = Wizard.objects.get_user_assigned_wizards(user, True)
    for w in assigned_wizards.all():
        if not w.configured_visibility and user not in w.users:
            ActionItem.objects.filter(user=user,wizard=w).delete()

    new_wizards = Wizard.objects.get_user_autoassigned_wizards(user)
    for w in new_wizards.all():
        if not w.is_complete(user):
            ActionItem.objects.update_or_create(user=user,wizard=w)


# copied from allianceauth-auth-reports
class hook_cache:
    all_hooks = None

    def get_hooks(self):
        if self.all_hooks is None:
            hook_array = set()
            # todo add same functionality to a report source kinds thingo
            _hooks = hooks.get_hooks("secure_group_filters")
            for app_hook in _hooks:
                for filter_model in app_hook():
                    if filter_model not in hook_array:
                        hook_array.add(filter_model)
            self.all_hooks = hook_array
        return self.all_hooks

# copied from allianceauth-auth-reports
filters = hook_cache()

# copied from allianceauth-auth-reports
def new_filter(sender, instance, created, **kwargs):
    try:
        if created:
            models.CheckFilter.objects.create(filter_object=instance)
        else:
            # this is an updated model we dont at this stage care about this.
            pass
    except:
        logger.error("Bah Humbug")  # we failed! do something here

# copied from allianceauth-auth-reports
def rem_filter(sender, instance, **kwargs):
    try:
        models.CheckFilter.objects.get(
            object_id=instance.pk, content_type__model=instance.__class__.__name__
        ).delete()
    except:
        logger.error("Bah Humbug")  # we failed! do something here

# copied from allianceauth-auth-reports
for _filter in filters.get_hooks():
    post_save.connect(new_filter, sender=_filter)
    pre_delete.connect(rem_filter, sender=_filter)
