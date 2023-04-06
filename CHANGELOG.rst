Changes
=======

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
