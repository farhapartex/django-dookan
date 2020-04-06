from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings
from django.contrib.auth import get_user_model
from django.forms import ValidationError
from django.utils.text import slugify
import logging, sys
from .utils import *
from .files import *
from .media import DynamicImageResize


from django.db.models.signals import post_save
from django.dispatch import receiver

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
        return self.image.name


class Category(Base):
    """docstring for Category."""
    name = models.CharField(_("Category Name"), max_length=55)
    parent = models.ForeignKey("self", verbose_name=_("Parent"), related_name="children", on_delete=models.CASCADE, blank=True, null=True)
    publish = models.BooleanField(_("Publish"), default=True)

    def __str__(self):
        return self.name
    
    class Meta:
        """docstring for Meta."""
        verbose_name_plural = "Categories"



class Brand(Base):
    name = models.CharField(_("Brand Name"), max_length=50)
    publish = models.BooleanField(_("Publish"), default=True)

    def __str__(self):
        return self.name


class ProductType(Base):
    name = models.CharField(_("Product Type"), max_length=50)

    def __str__(self):
        return self.name


UNIT_CHOICES = (('kg','KG'),('gm','GM'),('mg','MG'),('m','Meter'),('cm','Centimeter'),('mm','Millimeter'))
SIZE_CHOICE = (('s','Small'), ('m','Medium'), ('l','Large'), ('xl','Extra Large'),('xxl','Double Extra Large'))

class Product(Base):
    name = models.CharField(_("Product Name"), max_length=150)
    description = models.TextField(_("Product Description"))
    category = models.ForeignKey(Category, verbose_name=_("Product Category"), on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, verbose_name=_("Brand"), related_name="products", on_delete=models.CASCADE)
    product_type = models.ForeignKey(ProductType, verbose_name=_("Product Type"), related_name="type_products", on_delete=models.SET_NULL, blank=True, null=True)
    model = models.CharField(_("Product Model"), max_length=100, blank=True, null=True)
    weight = models.DecimalField(_("Weight"), max_digits=10, decimal_places=2, blank=True, null=True)
    unit = models.CharField(_("Unit"),choices=UNIT_CHOICES, max_length=50, blank=True, null=True)
    material = models.CharField(_("Material"), max_length=80, blank=True, null=True)
    size = models.CharField(_("Size"),choices=SIZE_CHOICE, max_length=50, blank=True, null=True)
    default_price = models.DecimalField(_("Default Price"), max_digits=12, decimal_places=2)
    discount_percentage = models.IntegerField(_("Discount Percentage"), blank=True, null=True)
    discount_price = models.DecimalField(_("Discount Price"), max_digits=12, decimal_places=2,blank=True, null=True)
    quantity = models.IntegerField(_("Quantity"), default=1)
    images = models.ManyToManyField(Media, verbose_name=_("Product Images"))
    product_key = models.CharField(_("Product Key"), max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name

        
