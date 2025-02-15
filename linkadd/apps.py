import sys
from django.apps import AppConfig


class LinkaddConfig(AppConfig):
    name = 'linkadd'
    
    #comment ready method to skip scheduler

    def ready(self):
        if "runserver" in sys.argv:
            from .scheduler import scheduler
            scheduler.start()
