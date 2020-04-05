from django.apps import AppConfig


class DookanConfig(AppConfig):
    name = 'dookan'

    def ready(self):
        from dookan import signals

