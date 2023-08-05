QU4RTET EPCIS
=============

.. image:: https://gitlab.com/serial-lab/quartet_epcis/badges/master/pipeline.svg
        :target: https://gitlab.com/serial-lab/quartet_epcis/commits/master

.. image:: https://gitlab.com/serial-lab/quartet_epcis/badges/master/coverage.svg
        :target: https://gitlab.com/serial-lab/quartet_epcis/pipelines

.. image:: https://badge.fury.io/py/quartet_epcis.svg
    :target: https://badge.fury.io/py/quartet_epcis

The quartet_epcis python package is a Django application that
contains the base database models necessary for the support of
EPCIS 1.2 data persistence to an RDBMS. The quartet_epcis.parsing
package contains an EPCIS XML parser that will take an input stream
of XML data and save it to a configured database back-end.

The quartet_epcis.app_models directory contains a set of
Django ORM models that are used to define the database scheme
and store EPCIS data in the database.

Documentation
-------------

Find the latest docs here:

https://serial-lab.gitlab.io/quartet_epcis/


The full (pre-built )documentation is under the docs directory in this project.

Quickstart
----------

Install QU4RTET EPCIS
---------------------

.. code-block:: text

    pip install quartet_epcis


Add it to your `INSTALLED_APPS`:

.. code-block:: text

    INSTALLED_APPS = (
        ...
        'quartet_epcis',
        ...
    )


Features
--------

* Maintains the database schema for EPCIS 1.2 support.
* Parses EPCIS 1.2 XML streams to the configured backend database system.
* Enforces business rules around decommissioning, commissioning, aggregation,
disaggregation, etc.

Running The Unit Tests
----------------------

.. code-block:: text

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install -r requirements_test.txt
    (myenv) $ python runtests.py





History
-------

0.1.0 (2017-12-07)
++++++++++++++++++

* First release on PyPI.

1.0.+ May 4, 2018
++++++++++++++++++

* First production-ready release.
* CI build to auto-deploy tags to PyPI
* Longer fields for document and event ids.
* Changes to CI build.
* Data migration to automatically create EPCIS rule and Step.

1.0.4 June 6, 2018
++++++++++++++++++

* EPCISParsingStep in the steps module was of wrong Type...but was working
anyway.  Switched to `rule.Step` from `models.Step`.
* Added on_failure to the EPCISParsingStep to account for the new abstract
method on the base `quartet_capture.rules.Step` class.

1.1 June 21 2018
++++++++++++++++
* Addition of new business parser for EPCIS.  The business parser inherits
from the original `quartet_epcis.parsing.parser.QuartetParser` and adds
additional business context processing.  The new parser will perform and
track explicit aggregation and dissagregation functions as well as maintain
records of deleted/decommissioned events and check for events containing
EPCs that were never commissioned.  Over 800 lines of unit testing code along
with 30 tests now cover just the quartet_epcis parsers and API.


