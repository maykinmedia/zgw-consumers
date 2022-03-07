from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from OpenSSL import crypto

from .models import Certificate


class CertificateAdminForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = "__all__"

    def clean_public_certificate(self):
        if self.cleaned_data["public_certificate"].closed:
            self.cleaned_data["public_certificate"].open()
        self.cleaned_data["public_certificate"].seek(0)

        try:
            crypto.load_certificate(
                crypto.FILETYPE_PEM,
                self.cleaned_data["public_certificate"].read(),
            )
        except Exception:
            raise ValidationError(_("Invalid certificate"), code="invalid")

        return self.cleaned_data["public_certificate"]
