"""Admin models"""

from .models import Wizard, Check, Step, CheckFilter, ActionItem, StepCompletion

# Django
from django.contrib import admin  # noqa: F401

# Register your models here.

admin.site.register(Wizard)
admin.site.register(Step)
admin.site.register(Check)
admin.site.register(CheckFilter)
admin.site.register(ActionItem)
admin.site.register(StepCompletion)
