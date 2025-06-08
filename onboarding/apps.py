"""App Configuration"""

# Django
from django.apps import AppConfig

# AA Example App
from onboarding import __version__


class OnboardingConfig(AppConfig):
    """App Config"""

    name = "onboarding"
    label = "onboarding"
    verbose_name = f"Onboarding Wizards v{__version__}"

    def ready(self):
        import onboarding.signals
