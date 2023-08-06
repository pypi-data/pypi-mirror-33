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




History
-------

0.1.0 (2018-01-12)
++++++++++++++++++

* First release on PyPI.

0.2.0 (2018-06-27)
++++++++++++++++++

* Changed models completely.
* Add graph interpretations for workflows.
* Add signal to automatically create task instances after workflow instance initiation.
* Add signals to update related task status after task updates.
* Add methods for single workflow/task instances to get current status, graph, JSON graph, and other useful helpers.
* Add managers for combined workflow and task methods.
* Add single and combined graph diagram, current status, and topographical sort to Django Admin.
* Complete the switch to Django 2.0
* Update requirements and dependencies.

0.2.1 (2018-07-02)
++++++++++++++++++

* Add raw id in Admin for workflow instance parent field

0.2.2 (2018-07-03)
++++++++++++++++++

* Add raw id in Admin for Task instance

0.2.3 (2018-07-06)
++++++++++++++++++

* Fix an issue with next and previous task instances

0.2.4 (2018-07-08)
++++++++++++++++++

* Improve combined Next and Previous calculations


