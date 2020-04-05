from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Media
import logging, sys

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Media)
def media_action(sender, instance, created, **kwargs):
    if created:
        logger.critical("Hello Hasan Working..")

    