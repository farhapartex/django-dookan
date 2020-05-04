from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import logging, sys, uuid
from .utils import *
from system.files import *
from system.media import DynamicImageResize
# Create your models here.

logger = logging.getLogger(__name__)

"""
Base model is abstract. It is extended by all other models for some default information such as created_at,
created_by, updated_at, updated_by
"""

class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("system.User", null=True, editable=False,
                                   related_name="%(app_label)s_%(class)s_created", on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey("system.User", null=True, editable=False,
                                   related_name="%(app_label)s_%(class)s_updated", on_delete=models.CASCADE)
    

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and user.is_authenticated:
            self.updated_by = user
            if self._state.adding:
                self.created_by = user
        super(Base, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class System(Base):
    name = models.CharField(_("System Name"), max_length=50)
    logo = models.ForeignKey("system.Media", verbose_name=_("System Logo"), related_name="logos", on_delete=models.SET_NULL, blank=True, null=True)

    def clean(self):
        if not self.id:
            if System.objects.all().count()>0:
                raise ValidationError(_("More than one site information can't be created"), code='invalid')

    def __str__(self):
        return self.name
    

class Media(Base):
    title = models.CharField(_("Image Title"), max_length=50, blank=True, null=True)
    image = models.ImageField(_("Image"), storage=fs,upload_to=image_upload_path)
    md_image = models.ImageField(_("Medium Image"), storage=fs,upload_to=md_image_upload_path, blank=True, null=True)
    sm_image = models.ImageField(_("Small Image"), storage=fs,upload_to=sm_image_upload_path, blank=True, null=True)

    def save(self, *args, **kwargs):
        try:
            # get image size from settings.py file
            md_size = settings.MID_IMAGE_SIZE
            sm_size = settings.SM_IMAGE_SIZE
        except :
            # if no size get from settings.py, default size will be this
            md_size = (768,1024)
            sm_size = (265, 300)

        if not self.md_image:
            self.md_image = DynamicImageResize(md_size, self.image).get_resize_image()
        if not self.sm_image:
            self.sm_image = DynamicImageResize(sm_size, self.image).get_resize_image()

        super(Media, self).save(*args, **kwargs)
    
    def __str__(self):
        try:
            return self.title
        except:
            return "Media "+ str(self.id)


class User(AbstractUser, Base):
    email = models.EmailField(_('email address'), blank=True, unique=True)
    avatar = models.ForeignKey(Media, related_name="profile_images", on_delete=models.SET_NULL, blank=True, null=True)
    
    def __str__(self):
        return self.username

class Customer(Base):
    """docstring for Customer."""
    user = models.OneToOneField(User, verbose_name=_("User"), related_name="customer", on_delete=models.CASCADE)
    mobile = models.CharField(_("Mobile Number"), null=True, max_length=20)
    billing_address = models.TextField(_("Shipping Address"))
    same_address = models.BooleanField(_("Same address for delivery?"))
    delivery_address = models.TextField(_("Delivery Address"), blank=True, null=True)
    active = models.BooleanField(_("ACtive"), default=True)

    def save(self, *args, **kwargs):
        if self.same_address is True or self.delivery_address is None:
            self.delivery_address = self.billing_address

        return super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username
