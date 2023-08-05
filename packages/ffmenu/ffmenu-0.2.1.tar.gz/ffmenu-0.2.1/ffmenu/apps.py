from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules
from .menu import manager


class FFMenuConfig(AppConfig):
    name = 'ffmenu'

    def ready(self):
        autodiscover_modules('menus', register_to=manager)
