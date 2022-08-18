Quickstart
==========

Installation
------------

**Requirements**

* Python 3.7 or newer
* Django 3.2+

1. Install from PyPI using ``pip``:

   .. code-block:: bash

      pip install zgw-consumers

2. Add ``zgw_consumers`` to the ``INSTALLED_APPS`` setting.
3. Run ``python src/manage.py migrate`` to create the necessary database tables
4. Configure `django-privates <https://django-privates.readthedocs.io/en/latest/quickstart.html>`_
   correctly


Usage
-----

In the Django admin, you can create:

* ``Service`` instances to define your external APIs.
* ``NLXConfig`` configuration for your `NLX <https://nlx.io/>`_ outway.

Constructing an OpenAPI 3 client
********************************

From a service, you can construct a `client <https://pypi.org/project/gemma-zds-client/>`_
instance which is driven by the API schema. There are two common scenario's:

**If you know upfront which service you need to consume**

Example snippet:

.. code-block:: python

    from zgw_consumers.models import Service

    my_service = Service.objects.get(api_root="https://api.example.com/")
    client = my_service.build_client()
    resource = client.retrieve("resource", uuid="6d166c39-74bf-4cf4-903d-f99fbb1670ac")

**If you are given a resource URL and need the appropriate client**

In this situation, you don't necessarily know upfront which service you will need,
since the resource URL may be from various services. You can obtain the service and/or
client directly based on the URL and the best ``api_root`` match:

.. code-block:: python

    from zgw_consumers.models import Service

    client = Service.get_client(resource_url)
    resource = client.retrieve("resource", url=resource_url)


Obtaining the authentication details
************************************

Similar to ``Service.get_client``, you can also invoke ``Service.get_auth_header``:

.. code-block:: python

    from zgw_consumers.models import Service

    auth = Service.get_auth_header(resource_url)

Data model
**********

Use ``zgw_consumers.api_models.base.factory`` to turn raw JSON responses into instances
of domain models:

.. code-block:: python

    from zgw_consumers.api_models.base import factory
    from zgw_consumers.api_models.zaken import Zaak

    results = client.list("zaak")["results"]

    return factory(Zaak, results)

It works for both collections and scalar values, and takes care of the camelCase to
snake_case conversion.

You can also define your own data models, take a look at the ``zgw_consumers.api_models``
package for inspiration.
