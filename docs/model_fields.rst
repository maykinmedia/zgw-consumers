Model fields
============

ZGW Consumers provides custom model fields to help with external API's usage.

ServiceUrlField
---------------

``ServiceUrlField`` handles storage and access to the external urls.

If you need to store external API urls in the database and you already use ``zgw_consumers.Serivce`` model
consider using ``ServiceUrlField`` instead of regular Django ``UrlField``. ``ServiceUrlField`` separates
url into base and relative parts and stores them in two database fields:

* ``ForeignKey`` field to ``Service`` model for the base part.
* ``CharField`` for the relative part.

``ServiceUrlField`` provides same Python API as regular Django model field and can be used in querysets.
The DRF serializer is included and picked up automatically.


Usage
*****

For example you have a case which type is defined in the external API "Casetypes".
The credentials to access this API are already stored in the ``Service`` model:

.. code-block:: python

    >>> from zgw_consumers.models import Service
    >>> Service.objects.create(api_root="http://example.org/casetypes/", api_type="orc", auth_type="no_auth")
    <Service: [ORC (Overige)] >


Let's use ``ServiceUrlField`` to store the case type:

.. code-block:: python

    # models.py

    from django.db import models

    from zgw_consumers.models import ServiceUrlField


    # set up for ServiceUrl test
    class Case(models.Model):
        _casetype_api = models.ForeignKey("zgw_consumers.Service", on_delete=models.CASCADE)
        _casetype_relative = models.CharField(max_length=200)
        casetype = ServiceUrlField(base_field="_casetype_api", relative_field="_casetype_relative")


Now you can use ``Case.casetype`` as a regular ``UrlField`` for both accessing and setting the data.

.. code-block:: python

    >>> case = Case.objects.create(casetype="http://example.org/casetypes/path/to/casetype/1")  # store casetype
    >>> case.casetype  # access casetype
    'http://example.org/casetypes/path/to/casetype/1'
    >>> case._casetype_api  # base part of the url is stored as a FK to Service
    <Service: [ORC (Overige)] >
    >>> case._casetype_relative  # relative part of url is stored as a string
    'path/to/casetype/1'


If the base part of the URL is not found in the Service model ``ValueError`` will be raised.

.. code-block:: python

    >>> other_case = Case.objects.create(casetype="http://example.org/other-casetypes/path/to/casetype/1")
    Traceback (most recent call last):
    ValueError: The base part of url is not found in 'Service' data


Rest Django Framework
*********************

A serializer field for ``ServiceUrlField`` is provided and loaded automatically. It includes ``ServiceValidator``
which checks is the base part of url is found in the ``Service`` model and raises validation error otherwise.

