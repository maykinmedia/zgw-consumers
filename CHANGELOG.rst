Changes
=======

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
