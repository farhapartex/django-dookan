from django.contrib import admin
from django.utils.html import format_html
from dookan.widgets import *
from .models import *

# Register your models here.

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ("title", "image","md_image","sm_image", "created_by", "list_image_tag", "action")
    list_display_links = ('action',)
    list_filter = ('created_at', )
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


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fieldsets = (
        ("General Information", {
            "description": "User General Information",
            "fields": (
                ('first_name', 'last_name', 'username'),
                ('email','avatar'),
                ('is_staff', 'is_active', 'is_superuser')
                
            ),
        }),
        ("User Role & Permission", {
            'fields': (
                ('groups',),'user_permissions'
            )
        }),
        ("Login & Creation Timing", {
            'classes': ('collapse',),
            'fields': (
                ('last_login','date_joined'),
            )
        })
    )
    readonly_fields=('last_login','date_joined')
    list_display = ("id", "full_name", "username", "email", "is_staff", "is_active", "action")
    search_fields = ['first_name', 'last_name', 'username', 'email']
    list_display_links = ('action',)
    list_filter = ('is_staff','created_at', )
    list_per_page=10
    actions = ['inactive_user']
    
    def action(self, obj):
        return format_html('{}'.format('Edit'))

    def full_name(self, obj):
        return obj.get_full_name()
    
    def inactive_user(self, request, queryset):
        queryset.update(is_active=False)
    inactive_user.short_description = "Inactive selected users"

    
class CustomerAdminForm(forms.ModelForm):
    model = Customer
    class Meta:
        fields = '__all__'
        widgets = {
            'billing_address': HtmlEditor(attrs={'style': 'width: 90%; height: 100%;'}),
            'delivery_address': HtmlEditor(attrs={'style': 'width: 90%; height: 100%;'}),
        }

@admin.register(System)
class SystemAdmin(admin.ModelAdmin):
    list_display = ("name", "logo", "created_by", "created_at")
    autocomplete_fields = ['logo']
    

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    form = CustomerAdminForm
    list_display = ("user", "mobile", "active", "created_by", "action")
    list_display_links = ('action',)
    list_filter = ('created_at', )
    search_fields = ['user__username',]
    fields = (("user", "mobile", "active"),  "billing_address","same_address", "delivery_address")
    list_per_page=10

    def action(self, obj):
        return format_html('{}'.format('Edit'))