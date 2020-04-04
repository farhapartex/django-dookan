from django.urls import path, re_path, include
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from dookan import views as dookan_views

public_router = DefaultRouter()
admin_router = DefaultRouter()

urlpatterns = [
    re_path(r"^public/", include(public_router.urls)),
    re_path(r"^admin/", include(admin_router.urls)),
]