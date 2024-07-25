Quickstart
==========

Installation
------------

**Requirements**

* Python 3.10 or newer
* Django 4.2+

1. Install from PyPI using ``pip``:

   .. code-block:: bash

      pip install zgw-consumers

2. Add ``zgw_consumers`` and ``simple_certmanager`` to the ``INSTALLED_APPS`` setting.
3. Run ``python src/manage.py migrate`` to create the necessary database tables
4. Configure `django-simple-certmanager <https://django-simple-certmanager.readthedocs.io/en/latest/quickstart.html>`_
   correctly


Usage
-----

In the Django admin, you can create:

* ``Service`` instances to define your external APIs.
* ``NLXConfig`` configuration for your `NLX <https://nlx.io/>`_ outway.

Using ``ape-pie`` to interact with your service
***********************************************

From a service, you can construct an :class:`ape_pie.APIClient` instance
(which is nothing more than an extension to the :class:`requests.Session` object).

.. code-block:: python

    from zgw_consumers.client import build_client
    from zgw_consumers.models import Service

    my_service = Service.objects.get(api_root="https://api.example.com/")
    client = build_client(my_service)

    with client:
        # The preferred way to use the client is within a context manager
        client.get("relative/url")

The resulting client will have certificate and authentication automatically configured from the database configuration.

.. note::

    By default, :func:`zgw_consumers.client.build_client` will return an instance of an :class:`zgw_consumers.nlx.NLXClient`, which will take care of rewriting URLs.
    You can customize this behavior by using the ``client_factory`` argument.

    If you want to customize how configuration is extracted from the :class:`zgw_consumers.models.Service`, you can
    make use of the :class:`zgw_consumers.client.ServiceConfigAdapter` directly.


Constructing an OpenAPI 3 client with the legacy client
*******************************************************

.. deprecated:: 0.28.x

    The legacy client is deprecated and will be removed in the next major release.

    You also need to install the extra ``zds-client``:

    .. code-block:: bash

        pip install zgw-consumers[zds-client]

From a service, you can construct a :class:`zds_client.client.Client`
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

Similar to :meth:`Service.get_client <zgw_consumers.models.Service.get_client>`, you can also invoke :meth:`Service.get_auth_header <zgw_consumers.models.Service.get_auth_header>`:

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
