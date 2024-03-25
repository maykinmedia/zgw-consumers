.. _settings:

Settings
========

ZGW Consumers is configurable through a number of settings. Each setting has a sane
default.

**General**

``ZGW_CONSUMERS_IGNORE_OAS_FIELDS``
    If set to ``True``, the OAS URL/file fields in the admin are hidden/ignored. Keep
    the default value of ``False`` when you still make use of ``zgw_consumers.legacy``.

``ZGW_CONSUMERS_OAS_CACHE``
    Which cache alias to use from ``settings.CACHES``. OpenAPI specifications are cached
    here after fetching them over HTTP. Defaults to
    ``django.core.cache.DEFAULT_CACHE_ALIAS``.

    .. deprecated:: 0.31.x
        Support for gemma-zds-client and thus OpenAPI schemas is deprecated and will
        be removed in 1.0.

``ZGW_CONSUMERS_CLIENT_CLASS``
    A dotted python path to the client class to use when building clients from services.
    This class must implement the interface of :class:`zds_client.client.Client`. Defaults to
    ``"zgw_consumers.legacy.client.ZGWClient"``. For NLX support, you would override this to
    include the ``zgw_consumers.legacy.nlx.NLXClientMixin``.

    .. deprecated:: 0.28.x
       The ``ZGWClient`` is deprecated and will be removed in the next major release. Instead,
       use the new :class:`ape_pie.client.APIClient` or :class:`zgw_consumers.nlx.NLXClient`.

``ZGW_CONSUMERS_TEST_SCHEMA_DIRS``
    A list of directories where OpenAPI schemas can be found. Used by
    ``zgw_consumers.test.mock_service_oas_get`` for mocking OpenAPI schema fetching
    in your tests.

    .. deprecated:: 0.31.x
        Support for gemma-zds-client and thus OpenAPI schemas is deprecated and will
        be removed in 1.0.

**NLX support**

``NLX_OUTWAY_TIMEOUT``
    Timeout (in seconds) for connecting to the NLX outway during input validation.
    Defaults to ``2``.

``NLX_DIRECTORY_URLS``
    Mapping of NLX directory environments to their (public) URLs. Defaults to the
    directories documented on `nlx.io <https://nlx.io>`_.
