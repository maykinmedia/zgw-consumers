from django.db import models

from zgw_consumers.models import ServiceUrlField


# set up for ServiceUrl test
# todo test together with loose-fk???
class Case(models.Model):
    _casetype_api = models.ForeignKey(
        "zgw_consumers.Service", on_delete=models.SET_NULL, null=True, blank=True
    )
    _casetype_relative = models.CharField(max_length=200, blank=True, null=True)
    casetype = ServiceUrlField(
        base_field="_casetype_api",
        relative_field="_casetype_relative",
        blank=True,
        null=True,
    )
