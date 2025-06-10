"""App Configuration"""

# Django
from django.apps import AppConfig

# AA Example App
from workflows import __version__


class OnboardingConfig(AppConfig):
    """App Config"""

    name = "workflows"
    label = "workflows"
    verbose_name = f"Workflows v{__version__}"

    def ready(self):
        import workflows.signals
