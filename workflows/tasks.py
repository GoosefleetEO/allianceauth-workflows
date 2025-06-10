"""App Tasks"""

# Standard Library
import logging

# Third Party
from celery import shared_task

logger = logging.getLogger(__name__)

# Create your tasks here


# Example Task
@shared_task
def example_task():
    """Example Task"""

    pass
