=============================
django-genomix-workflows
=============================

.. image:: https://badge.fury.io/py/django-genomix-workflows.svg
    :target: https://badge.fury.io/py/django-genomix-workflows

.. image:: https://travis-ci.org/fullrobot/django-genomix-workflows.svg?branch=develop
    :target: https://travis-ci.org/fullrobot/django-genomix-workflows

.. image:: https://codecov.io/gh/fullrobot/django-genomix-workflows/branch/develop/graph/badge.svg
    :target: https://codecov.io/gh/fullrobot/django-genomix-workflows

.. image:: https://pyup.io/repos/github/fullrobot/django-genomix-workflows/shield.svg
     :target: https://pyup.io/repos/github/fullrobot/django-genomix-workflows/
     :alt: Updates

.. image:: https://pyup.io/repos/github/fullrobot/django-genomix-workflows/python-3-shield.svg
      :target: https://pyup.io/repos/github/fullrobot/django-genomix-workflows/
      :alt: Python 3

Django App for storing Workflows and Tracking

Documentation
-------------

The full documentation is at https://django-genomix-workflows.readthedocs.io.

Quickstart
----------

Install django-genomix-workflows::

    pip install django-genomix-workflows

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'genomix_workflows',
        ...
    )

Add django-genomix-workflows's URL patterns:

.. code-block:: python

    from genomix_workflows import urls as genomix_workflows_urls


    urlpatterns = [
        ...
        url(r'^', include(genomix_workflows_urls, namespace='genomix_workflows')),
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
