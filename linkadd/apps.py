import sys
from django.apps import AppConfig


class LinkaddConfig(AppConfig):
    name = 'linkadd'
    
    #comment ready method to skip scheduler

    def ready(self):
        if not any(arg in sys.argv for arg in ["migrate", "makemigrations"]):
            from .scheduler import scheduler
            scheduler.start()
