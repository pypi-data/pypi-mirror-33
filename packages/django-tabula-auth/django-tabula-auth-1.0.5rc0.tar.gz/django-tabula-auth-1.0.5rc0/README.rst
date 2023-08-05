=====
Tabula Auth
=====

Tabula Auth is a django authorization by Phone Number used in TabulaRassa products
Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "polls" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'tabula_auth',
    ]

2. Include the polls URLconf in your project urls.py like this::

    path('auth/', include(('tabula_auth.urls', 'tabula_auth'),
                              namespace='tabula_auth')),

3. Run `python manage.py migrate` to create the polls models.

