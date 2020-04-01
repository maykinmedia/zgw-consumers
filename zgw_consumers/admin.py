from django.contrib import admin

from .admin_fields import get_zaaktype_field
from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("label", "api_type", "api_root", "auth_type")
    list_filter = ("api_type", "auth_type")
    search_fields = ("label", "api_root", "nlx")


class ListZaaktypenMixin:
    zaaktype_fields = ()

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in self.zaaktype_fields:
            return get_zaaktype_field(db_field, request, **kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)
