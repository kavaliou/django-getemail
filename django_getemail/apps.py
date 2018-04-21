from django.apps import AppConfig


class EmailReceiverConfig(AppConfig):
    name = 'django_getemail'

    def ready(self):
        import django_getemail.signals
