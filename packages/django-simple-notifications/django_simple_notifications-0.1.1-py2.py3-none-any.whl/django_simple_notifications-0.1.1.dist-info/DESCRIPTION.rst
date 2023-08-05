=============================
django-simple-notifications
=============================

.. image:: https://travis-ci.org/leonardoo/django-simple-notifications.svg?branch=master
    :target: https://travis-ci.org/leonardoo/django-simple-notifications

.. image:: https://codecov.io/gh/leonardoo/django-simple-notifications/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/leonardoo/django-simple-notifications

A app package for simple notifications for django

Quickstart
----------

Install django-notifications::

    pip install django-simple-notifications

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'simple_notifications.apps.DjNotificationsConfig',
        ...
    )

Add django-simple-notifications's URL patterns:

.. code-block:: python

    from simple_notifications import urls as simple_notifications_urls


    urlpatterns = [
        ...
        url(r'^', include(simple_notifications_urls)),
        ...
    ]


Add django-simple-notifications's to the contexts processors:

.. code-block:: python

    TEMPLATES = [
        {
            ...
            'OPTIONS': {
                'context_processors': [
                    ...
                    "simple_notifications.context_processors.check_user_show_notification"
                ],
            },
        },
    ]

Add to the templates or base html:

.. code-block:: python

    {% include "simple_notifications/alert.html" %}

Features
--------

* TODO

Running Tests
-------------

* TODO

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage




History
-------

0.1.1 (2018-06-19)
++++++++++++++++++

* Bug fix

0.1.0 (2018-06-05)
++++++++++++++++++

* First release on PyPI.


