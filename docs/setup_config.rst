Setup configuration
===================

Loading Services from a YAML file
*********************************

This library provides a ``ConfigurationStep``
(from the library ``django-setup-configuration``, see the
`documentation <https://github.com/maykinmedia/django-setup-configuration>`_
for more information on how to run ``setup_configuration``)
to configure any number of ``Services`` from a YAML file.

To make use of this, you must install the ``setup-configuration`` dependency group:

.. code-block:: bash

    pip install zgw-consumers[setup-configuration]

To add this step to your configuration steps, add ``django_setup_configuration`` to ``INSTALLED_APPS`` and add the following setting:

    .. code:: python

        SETUP_CONFIGURATION_STEPS = [
            ...
            "zgw_consumers.contrib.setup_configuration.steps.ServiceConfigurationStep"
            ...
        ]

The YAML file that is passed to ``setup_configuration`` must set the
``zgw_consumers_config_enable`` flag to ``true`` to enable the step and also provide ``services`` under
the ``zgw_consumers`` namespace to configure ``Services``.

You can use the following example YAML and adapt it to your needs:

.. setup-config-example:: zgw_consumers.contrib.setup_configuration.steps.ServiceConfigurationStep
