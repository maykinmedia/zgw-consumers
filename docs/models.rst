Models
======

The models documented here are part of the public API.

Concrete
--------

**Service**

The ``Service`` model is aimed at RESTful services, ideally with an OpenAPI
specification. It supports:

* credentials: ZGW auth (JWT based), API key, basic auth, no auth
* custom/self-signed server certificates
* mutual TLS (client certificate)
* accessing over NLX

.. autoclass:: zgw_consumers.models.Service
   :members:
   :exclude-members: DoesNotExist, MultipleObjectsReturned, clean, save

   .. automethod:: get_service
   .. automethod:: get_client
   .. automethod:: get_auth_header


**Certificate**

The ``Certificate`` model holds your TLS certificates. Files on disk are deleted when
model instances are deleted.

.. autoclass:: zgw_consumers.models.Certificate
   :members:
   :exclude-members: DoesNotExist, MultipleObjectsReturned, clean, save


Abstract
--------

The abstract models are used as base classes for the concrete models - you can use them
to implement your own service types like ``SOAPService``.


.. autoclass:: zgw_consumers.models.abstract.Service
   :members:
   :exclude-members: DoesNotExist, MultipleObjectsReturned, clean, save


.. autoclass:: zgw_consumers.models.abstract.RestAPIService
   :members:
   :exclude-members: DoesNotExist, MultipleObjectsReturned, clean, save
