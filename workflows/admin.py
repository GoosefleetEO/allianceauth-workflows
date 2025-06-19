"""Admin models"""

from allianceauth.services.admin import ServicesUserAdmin
from .models import Wizard, Check, Step, CheckFilter, ActionItem, StepCompletion

# Django
from django.contrib import admin  # noqa: F401

# Register your models here.


@admin.register(Wizard)
class WizardAdmin(admin.ModelAdmin):
    list_display = ['name', 'comment', 'description', 'permalink', 'auto_assigned']
    filter_horizontal = ['states', 'groups', 'corporations', 'alliances', 'factions', 'characters']


admin.site.register(Step)
admin.site.register(Check)
admin.site.register(CheckFilter)

@admin.register(ActionItem)
class ActionItemAdmin(ServicesUserAdmin):
    search_fields = ServicesUserAdmin.search_fields + ('wizard',)
    list_display = ServicesUserAdmin.list_display + ('wizard', 'completed')

@admin.register(StepCompletion)
class StepCompletionAdmin(ServicesUserAdmin):
    search_fields = ServicesUserAdmin.search_fields + ('wizard','step')
    list_display = ServicesUserAdmin.list_display + ('wizard', 'step')
