from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig


class DookanConfig(AppConfig):
    name = 'dookan'

    def ready(self):
        from dookan import signals
