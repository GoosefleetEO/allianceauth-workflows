"""App Configuration"""

# Django
from django.apps import AppConfig

# AA Example App
from onboarding import __version__


class ExampleConfig(AppConfig):
    """App Config"""

    name = "onboarding"
    label = "onboarding"
    verbose_name = f"Example App v{__version__}"
