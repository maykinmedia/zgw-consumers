from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from OpenSSL import crypto

from .models import Certificate
from .widgets import PasswordAreaWidget


class CertificateAdminForm(forms.ModelForm):
    private_key = forms.CharField(
        widget=PasswordAreaWidget(),
        help_text=_("The private key can only be updated, but not read."),
        required=False,
    )

    class Meta:
        model = Certificate
        fields = ("label", "type", "public_certificate", "private_key")

    def clean_public_certificate(self):
        try:
            crypto.load_certificate(
                crypto.FILETYPE_PEM,
                self.cleaned_data["public_certificate"].encode("utf-8"),
            )
        except Exception:
            raise ValidationError(_("Invalid certificate"), code="invalid")
        return self.cleaned_data["public_certificate"]
