from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q

class WizardManager(models.Manager):

    def get_user_assigned_wizards(self, user: User):
        return self.filter(actionitem__user = user, actionitem__completed = False)

    def get_user_autoassigned_wizards(self, user: User):
        result = self.get_user_wizards(user)
        return result.filter(auto_assigned = True).exclude(actionitem__user = user);

    def get_user_wizards(self, user: User):
        assigned_wizards = Q(actionitem__user = user)

        state_wizards = Q(states = user.profile.state)

        group_wizards = Q(groups__in = user.groups.all())

        alliance_ids = []
        corp_ids = []
        char_ids = []
        faction_ids = []

        for c in user.character_ownerships.all():
            if c.character.alliance_id:
                alliance_ids.append(c.character.alliance_id)
            if c.character.faction_id:
                faction_ids.append(c.character.faction_id)

            corp_ids.append(c.character.corporation_id)
            char_ids.append(c.character.character_id)

        alliance_wizards = Q(alliances__alliance_id__in = alliance_ids)
        corp_wizards = Q(corporations__corporation_id__in = corp_ids)
        char_wizards = Q(characters__character_id__in = char_ids)
        faction_wizards = Q(factions__faction_id__in = faction_ids)

        return self.filter(assigned_wizards | state_wizards | group_wizards | alliance_wizards | corp_wizards | char_wizards | faction_wizards).distinct()
