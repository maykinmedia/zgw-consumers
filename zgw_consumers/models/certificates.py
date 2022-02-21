from datetime import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _

from OpenSSL import crypto

from ..constants import CertificateTypes
from ..utils import pretty_print_certificate_components


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

    _certificate_obj = None

    @property
    def _certificate(self):
        if not self._certificate_obj:
            self._certificate_obj = crypto.load_certificate(
                crypto.FILETYPE_PEM, self.public_certificate.encode("utf-8")
            )
        return self._certificate_obj

    @property
    def expiry_date(self) -> datetime:
        expiry = self._certificate.get_notAfter()
        return datetime.strptime(expiry.decode("utf-8"), "%Y%m%d%H%M%SZ")

    @property
    def issuer(self):
        issuer_x509name = self._certificate.get_issuer()
        return pretty_print_certificate_components(issuer_x509name)

    @property
    def subject(self):
        subject_x509name = self._certificate.get_subject()
        return pretty_print_certificate_components(subject_x509name)
