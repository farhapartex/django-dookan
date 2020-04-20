from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings
from django.contrib.auth import get_user_model
from django.forms import ValidationError
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging, sys, uuid
from system.models import Base, Customer
from system.utils import *
from .files import *
from .media import DynamicImageResize


# Create your models here.
logger = logging.getLogger(__name__)
USER_MODEL = get_user_model()

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
        return self.title


class PaymentMethod(Base):
    name = models.CharField(_("Payment Method"), max_length=50)
    code = models.CharField(_("Code"), max_length=50)
    active = models.BooleanField(_("Active"), default=True)

    def __str__(self):
        return self.name
    
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
    product_key = models.CharField(_("Product Key"), max_length=40, blank=True, null=True)
    publish = models.BooleanField(_("Publish"), default=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.discount_percentage:
            discount_amount = round((self.default_price * self.discount_percentage)/100)
            self.discount_price = self.default_price-discount_amount
        
        if not self.product_key:
            self.product_key = uuid.uuid4()

        return super().save(*args, **kwargs)


AMOUNT_TYPE_CHOICES = (('percentage', 'Percentage'), ('fixed', 'Fixed'))
class Coupon(Base):
    category = models.ForeignKey(Category, related_name="coupons", on_delete=models.CASCADE)
    code = models.CharField(_("Coupon Code"), max_length=15)
    amount = models.IntegerField()
    amount_type = models.CharField(_("Amount Type"), choices=AMOUNT_TYPE_CHOICES, default='percentage', max_length=15)
    valid_from = models.DateField()
    valid_until = models.DateField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code
        

class Cart(Base):
    customer = models.ForeignKey(Customer, verbose_name=_("User"), related_name="cart_users", on_delete=models.CASCADE)
    products = models.ManyToManyField(Product,through='CartItem',through_fields=('cart', 'product'), verbose_name=_("Items"))

    def __str__(self):
        return self.customer.user.username + str(self.id)
    

class CartItem(Base):
    cart = models.ForeignKey(Cart, verbose_name=_("Cart"), related_name="cart_items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name=_("Product"),  on_delete=models.CASCADE)
    quantity = models.IntegerField(_("Quantity"))

    def __str__(self):
        return self.cart.customer.user.username


PAYMENT_STATUS_CHOICES = (('paid','Paid'), ('half-paid', 'Half Paid'), ('not-paid', 'Not Paid'))
class Order(Base):
    cart = models.ForeignKey(Cart, related_name="orders", on_delete=models.CASCADE)
    cost = models.DecimalField(_("Total Price"), max_digits=12, decimal_places=2, default=0, null=True)
    order_confirm = models.BooleanField(_("Is Order Confirm?"), default=False)
    payment_method = models.ForeignKey(PaymentMethod, related_name="order_payments", on_delete=models.SET_NULL, blank=True, null=True)
    payment_status = models.CharField(_("Payment Status"), choices=PAYMENT_STATUS_CHOICES, max_length=20)
    order_received = models.BooleanField(_("Is Order Received?"), default=False)
    order_reference = models.CharField(_("Order Reference"), max_length=40, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.order_reference is None or self.order_reference == "":
            self.order_reference = uuid.uuid4()

        if self.cost is None or self.cost == 0:
            items = self.cart.cart_items.all()
            for item in items:
                if item.product.discount_price:
                    price = item.product.discount_price * item.quantity
                else:
                    price = item.product.default_price * item.quantity
                
                self.cost += price

        super().save(*args, **kwargs)
    

    def __str__(self):
        return self.cart.customer.user.username
    
    class Meta:
         ordering = ['created_at']

