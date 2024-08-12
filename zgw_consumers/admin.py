from django.contrib import admin
from django.db import models
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from privates.admin import PrivateMediaMixin
from solo.admin import SingletonModelAdmin

from .admin_fields import get_nlx_field
from .models.services import NLXConfig, Service
from .settings import get_setting
from .widgets import NoDownloadPrivateFileWidget


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("label", "api_type", "api_root", "slug", "nlx", "auth_type")
    list_filter = ("api_type", "auth_type")
    search_fields = ("label", "api_root", "nlx", "uuid", "slug")
    readonly_fields = ("get_connection_check",)
    prepopulated_fields = {"slug": ["api_root"]}

    @admin.display(description=_("Connection check status code"))
    def get_connection_check(self, obj):
        if obj.pk is None:
            return _("n/a")

        return obj.connection_check

    def get_fields(self, request: HttpRequest, obj: models.Model | None = None):
        fields = super().get_fields(request, obj=obj)
        if get_setting("ZGW_CONSUMERS_IGNORE_OAS_FIELDS"):
            assert isinstance(fields, list)
            fields.remove("oas")
            fields.remove("oas_file")
        return fields

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "nlx":
            return get_nlx_field(db_field, request, **kwargs)

        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(NLXConfig)
class NLXConfigAdmin(PrivateMediaMixin, SingletonModelAdmin):
    private_media_fields = ("certificate", "certificate_key")
    private_media_file_widget = NoDownloadPrivateFileWidget
