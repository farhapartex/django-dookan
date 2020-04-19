from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth import get_user_model
import logging, sys, uuid
from .utils import *
# Create your models here.

logger = logging.getLogger(__name__)
USER_MODEL = get_user_model()

"""
Base model is abstract. It is extended by all other models for some default information such as created_at,
created_by, updated_at, updated_by

"""
class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(USER_MODEL, null=True, editable=False,
                                   related_name="%(app_label)s_%(class)s_created", on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(USER_MODEL, null=True, editable=False,
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
    logo = models.ForeignKey("dookan.Media", verbose_name=_("System Logo"), related_name="logos", on_delete=models.SET_NULL, blank=True, null=True)

    def clean(self):
        if not self.id:
            if System.objects.all().count()>0:
                raise ValidationError(_("More than one site information can't be created"), code='invalid')

    def __str__(self):
        return self.name
    

class Customer(Base):
    """docstring for Customer."""
    user = models.OneToOneField(USER_MODEL, verbose_name=_("User"), related_name="customer", on_delete=models.CASCADE)
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
