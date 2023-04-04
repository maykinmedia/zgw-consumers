from django.contrib import admin

from privates.admin import PrivateMediaMixin
from solo.admin import SingletonModelAdmin

from .admin_fields import get_nlx_field, get_zaaktype_field
from .models.services import NLXConfig, Service
from .widgets import NoDownloadPrivateFileWidget


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("label", "api_type", "api_root", "nlx", "auth_type")
    list_filter = ("api_type", "auth_type")
    search_fields = ("label", "api_root", "nlx", "uuid")

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "nlx":
            return get_nlx_field(db_field, request, **kwargs)

        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(NLXConfig)
class NLXConfigAdmin(PrivateMediaMixin, SingletonModelAdmin):
    private_media_fields = ("certificate", "certificate_key")
    private_media_file_widget = NoDownloadPrivateFileWidget


class ListZaaktypenMixin:
    zaaktype_fields = ()

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in self.zaaktype_fields:
            return get_zaaktype_field(db_field, request, **kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)
