from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Service(models.Model):
    label = models.CharField(_("label"), max_length=100)

    class Meta:
        abstract = True


class RestAPIService(Service):
    oas = models.URLField(
        _("OAS url"), max_length=1000, blank=True, help_text=_("URL to OAS yaml file")
    )
    oas_file = models.FileField(
        _("OAS file"),
        blank=True,
        help_text=_("OAS yaml file"),
        upload_to="zgw-consumers/oas/",
        validators=[FileExtensionValidator(["yml", "yaml"])],
    )

    class Meta:
        abstract = True
