from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Media
from .files import rename_image
import logging, sys, os

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Media)
def media_action(sender, instance, created, **kwargs):
    if created:
        image_data = instance.image.name.split("/")
        if instance.title is None or instance.title == "":
            instance.title = image_data[1].split(".")[0]
            if len(instance.title) > 15:
                instance.title = instance.title[0:15]

        instance.image = rename_image(instance.title, instance.image)
    
        # instance.image = rename_image(instance.title,instance.image)
        instance.save()

    