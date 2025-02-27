from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings
from django.contrib.auth import get_user_model
from django.forms import ValidationError
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging, sys, uuid
from system.models import Base, User, Customer, Media
# from system.utils import *


# Create your models here.
logger = logging.getLogger(__name__)


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
    code = models.CharField(_("Coupon Code"), max_length=15)
    amount = models.IntegerField()
    amount_type = models.CharField(_("Amount Type"), choices=AMOUNT_TYPE_CHOICES, default='percentage', max_length=15)
    valid_from = models.DateField()
    valid_until = models.DateField()
    active = models.BooleanField(default=True)
    category = models.ForeignKey(Category, related_name="cat_coupons", on_delete=models.SET_NULL, blank=True, null=True)
    is_brand = models.BooleanField(_("Is For Brand?"), default=False, blank=True, null=True)
    brand = models.ForeignKey(Brand, related_name="brand_coupons", on_delete=models.SET_NULL, blank=True, null=True)

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
    discount = models.DecimalField(_("Discount"), max_digits=12, decimal_places=2, blank=True, null=True)
    coupon = models.CharField(_("Coupon"), max_length=15, blank=True, null=True)
    order_note = models.TextField(_("Order Note"),  blank=True, null=True)
    
    def clean(self):
        if self.discount > self.cost:
            raise ValidationError(_("Discount amount can't be greater than total cost"), code='invalid')
        if (self.diccount or self.coupne) and (self.order_note == "" or self.order_note is None):
            raise ValidationError(_("You have to put a order note for a discount"), code='invalid')

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
        
        if self.discount:
            self.cost -= self.discount
        
        if self.coupon:
            queryset = Coupon.objects.all()
            coupon = get_object_or_404(queryset, code=self.coupon)
            
            today = datetime.date.today()
            if coupon.valid_from <= today and coupon.valid_until >= today:
                if coupon.amount_type == "percentage":
                    self.cost -= (self.cost * coupon.amount)/100
                elif coupon.amount_type == "fixed":
                    self.cost -= coupon.amount
            

        super().save(*args, **kwargs)
    

    def __str__(self):
        return self.cart.customer.user.username
    
    class Meta:
         ordering = ['created_at']
         

