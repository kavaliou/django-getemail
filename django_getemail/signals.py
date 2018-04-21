import django.dispatch

email_imported = django.dispatch.Signal(providing_args=["email", ])
