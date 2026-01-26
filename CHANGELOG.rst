Changes
=======

1.1.2 (2026-01-26)
-------------------

Patch release.

* [#124] Fixed crash in connection check when the OAUTH2 configuration is broken.
* Fixed CI configuration issue that would install Django 6 instead of 5.2.

1.1.1 (2025-11-20)
-------------------

Patch release.

* Switch to the updated Utrecht NLX directory URLs. The ``NLX_DIRECTORY_URLS`` defaults
  have been updated and can still be overridden in project settings. They can also be
  overridden with environment variables:

  * ``NLX_DIRECTORY_URL_DEMO`` (default: ``https://nlx-directory-ui.commonground.acc.utrecht.nl/``)
  * ``NLX_DIRECTORY_URL_PROD`` (default: ``https://nlx-directory-ui.commonground.utrecht.nl/``)

1.1.0 (2025-10-17)
-------------------

Feature release that provides OAuth 2.0 client credentials flow.

* [open-formulieren/open-forms#5688] Added ``OAuth 2.0 client credentials flow`` support.

Maintenance:

* Added support for Python 3.12 and Django 5.2 

1.0.0 (2025-06-24)
------------------

💥 Major release with breaking changes

Maintenance:

* Remove deprecated ``zgw_consumers.drf.serializers.APIModelSerializer``
* Remove deprecated ``zgw_consumers.legacy`` module
* Remove ``gemma-zds-client`` dependency
* Remove deprecated fields and methods for ``Service`` model

  * ``get_client`` and ``build_client`` (can be replaced with ``zgw_consumers.client.build_client`` together with ``ape_pie.APIClient`` or ``zgw_consumers.nlx.NLXClient``)
  * ``get_auth_header``
  * ``oas``
  * ``oas_file``

* Remove OAS test utils (moved to ``zgw-consumers-oas`` package)

  * ``zgw_consumers.test.read_schema`` (can be replaced by ``zgw_consumers_oas.read_schema``)
  * ``zgw_consumers.test.mock_service_oas_get`` (can be replaced by ``zgw_consumers_oas.mocks.mock_service_oas_get``)
  * ``zgw_consumers.test.generate_oas_component`` (can be replaced by ``zgw_consumers_oas.generate_oas_component``)

Removed deprecated settings:

* ``ZGW_CONSUMERS_IGNORE_OAS_FIELDS``
* ``ZGW_CONSUMERS_OAS_CACHE``
* ``ZGW_CONSUMERS_CLIENT_CLASS``
* ``ZGW_CONSUMERS_TEST_SCHEMA_DIRS`` (moved to ``zgw-consumers-oas``)

0.38.1 (2025-06-16)
-------------------

* [#112] Add ``jwt_valid_for`` to the django-setup-configuration model

0.38.0 (2025-04-01)
-------------------

Feature release

* [#109] 💥 The NLX directory URLs have been updated to their new location - Utrecht
  takes care of hosting these. Note that the pre-production URL is removed, as there
  were no services registered in there. If, for some reason, you still need the old URLs,
  you can specify the ``NLX_DIRECTORY_URLS`` setting in your project to the old values.
* [open-formulieren/open-forms#5193] The generated JWTs for ZGW APIs authentication now
  have an ``exp`` claim indicating when the JWT is no longer valid. By default, it is
  valid for 12 hours, but you can configure this per-service.
* The service slug is now automatically populated from the label. This only affects
  newly added services.

**Cleanups**

* The testapp settings have been updated so you can now properly use ``runserver`` to
  view the admin.
* Added some more missing Dutch translations.

0.37.0 (2025-01-27)
-------------------

Small feature release that updates ``setup-configuration`` documentation

* Use generated yaml directive for setup-config docs

0.36.1 (2024-12-03)
-------------------

Bugfix release.

* 🐛 Make it possible to refresh credentials if a client is used over a long period of time.

0.36.0 (2024-11-02)
-------------------

Small feature release that provides an optional dependency via ``zgw-consumers[setup-configuration]``

* Add a ``django-setup-configuration`` ``ConfigurationStep`` that configures any number of ``Service``\s from a YAML file.

0.35.1 (2024-08-15)
-------------------

Bugfix release.

* 🐛 The data migration introduced in 0.35.0 would initialize the ``slug``
  field in such a way that the generated slug would typically exceed the
  field's ``max_length``. This release fixes the field and the underlying
  migration.

0.35.0💥 (2024-08-13)
---------------------

**💥 0.35.0 has been yanked and should not be used to avoid ending up in
an inconsistent migration state. Use 0.35.1 instead.**

Small feature release.

* ✨ Added a slug field to the ``Service`` model for improved indexing across
  instances. As this field is required, the included migration will initiaize
  this field with a slugified version of the ``api_root`` field.
* ✨ Added natural key getters to the ``Service`` model to support Django's
  natural key-based (de)serialization methods.

**💥 Breaking changes**

* Because ``slug`` is now a required field, you may have to update your
  custom ``Service`` creation or testing logic to ensure the field is
  properly set.

0.34.0 (2024-07-31)
-------------------

Feature and maintenance release

* 💥 Dropped support for Django 3.2 (end of life), only 4.2 and up are supported.
* You can now configure a health check endpoint for a service. The HTTP response
  status code of this URL is displayed in the admin change page.

0.33.0 (2024-03-29)
-------------------

Deprecation release. We've deprecated more public API, but made sure to provide/offer
alternatives. This allows you to upgrade to newer versions of zgw-consumers already
while buying yourself enough time to update your project code.

We published some of the deprecated utilities in a separate package: ``zgw-consumers-oas``.

* Deprecated the OAS test utilities in ``zgw_consumers.test``:

    - ``read_schema``: Use ``zgw_consumers_oas.read_schema`` if you need to.
    - ``generate_oas_component``: Use ``zgw_consumers_oas.generate_oas_component`` if
      you need to. However, we recommend using `VCR`_ instead of manually
      building API mocks, or leverage factory_boy_ to generate mock data.
    - ``mock_service_oas_get``: there is no alternative because zgw-consumers no longer
      fetches configured API schemas.

* Deprecated ``zgw_consumers.drf.serializers.APIModelSerializer``. Instead, use
  `djangorestframework-dataclasses`_.

.. _VCR: https://vcrpy.readthedocs.io/en/latest/
.. _factory_boy: https://factoryboy.readthedocs.io/en/stable/
.. _djangorestframework-dataclasses: https://pypi.org/project/djangorestframework-dataclasses/

0.32.0 (2024-03-26)
-------------------

The hard dependency on gemma-zds-client client is now optional.

This is another important step towards a 1.0 version. gemma-zds-client usage is still
supported through the legacy subpackage. Additionally, it was decided that the
``zgw_consumers.api_models`` package will still be part of 1.0, but it will be deprecated
and removed in 2.0.

**💥 Breaking changes**

* The helpers in ``zgw_consumers.service`` (except for ``pagination_helper``) are
  removed. If you need these, you can safely copy the
  `0.31.0 service <https://github.com/maykinmedia/zgw-consumers/blob/0.31.0/zgw_consumers/service.py>`_
  implementation.

* The zaaktype field mixin (``ListZaaktypenMixin``) for the admin is removed. If you
  need this, we recommend writing your own version based on ``ape-pie``. You can of
  course use the `0.31.0 admin <https://github.com/maykinmedia/zgw-consumers/blob/0.31.0/zgw_consumers/admin_fields.py>`_
  implementation for inspiration.

* Removed the manager method ``Service.objects.get_client_for``. For the time being you
  can use ``Service.get_client`` instead, which is a drop-in replacement. Note however
  that this class method is deprecated and will be removed in 1.0. We recommend
  migrating to ``ape-pie``:

  .. code-block:: python

      from requests import Session
      from zgw_consumers.client import build_client

      service = Service.get_service(some_resource_url)
      client: Session = build_client(service)

* The gemma-zds-client is now an optional dependency. If you still make use of the
  ``zgw_consumers.legacy`` package, update your dependencies to include the new
  dependency group, e.g. ``zgw-consumers[zds-client]``.

**🗑️ Deprecations**

* All code that is processing an OpenAPI specification in some form is deprecated. This
  includes:

    - ``zgw_consumers.cache``
    - ``zgw_consumers.legacy``
    - ``zgw_consumers.test.component_generation``
    - ``zgw_consumers.test.schema_mock``

* Code built on top of gemma-zds-client is deprecated and will be removed in 1.0:

    - ``zgw_consumers.models.Service.build_client``
    - ``zgw_consumers.models.Service.get_client``
    - ``zgw_consumers.models.Service.get_auth_header``

**Cleanups**

* gemma-zds-client is no longer a hard dependency. Users that don't use the
  ``zgw_consumers.legacy`` package can safely remove the ``gemma-zds-client`` package.

* The ``Service`` (and ``RestAPIService`` abstract base) model requirement of either
  providing ``oas`` (URL) or ``oas_file`` is relaxed - opt-in via the new transitional
  setting ``ZGW_CONSUMERS_IGNORE_OAS_FIELDS = True``. Note that this excludes these
  fields from the admin UI and bypasses the validation that a mutually exclusive value
  must be provided.

0.31.0 (2024-03-15)
-------------------

Periodic maintenance release

**Breaking changes**

* Dropped support for Django 4.1

**Bugfixes and other cleanups**

* Updated Github actions
* Set up PyPI trusted publisher
* Drop unused PyOpenSSL dependency from installation requirements
* Switched package management to ``pyproject.toml``
* Confirmed Python 3.12 support

0.30.0 (2024-02-22)
-------------------

Feature release

* Added a timeout field (default of 10s) to the service model. The timeout is passed to
  the API client when using the ``ape-pie`` integration (
  ``zgw_consumers.client.ServiceConfigAdapter`` and
  ``zgw_consumers.client.build_client``).

0.29.0 (2024-02-05)
-------------------
Backwards compatible 'feature' release.

* [#81] Replace get_paginated_results with pagination_helper

0.28.0 (2024-01-11)
-------------------

💥 Breaking changes release!

* ``zgw_consumers`` now recommends using ``ape-pie`` as an HTTP client. The
  old ``ZGWClient`` is still made available under the
  ``zgw_consumers.legacy`` module. It is planned to be removed in the next
  major version.
* Bump the minimum supported Python version to ``3.10``.
* Some dependencies that were installed by default are now moved to the
  ``testutils`` extra dependency group.

Bugfixes and other cleanups

* Added a ``ServiceFactory`` in the ``zgw_consumers.test.factories`` module.
* Fixed an issue that could lead to an infinite loop while parsing response
  from ZTC services.
* Fixed zaaktype field crashing if the Catalogi API spec uses non-standard
  operation ID's.

0.27.0 (2023-10-10)
-------------------

Backwards compatible 'feature' release.

.. warning:: The next release will have some breaking changes w/r to the API client
   implementations.

* [#67] Mention simple certmanager in installation instructions
* Formatted code with black
* test utilities: added minimal support for 'allOf' schema in generation of OAS properties
* test utilities: schema loading (YAML parsing) is now cached

0.26.2 (2023-05-25)
-------------------

Bugfix release

Removed the ``lru_cache`` of ``zgw_consumers.admin_fields.get_zaaktypen`` to prevent
stale data being returned on configuration changes or changes in remote API data.

0.26.1 (2023-04-06)
-------------------

Fixed a data migration crash after introducing the ``Service.uuid`` field.

0.26.0 (2023-04-04)
-------------------

Feature/support release

* Catch HTTP 4xx and 5xx errors when using ZaaktypeField in the admin and display a
  meaningful message to the end user
* Added ``Service.uuid`` model field
* Confirmed support for Django 4.2 and Python 3.11

0.25.0 (2023-02-27)
-------------------

Small compatibility release

* Hardened ``get_paginated_results()`` function to accept missing 'next'-link

0.24.0 (2023-02-16)
-------------------

Small maintenance release

* Replaced django-choices with models.TextChoices
* Confirmed support for Django 4.1
* Formatted code with latest black version

0.23.2 (2022-12-06)
-------------------

* Fixed bug in ``get_paginated_results`` function
* Fixed bug in compatibility layer for zds-client v1/v2

0.23.1 (2022-11-16)
-------------------

Fixed missing prefix in default constraint name

0.23.0 (2022-11-15)
-------------------

Feature release

* ``ServiceUrlField`` now creates check constraints to guarantee data consistency

0.22.0 (2022-10-28)
-------------------

Feature release

* Added support for zds-client 2.0

0.21.2 (2022-09-07)
-------------------

Fixed the API models to be more compliant with the ZGW API standards.

(Most) fields that are not required in the API schema can now effectively be omitted
from the response and still work with the API models.

0.21.1 (2022-09-07)
-------------------

* Fixed the usage of ServiceUrlField in nested queries.

0.21.0 (2022-08-31)
-------------------

💥 Breaking changes release!

TLS certificate management has been split off into the django-simple-certmanager_
library, which is now a dependency of this project. You should update the following
references in your own code:

* ``zgw_consumers.constants.CertificateTypes`` -> ``simple_certmanager.constants.CertificateTypes``
* ``zgw_consumers.models.Certificate`` -> ``simple_certmanager.models.Certificate``

The ``Certificate`` model is identical to the one shipped in zgw-consumers before
0.21.0. As a convenience, ``zgw_consumers.Certifcate`` is still provided, which is a
proxy model to ``simple_certmanager.Certificate``.

**Other changes**

* Dropped support for Django 2.2. Only Django 3.2 and upwards are supported.
* The minimum version of gemma-zds-client_ has been bumped to the 1.0.x series

.. _django-simple-certmanager: https://pypi.org/project/django-simple-certmanager/
.. _gemma-zds-client: https://pypi.org/project/gemma-zds-client/

0.20.0 (2022-08-22)
-------------------

* Added database field ServiceUrlField

0.19.0 (2022-07-22)
-------------------

* Added management command to dump certificates to .zip archive
* Added docs (published on readthedocs.io)
* Updated package meta information

0.18.2 (2022-06-13)
-------------------

* Fixed admin crash when certificate label is empty

0.18.1 (2022-05-17)
-------------------

* Added Dutch translations
* Always display a label for certificates
* [#39] Hardened certificate admin changelist to not crash on missing physical files
* [#34] Test certificates are removed from filesystem when certificate records are deleted
* Expose type hints
