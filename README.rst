.. zgw_consumers documentation master file, created by startproject.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ZGW Consumers' documentation!
========================================

:Version: 0.29.0
:Source: https://github.com/maykinmedia/zgw-consumers
:Keywords: OpenAPI, Zaakgericht Werken, Common Ground, NLX

|build-status| |coverage| |linting| |docs|

|python-versions| |django-versions| |pypi-version|

Manage your external API's to consume.

.. contents::

.. section-numbering::

Features
========

* Store services with their configuration in the database
* Integrate with OpenAPI 3.0 specifications
* NLX support
* Declare data/domain objects as modern Python dataclasses

Installation
============

Requirements
------------

* Python 3.10 or newer
* setuptools 30.3.0 or newer
* Django 3.2 or newer


Install
-------

1. Install from PyPI

.. code-block:: bash

    pip install zgw-consumers

2. Add ``zgw_consumers`` and ``simple_certmanager`` to the ``INSTALLED_APPS`` setting.

3. Optionally override ``ZGW_CONSUMERS_CLIENT_CLASS`` to a custom client class.

4. Optionally specify ``ZGW_CONSUMERS_OAS_CACHE`` to point to a separate django cache.
   Defaults to ``django.core.cache.DEFAULT_CACHE_ALIAS``, which is ``default`` in
   practice. For performance reasons we highly recommend to use a real cache backend
   like Redis or Memcache.


Usage
=====

In the Django admin, you can create ``Service`` instances to define your external APIs.

**Client**

To get a client for a given resource, you can use:

.. code-block:: python

    from zgw_consumers.client import build_client
    from zgw_consumers.models import Service

    my_service = Service.objects.get(api_root="https://api.example.com/")
    client = build_client(my_service)

    with client:
        # The preferred way to use the client is within a context manager
        client.get("relative/url")

The resulting client will have certificate and authentication automatically configured from the database configuration.

.. |build-status| image:: https://github.com/maykinmedia/zgw-consumers/workflows/Run%20CI/badge.svg
    :target: https://github.com/maykinmedia/zgw-consumers/actions?query=workflow%3A%22Run+CI%22
    :alt: Run CI

.. |linting| image:: https://github.com/maykinmedia/zgw-consumers/workflows/Code%20quality%20checks/badge.svg
    :target: https://github.com/maykinmedia/zgw-consumers/actions?query=workflow%3A%22Code+quality+checks%22
    :alt: Code linting

.. |coverage| image:: https://codecov.io/gh/maykinmedia/zgw-consumers/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/maykinmedia/zgw-consumers
    :alt: Coverage status

.. |docs| image:: https://readthedocs.org/projects/zgw-consumers/badge/?version=latest
    :target: https://zgw-consumers.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |python-versions| image:: https://img.shields.io/pypi/pyversions/zgw_consumers.svg

.. |django-versions| image:: https://img.shields.io/pypi/djversions/zgw_consumers.svg

.. |pypi-version| image:: https://img.shields.io/pypi/v/zgw_consumers.svg
    :target: https://pypi.org/project/zgw_consumers/
