from django.utils.translation import gettext_lazy as _

from rest_framework import fields
from rest_framework.exceptions import ValidationError

from zgw_consumers.models import Service


class ServiceValidator:
    """
    Validate that url belongs to the known Service
    """

    message = _("The url service is unknown.")
    code = "unknown_service"

    def __call__(self, value):
        if not value:
            return

        service = Service.get_service(value)
        if not service:
            raise ValidationError(self.message, code=self.code)


class ServiceUrlApiField(fields.URLField):
    """Serializer field for database ServiceUrlField field"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validators.append(ServiceValidator())
