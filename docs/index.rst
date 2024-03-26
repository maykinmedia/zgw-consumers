ZGW Consumers
=============

|build-status| |coverage| |linting|

|python-versions| |django-versions| |pypi-version|

ZGW Consumers allows you to manage your external services through the Django admin.

Features
--------

* Store services with their configuration in the database
* Built in `ape-pie <https://pypi.org/project/ape-pie/>`_ API client adapter
* NLX support
* Declare data/domain objects as modern Python dataclasses

Developed for use in Dutch government software where data exchange with external
services is run of the mill, this library provides flexibility in configuring your
environment(s).

ZGW Consumers allows you to centralize the location, credentials, API schema information... to
connect to HTTP-based services. There is first class support for OpenAPI 3
specifications, but you are not limited to "modern" RESTful services! SOAP/XML services
can still leverage the utilities offered by ZGW Consumers.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   settings
   recipes
   models
   model_fields
   drf
   testing
   reference
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`



.. |build-status| image:: https://github.com/maykinmedia/zgw-consumers/workflows/Run%20CI/badge.svg
    :target: https://github.com/maykinmedia/zgw-consumers/actions?query=workflow%3A%22Run+CI%22
    :alt: Run CI

.. |linting| image:: https://github.com/maykinmedia/zgw-consumers/workflows/Code%20quality%20checks/badge.svg
    :target: https://github.com/maykinmedia/zgw-consumers/actions?query=workflow%3A%22Code+quality+checks%22
    :alt: Code linting

.. |coverage| image:: https://codecov.io/gh/maykinmedia/zgw-consumers/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/maykinmedia/zgw-consumers
    :alt: Coverage status

.. |python-versions| image:: https://img.shields.io/pypi/pyversions/zgw_consumers.svg

.. |django-versions| image:: https://img.shields.io/pypi/djversions/zgw_consumers.svg

.. |pypi-version| image:: https://img.shields.io/pypi/v/zgw_consumers.svg
    :target: https://pypi.org/project/zgw_consumers/
