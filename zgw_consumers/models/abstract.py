from django.db import models
from django.utils.translation import gettext_lazy as _


class Service(models.Model):
    label = models.CharField(_("label"), max_length=100)

    class Meta:
        abstract = True
