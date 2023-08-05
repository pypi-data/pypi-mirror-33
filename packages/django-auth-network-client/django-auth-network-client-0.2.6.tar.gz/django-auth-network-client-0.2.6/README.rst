=============================
Django Auth Network Client
=============================

.. image:: https://badge.fury.io/py/django-auth-network-client.svg
    :target: https://badge.fury.io/py/django-auth-network-client

.. image:: https://travis-ci.org/antoningrele/django-auth-network-client.svg?branch=master
    :target: https://travis-ci.org/antoningrele/django-auth-network-client

.. image:: https://codecov.io/gh/antoningrele/django-auth-network-client/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/antoningrele/django-auth-network-client

Django Auth Network (DAN) is a set of two packages that create Google and Facebook-style authentication, but using your own provider instead of Google or Facebook. This is the client package, and it allows an app to connect to your provider package.

Documentation
-------------

The full documentation is at https://django-auth-network-client.readthedocs.io.

Quickstart
----------

Install Django Auth Network Client::

    pip install django-auth-network-client

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_auth_network_client.apps.DjangoAuthNetworkClientConfig',
        ...
    )

Add Django Auth Network Client's URL patterns:

.. code-block:: python

    from django_auth_network_client import urls as django_auth_network_client_urls


    urlpatterns = [
        ...
        url(r'^', include(django_auth_network_client_urls)),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
