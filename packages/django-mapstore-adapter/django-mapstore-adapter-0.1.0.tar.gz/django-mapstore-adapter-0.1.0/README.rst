Django MapStore2 Adapter
========================

.. image:: https://www.geo-solutions.it/wp-content/uploads/2014/12/logo_geo-solutions.jpg
   :target: https://www.geo-solutions.it/
   :alt: GeoSolutions

*Django Adapter for MapStore2*

.. image:: https://badge.fury.io/py/django-mapstore-adapter.png?service=github
    :target: http://badge.fury.io/py/django-mapstore-adapter

.. image:: https://travis-ci.org/geosolutions-it/django-mapstore-adapter.png?service=github
   :alt: Build Status
   :target: https://travis-ci.org/geosolutions-it/django-mapstore-adapter

.. image:: https://coveralls.io/repos/github/geosolutions-it/django-mapstore-adapter/badge.svg?branch=master&service=github
   :alt: Coverage Status
   :target: https://coveralls.io/github/geosolutions-it/django-mapstore-adapter?branch=master


If you are facing one or more of the following:
 * TODO,
 * TODO,

TODO

Contributing
------------

We love contributions, so please feel free to fix bugs, improve things, provide documentation. Just `follow the
guidelines <https://django-mapstore-adapter.readthedocs.io/en/latest/contributing.html>`_ and submit a PR.

Requirements
------------

* Python 2.7, 3.4, 3.5, 3.6
* Django 1.11, 2.0

Installation
------------

Install with pip::

    pip install django-mapstore-adapter

Add `mapstore2_adapter` to your `INSTALLED_APPS`

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'mapstore2_adapter',
    )


If you need an OAuth2 provider you'll want to add the following to your urls.py.
Notice that `mapstore2_adapter` namespace is mandatory.

.. code-block:: python

    urlpatterns = [
        ...
        url(r'^o/', include('mapstore2_adapter.urls', namespace='mapstore2_adapter')),
    ]


Changelog
---------

See `CHANGELOG.md <https://github.com/geosolutions-it/django-mapstore-adapter/blob/master/CHANGELOG.md>`_.


Documentation
--------------

The `full documentation <https://django-mapstore-adapter.readthedocs.io/>`_ is on *Read the Docs*.

License
-------

django-mapstore-adapter is released under the terms of the **Simplified BSD license**. Full details in ``LICENSE`` file.
