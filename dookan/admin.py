from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import *
from .widgets import *
import logging

logger = logging.getLogger(__name__)

# Register your models here.

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ("title", "image","md_image","sm_image", "created_by", "list_image_tag", "action")
    list_display_links = ('action',)
    search_fields = ['title',]
    fieldsets = (
        ("Required Information", {
            "description": "These fields are required for each Media",
            "fields": (
                ('title',),
                ('image', 'image_tag'),
            ),
        }),
        ("Optional Information", {
            'classes': ('collapse',),
            'fields': (
                ('md_image','sm_image'),
            )
        })
    )
    readonly_fields = ('image_tag',)
    list_per_page=10
    

    def image_tag(self, obj):
        return format_html('<img src="{}" width="160" height="135"/>'.format(obj.image.url))
    
    def list_image_tag(self, obj):
        return format_html('<img src="{}" width="75" height="50"/>'.format(obj.sm_image.url))
    
    def action(self, obj):
        return format_html('{}'.format('Edit'))

    image_tag.short_description = 'Image'
    list_image_tag.short_description = 'Image Preview'


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("user", "active", "created_by", "created_at", "action")
    list_display_links = ('action',)
    list_filter = ('created_at', )
    fields = (("user", "active"), "billing_address","same_address", "delivery_address")
    list_per_page=10

    def action(self, obj):
        return format_html('{}'.format('Edit'))


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


class ProductAdminForm(forms.ModelForm):
    model = Product
    class Meta:
        fields = '__all__'
        widgets = {
            'description': HtmlEditor(attrs={'style': 'width: 90%; height: 100%;'}),
        }


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



@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    fields = (('category', 'code'), ('amount', 'amount_type'), ('valid_from',), 'valid_until', 'active',)
    list_display_links = ('action',)
    list_display = ("category", "code", "amount", "amount_type", "valid_from", "valid_until", "active", "action")
    list_filter = ("category", "code", "valid_from", "valid_until")

    def action(self, obj):
        return format_html('{}'.format('Edit'))