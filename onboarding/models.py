"""
App Models
Create your models in here
"""

# Django
from django.db import models
from allianceauth.authentication.models import State
from allianceauth.eveonline.models import (EveAllianceInfo, EveCharacter, EveCorporationInfo, EveFactionInfo)
from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from sortedm2m.fields import SortedManyToManyField

class General(models.Model):
    """Meta model for app permissions"""

    class Meta:
        """Meta definitions"""

        managed = False
        default_permissions = ()
        permissions = (("basic_access", "Can access this app"),)

# shamelessly copied straight from allianceauth-secure-groups
class CheckFilter(models.Model):
    class Meta:
        verbose_name = "Smart Filter Binding"
        verbose_name_plural = "Smart Filter Catalog"
        default_permissions = []

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, editable=False
    )
    object_id = models.PositiveIntegerField(editable=False)
    filter_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        try:
            return f"{self.filter_object.name}: {self.filter_object.description}"
        except:  # noqa: E722
            return f"Error: {self.content_type.app_label}:{self.content_type} {self.object_id} Not Found"


class Check(models.Model):
    name = models.CharField(help_text='Name', max_length=32)
    description = models.CharField(help_text='Short description', blank=True, max_length=255)
    filter = models.ForeignKey(CheckFilter, on_delete=models.CASCADE)

    def is_complete(self, user: User):
        return self.filter.filter_object.process_filter(user)

    def is_complete_detail(self, user: User):
        return self.filter.filter_object.audit_filter([user])[user.pk]


    def __str__(self):
        return f"{self.name}: {self.description}"


class Step(models.Model):
    name = models.CharField(help_text='Name', max_length=32)
    description = models.CharField(help_text='Short description', blank=True, max_length=255)
    body = models.TextField(help_text='Body text', blank=True)
    checks = SortedManyToManyField(Check, blank=True)
    is_selfguided = models.BooleanField(help_text="Overrides any Smart Filters assigned to this step.", default=False)

    def is_complete(self, user: User, wizard: 'Wizard'):
        if self.is_selfguided:
            return StepCompletion.objects.filter(user=user, step=self, wizard=wizard).exists()

        result = True
        for check in self.checks.all():
            result = result and check.is_complete(user)

        return result

    def pct_complete(self, user:User, wizard: 'Wizard'):
        if self.is_selfguided:
            return int(self.is_complete(user, wizard))

        if self.checks.count() == 0:
            return 1

        passed = 0
        total = 0
        for check in self.checks.all():
            if check.is_complete(user):
                passed += 1
            total += 1

        return passed / total

    def __str__(self):
        return f"{self.name}: {self.description}"

class Wizard(models.Model):
    
    name = models.CharField(help_text='Name', max_length=32)
    description = models.CharField(help_text='Short description', blank=True, max_length=255)
    permalink = models.SlugField(help_text='user friendly permalink slug',blank=True,null=True)
    body = models.TextField(help_text='Body text', blank=True)

    states = models.ManyToManyField(
        State,
        blank=True,
        help_text="States that can access this wizard."

    )

    groups = models.ManyToManyField(
        Group,
        blank=True,
        help_text="Groups that can access this wizard."
    )

    characters = models.ManyToManyField(
        EveCharacter,
        blank=True,
        help_text="Characters that can access this wizard."
    )

    corporations = models.ManyToManyField(
        EveCorporationInfo,
        blank=True,
        help_text="Corporations that can access this wizard."
    )

    alliances = models.ManyToManyField(
        EveAllianceInfo,
        blank=True,
        help_text="Alliances that can access this wizard."
    )

    factions = models.ManyToManyField(
        EveFactionInfo,
        blank=True,
        help_text="Factions that can access this wizard."
    )
    
    steps = SortedManyToManyField(Step)
    
    @property
    def users(self):
        state_users = User.objects.filter(profile__state__in=self.states.all())
        group_users = User.objects.filter(groups__in=self.groups.all())

        corp_ids = []
        for corp in self.corporations.all():
            corp_ids.append(corp.corporation_id)
        corp_users = User.objects.filter(character_ownerships__character__corporation_id__in=corp_ids)

        
        alliance_ids = []
        for alliance in self.alliances.all():
            alliance_ids.append(alliance.alliance_id)
        alliance_users = User.objects.filter(character_ownerships__character__alliance_id__in=alliance_ids)
        
        faction_ids = []
        for faction in self.factions.all():
            faction_ids.append(faction.faction_id)
        faction_users = User.objects.filter(character_ownerships__character__faction_id__in=faction_ids)
        
        return state_users | group_users | corp_users | alliance_users | faction_users

    def is_complete(self, user: User):
        result = True
        for step in self.steps.all():
            result = result and step.is_complete(user, self)

        return result

    def pct_complete(self, user:User):
        if self.steps.count() == 0:
            return 1

        passed = 0
        total = 0
        for step in self.steps.all():
            passed += step.pct_complete(user, self)
            total += 1

        return passed / total

    def __str__(self):
        return f"{self.name}: {self.description}"

class StepCompletion(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    wizard = models.ForeignKey(Wizard,on_delete=models.CASCADE)
    step = models.ForeignKey(Step,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}: {self.wizard.name}: {self.step.name}"

class ActionItem(models.Model):
    wizard = models.ForeignKey(Wizard,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}: {self.wizard.name}"
