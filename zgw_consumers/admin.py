from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from privates.admin import PrivateMediaMixin
from solo.admin import SingletonModelAdmin

from .admin_fields import get_nlx_field, get_zaaktype_field
from .forms import CertificateAdminForm
from .models.certificates import Certificate
from .models.services import NLXConfig, Service
from .widgets import NoDownloadPrivateFileWidget


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("label", "api_type", "api_root", "nlx", "auth_type")
    list_filter = ("api_type", "auth_type")
    search_fields = ("label", "api_root", "nlx")

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "nlx":
            return get_nlx_field(db_field, request, **kwargs)

        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(NLXConfig)
class NLXConfigAdmin(PrivateMediaMixin, SingletonModelAdmin):
    private_media_fields = ("certificate", "certificate_key")
    private_media_file_widget = NoDownloadPrivateFileWidget


@admin.register(Certificate)
class CertificateAdmin(PrivateMediaMixin, admin.ModelAdmin):
    form = CertificateAdminForm

    fields = ("label", "type", "public_certificate", "private_key")
    list_display = ("get_label", "type", "expiry_date", "is_valid_key_pair")
    list_filter = ("label", "type")
    search_fields = ("label", "type")

    private_media_fields = ("public_certificate", "private_key")

    def get_label(self, obj):
        return str(obj)

    get_label.short_description = _("label")
    get_label.admin_order_field = "label"

    def expiry_date(self, obj=None):
        # alias model property to catch file not found errors
        try:
            return obj.expiry_date
        except FileNotFoundError:
            return _("file not found")

    expiry_date.short_description = _("expiry date")

    def is_valid_key_pair(self, obj=None):
        # alias model method to catch file not found errors
        try:
            return obj.is_valid_key_pair()
        except FileNotFoundError:
            return None

    is_valid_key_pair.short_description = _("valid key pair")
    is_valid_key_pair.boolean = True


class ListZaaktypenMixin:
    zaaktype_fields = ()

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in self.zaaktype_fields:
            return get_zaaktype_field(db_field, request, **kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)
