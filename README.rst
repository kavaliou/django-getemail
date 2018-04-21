=====
Django-Getemail
=====

Getemail is a simple Django app to get emails from Gmail.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "polls" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'django_getemail',
    ]

2. Run `python manage.py migrate` to create the emails models.

3. Start the development server and visit http://127.0.0.1:8000/admin/
   to create an email (you'll need the Admin app enabled).

