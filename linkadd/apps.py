from django.apps import AppConfig


class LinkaddConfig(AppConfig):
    name = 'linkadd'
    
    #comment ready method to skip scheduler

    def ready(self):
            from .scheduler import scheduler
            scheduler.start()