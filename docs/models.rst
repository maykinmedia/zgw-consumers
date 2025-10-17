Models
======

The models documented here are part of the public API.

Concrete
--------

**Service**

The ``Service`` model is aimed at RESTful services, ideally with an OpenAPI
specification. It supports:

* credentials: ZGW auth (JWT based), API key, basic auth, no auth, OAuth 2.0 client credentials flow
* custom/self-signed server certificates
* mutual TLS (client certificate)
* accessing over NLX

.. autoclass:: zgw_consumers.models.Service
   :members:
   :exclude-members: DoesNotExist, MultipleObjectsReturned, clean, save

   .. automethod:: get_service


Abstract
--------

The abstract models are used as base classes for the concrete models - you can use them
to implement your own service types like ``SOAPService``.


.. autoclass:: zgw_consumers.models.abstract.Service
   :members:
   :exclude-members: DoesNotExist, MultipleObjectsReturned, clean, save
