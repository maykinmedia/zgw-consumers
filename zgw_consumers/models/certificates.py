from datetime import date, datetime
from typing import Optional

from django.db import models
from django.utils.translation import gettext, gettext_lazy as _

from OpenSSL import SSL, crypto
from privates.fields import PrivateMediaFileField

from ..constants import CertificateTypes
from ..mixins import DeleteFileFieldFilesMixin
from ..utils import pretty_print_certificate_components


class Certificate(DeleteFileFieldFilesMixin, models.Model):
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
    public_certificate = PrivateMediaFileField(
        _("public certificate"),
        help_text=_("The content of the certificate"),
        upload_to="ssl_certs_keys/%Y/%m/%d",
    )
    private_key = PrivateMediaFileField(
        _("private key"),
        help_text=_("The content of the private key"),
        blank=True,
        upload_to="ssl_certs_keys/%Y/%m/%d",
    )

    class Meta:
        verbose_name = _("certificate")
        verbose_name_plural = _("certificates")

    _certificate_obj = None
    _private_key_obj = None

    def __str__(self):
        return self.label or gettext("(missing label)")

    @property
    def _certificate(self):
        if not self._certificate_obj:
            with self.public_certificate.open(mode="rb") as certificate_f:
                self._certificate_obj = crypto.load_certificate(
                    crypto.FILETYPE_PEM, certificate_f.read()
                )
        return self._certificate_obj

    @property
    def _private_key(self):
        if not self._private_key_obj:
            with self.private_key.open(mode="rb") as key_f:
                self._private_key_obj = crypto.load_privatekey(
                    crypto.FILETYPE_PEM, key_f.read()
                )
        return self._private_key_obj

    @property
    def expiry_date(self) -> datetime:
        expiry = self._certificate.get_notAfter()
        return datetime.strptime(expiry.decode("utf-8"), "%Y%m%d%H%M%SZ")

    @property
    def issuer(self) -> str:
        issuer_x509name = self._certificate.get_issuer()
        return pretty_print_certificate_components(issuer_x509name)

    @property
    def subject(self) -> str:
        subject_x509name = self._certificate.get_subject()
        return pretty_print_certificate_components(subject_x509name)

    def is_valid_key_pair(self) -> Optional[bool]:
        if not self.private_key:
            return None

        context = SSL.Context(SSL.TLSv1_2_METHOD)
        context.use_privatekey(self._private_key)
        context.use_certificate(self._certificate)

        try:
            context.check_privatekey()
        except SSL.Error:
            return False

        return True

    is_valid_key_pair.boolean = True
