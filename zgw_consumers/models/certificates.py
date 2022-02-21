from datetime import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _

from OpenSSL import crypto

from ..constants import CertificateTypes


class Certificate(models.Model):
    label = models.CharField(
        _("label"),
        max_length=100,
        help_text=_("Recognisable label for the certificate"),
    )
    type = models.CharField(
        _("type"),
        max_length=20,
        choices=CertificateTypes.choices,
        help_text=_(
            "Is this only a certificate or is there an associated private key?"
        ),
    )
    public_certificate = models.TextField(
        _("public certificate"), help_text=_("The content of the certificate")
    )
    private_key = models.TextField(
        _("private key"), help_text=_("The content of the private key"), blank=True
    )

    class Meta:
        verbose_name = _("certificate")
        verbose_name_plural = _("certificates")

    @property
    def expiry_date(self) -> datetime:
        certificate = crypto.load_certificate(
            crypto.FILETYPE_PEM, self.public_certificate.encode("utf-8")
        )
        expiry_datetime = certificate.get_notAfter()
        print(expiry_datetime)
        return expiry_datetime

    @property
    def issuer(self):
        certificate = crypto.load_certificate(
            crypto.FILETYPE_PEM, self.public_certificate.encode("utf-8")
        )
