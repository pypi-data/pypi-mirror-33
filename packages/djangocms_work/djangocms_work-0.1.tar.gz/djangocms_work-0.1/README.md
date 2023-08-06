=====
DJANGOCMS WORK
=====

DJANGO_CMS WORK is a simple Django app to add your best works for your differents customers.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "djangocms_work" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'djangocms_work',
    ]

2. Include the polls URLconf in your project urls.py like this::

    path('djangocms_work/', include('djangocms_work.urls')),

3. Run `python manage.py migrate` to create the djangocms_work models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a works (you'll need the Admin app enabled).
