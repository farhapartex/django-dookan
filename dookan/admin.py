from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.contenttypes.admin import GenericTabularInline
from dookan.models import *
from dookan.widgets import *
from system.models import *
import logging

logger = logging.getLogger(__name__)
# Register your models here.

def get_site_info():
    try:
        if System.objects.all().count()>0:
            queryset = System.objects.all()[0]
            header_title = queryset.name
            if queryset.logo is not None:
                logo = queryset.logo
            else:
                logo = None
        return (header_title, logo)
    except:
        return ("Dookan", None)



system_info = get_site_info()
admin.site.site_header = system_info[0] + " Admin Panel"
admin.site.index_title = "Dashboard"


class ProductAdminForm(forms.ModelForm):
    model = Product
    class Meta:
        fields = '__all__'
        widgets = {
            'description': HtmlEditor(attrs={'style': 'width: 90%; height: 100%;'}),
        }

class OrderAdminForm(forms.ModelForm):
    model = Order
    class Meta:
        fields = '__all__'
        widgets = {
            'order_note': HtmlEditor(attrs={'style': 'width: 90%; height: 100%;'}),
        }


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "active", "created_at", "action")
    list_display_links = ('action',)
    list_filter = ('code', 'active', 'created_at', )
    fields = (("name", "code"), "active",)
    list_per_page=10

    def action(self, obj):
        return format_html('{}'.format('Edit'))


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "publish", "created_by", "created_at", "action")
    list_display_links = ('action',)
    list_filter = ('publish', 'created_at', 'parent', )
    fields = (("parent", "name"), "publish")
    search_fields = ['name',]
    list_per_page=10

    def action(self, obj):
        return format_html('{}'.format('Edit'))


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "publish", "created_by", "created_at", "action")
    list_display_links = ('action',)
    list_filter = ('publish', 'created_at', 'name', )
    fields = ("name","publish")
    search_fields = ['name']
    list_per_page=10

    def action(self, obj):
        return format_html('{}'.format('Edit'))



@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "created_by", "created_at", "action")
    list_display_links = ('action',)
    list_filter = ('name', 'created_at', )
    list_per_page=10

    def action(self, obj):
        return format_html('{}'.format('Edit'))


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ("product_name", "category", "default_price", "product_key", "publish","action")
    list_display_links = ('action',)
    list_filter = ('category', 'brand', 'material', 'product_type' )
    search_fields = ['name',]
    autocomplete_fields = ['images']
    fieldsets = (
        ("Required Information", {
            "description": "These fields are required for each Product",
            "fields": (
                ('category', 'brand', 'publish'),
                ('name'),
                ('description',),
                ('default_price','quantity', 'product_type'),
                ('images')
            ),
        }),
        ("Optional Information", {
            'classes': ('collapse',),
            'fields': (
                ('model','weight', 'unit','size'),
                ('material','discount_percentage', 'discount_price',),
                ('product_key')
            )
        })
    )
    list_per_page=15

    def product_name(self, obj):
        if len(obj.name) > 20:
            return obj.name[0:20]+"..."
        else:
            return obj.name
    

    def action(self, obj):
        return format_html('{}'.format('Edit'))
    
    product_name.short_description = 'Product Name'


class OrderInline(admin.TabularInline):
    model = Order


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "created_by", "created_at", "action")
    list_display_links = ('action',)
    list_per_page=10
    inlines = [
        OrderInline,
    ]

    def action(self, obj):
        return format_html('{}'.format('Edit'))


    
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "product_name", "quantity", "total_price", "created_by", "created_at", "action")
    fields = (('cart', 'product'), 'quantity',)
    search_fields = ['product__name', 'cart__customer__user__username']
    list_display_links = ('action',)
    list_per_page=10

    def action(self, instance):
        return format_html('{}'.format('Edit'))
    
    def product_name(self, instance):
        return instance.product.name if len(instance.product.name)<=20 else instance.product.name[:20] + "..."

    def total_price(self, instance):
        product = instance.product
        if product.discount_price:
            return product.discount_price * instance.quantity
        else:
            return product.default_price * instance.quantity
    
    total_price.short_description = 'Total Price'
    product_name.short_description = 'Product Name'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm
    list_display = ("id", "cart", "cost", "order_confirm", "payment_status", "order_reference", "created_by", "created_at", "action")
    fieldsets = (
        ("Required Information", {
            "description": "These fields are required for each Product",
            "fields": (
                ('cart', 'payment_method', 'payment_status'),
                ('cost', 'order_reference'),
                ('order_confirm', 'order_received'),
            ),
        }),
        ("Discount Information", {
            "description": "Admin can discount for any order. Admin can use discount field or coupon field for discount",
            'classes': ('collapse',),
            'fields': (
                ('discount', 'coupon'),
                ('order_note')
            )
        })
    )
    list_filter = ('order_confirm', 'payment_status', )
    search_fields = ['cart__customer__user__username', 'order_reference' ]
    readonly_fields=('cost', 'order_reference')
    list_display_links = ('action',)
    list_per_page = 15

    def action(self, instance):
        return format_html('{}'.format('Edit'))



@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    fieldsets = (
        ("General Information", {
            "description": "General information for each Coupon",
            "fields": (
                ('code','amount', 'amount_type'),
                'valid_from', 'valid_until',
            ),
        }),
        ("Coupon Dependency", {
            "description": "You can create coupon for a category or for a brand.",
            'fields': (
                ('category', 'is_brand', 'brand'),
                'active',
            )
        })
    )
    list_display_links = ('action',)
    list_display = ("category", "code", "amount", "amount_type", "valid_from", "valid_until", "active", "action")
    list_filter = ("valid_from", "valid_until")
    search_fields = ['code',]
    list_per_page=10

    def action(self, obj):
        return format_html('{}'.format('Edit'))