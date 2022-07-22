.. _settings:

Settings
========

ZGW Consumers is configurable through a number of settings. Each setting has a sane
default.

**General**

``ZGW_CONSUMERS_OAS_CACHE``
    Which cache alias to use from ``settings.CACHES``. OpenAPI specifications are cached
    here after fetching them over HTTP. Defaults to
    ``django.core.cache.DEFAULT_CACHE_ALIAS``.

``ZGW_CONSUMERS_CLIENT_CLASS``
    A dotted python path to the client class to use when building clients from services.
    This class must implement the interface of ``zds_client.Client``. Defaults to
    ``"zgw_consumers.client.ZGWClient"``. For NLX support, you would override this to
    include the ``zgw_consumers.nlx.NLXClientMixin``.

``ZGW_CONSUMERS_TEST_SCHEMA_DIRS``
    A list of directories where OpenAPI schemas can be found. Used by
    ``zgw_consumers.test.mock_service_oas_get`` for mocking OpenAPI schema fetching
    in your tests.

**NLX support**

``NLX_OUTWAY_TIMEOUT``
    Timeout (in seconds) for connecting to the NLX outway during input validation.
    Defaults to ``2``.

``NLX_DIRECTORY_URLS``
    Mapping of NLX directory environments to their (public) URLs. Defaults to the
    directories documented on `nlx.io <https://nlx.io>`_.