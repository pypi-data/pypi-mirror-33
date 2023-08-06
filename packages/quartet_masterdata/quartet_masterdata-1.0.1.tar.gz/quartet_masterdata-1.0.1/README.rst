=============================
quartet_masterdata
=============================

.. image:: https://gitlab.com/serial-lab/quartet_masterdata/badges/master/coverage.svg
   :target: https://gitlab.com/serial-lab/quartet_masterdata/pipelines
.. image:: https://gitlab.com/serial-lab/quartet_masterdata/badges/master/build.svg
   :target: https://gitlab.com/serial-lab/quartet_masterdata/commits/master
.. image:: https://badge.fury.io/py/quartet_masterdata.svg
    :target: https://badge.fury.io/py/quartet_masterdata

GS1 CBV 1.2 Implementation for Trade Items and Location Master Data
-------------------------------------------------------------------

Models and APIs to support material, lot and location master data within
QU4RTET as defined in the *GS1 Core Business Vocabulary*.

Geo-Location/History APIs
-------------------------
By cross-referencing BizLocation and other information from the `quartet_epcis`
module, `quartet_masterdata` provides full geo-location (lat, long) by
item by EPCIS event.  This provides the `quartet-ui` interface a mechanism
by which to display mapping and geo-location visual assets.

Documentation
-------------

The full documentation is at https://serial-lab.gitlab.io/quartet_masterdata/

Quickstart
----------
The QU4RTET Master Data module comes pre-configured in the QU4RTET project;
however, if you need to add it to a test installation manually peform the
following:

Install quartet_masterdata::

    pip install quartet_masterdata

Add it to your `INSTALLED_APPS`:

.. code-block:: text

    INSTALLED_APPS = (
        ...
        'quartet_masterdata.apps.QuartetMasterdataConfig',
        ...
    )

Add quartet_masterdata's URL patterns:

.. code-block:: text

    from quartet_masterdata import urls as quartet_masterdata_urls


    urlpatterns = [
        ...
        url(r'^', include(quartet_masterdata_urls)),
        ...
    ]

Features
--------

* GeoLocation APIs
* API and Database Support For Product Master Material
* API and Database Support for

Running Tests
-------------

** REQUIRES PYTHON 3 **

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install -r requirements_test.txt
    (myenv) $ python runtests.py

