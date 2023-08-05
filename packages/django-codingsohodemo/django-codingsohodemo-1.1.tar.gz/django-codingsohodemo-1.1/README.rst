=====
django-codingsohodemo
=====

django-codingsohodmeo project is demo application  for codingsoho

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "codingsohodemo" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'codingsohodemo',
    ]

2. Include the polls URLconf in your project urls.py like this::

    url(r'^codingsohodemo/', include('codingsohodemo.urls')),

3. Run `python manage.py migrate` to create the codingsohodemo models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a models if needed (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000/codingsohodemo/ to participate in the poll.