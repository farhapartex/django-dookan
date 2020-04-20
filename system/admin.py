from django.contrib import admin
from django.utils.html import format_html
from dookan.widgets import *
from .models import *

# Register your models here.

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