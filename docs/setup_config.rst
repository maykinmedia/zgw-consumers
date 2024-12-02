Setup configuration
===================

Loading Services from a YAML file
*********************************

This library provides a ``ConfigurationStep``
(from the library ``django-setup-configuration``, see the
`documentation <https://github.com/maykinmedia/django-setup-configuration>`_
for more information on how to run ``setup_configuration``)
to configure any number of ``Services`` from a YAML file.

To add this step to your configuration steps, add ``django_setup_configuration`` to ``INSTALLED_APPS`` and add the following setting:

    .. code:: python

        SETUP_CONFIGURATION_STEPS = [
            ...
            "zgw_consumers.contrib.setup_configuration.steps.ServiceConfigurationStep"
            ...
        ]

The YAML file that is passed to ``setup_configuration`` must set the
``zgw_consumers_config_enable`` flag to ``true`` to enable the step and also provide ``services`` under
the ``zgw_consumers`` namespace to configure ``Services``

Example file:

    .. code:: yaml

        zgw_consumers_config_enable: True
        zgw_consumers:
          services:
          # all possible configurable fields
          - identifier: objecten-test
            label: Objecten API test
            api_root: http://objecten.local/api/v1/
            api_connection_check_path: objects
            api_type: orc
            auth_type: api_key
            header_key: Authorization
            header_value: Token foo
            client_id: client
            secret: super-secret
            nlx: http://some-outway-adress.local:8080/
            user_id: open-formulieren
            user_representation: Open Formulieren
            timeout: 5
          # minimum required fields
          - identifier: objecttypen-test
            label: Objecttypen API test
            api_root: http://objecttypen.local/api/v1/
            api_type: orc
            auth_type: api_key
