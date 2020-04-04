from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import *
import logging

logger = logging.getLogger(__name__)

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "publish", "created_by", "created_at")
    list_filter = ('publish', 'created_at', 'parent', )
    fields = (("parent", "name"), "publish")