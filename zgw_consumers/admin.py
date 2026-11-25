from collections.abc import Sequence
from typing import ClassVar

from django.contrib import admin, messages
from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpRequest, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.functional import Promise
from django.utils.translation import gettext_lazy as _

from privates.admin import PrivateMediaMixin
from solo.admin import SingletonModelAdmin

from .admin_fields import get_nlx_field
from .admin_forms import (
    CREDENTIAL_URL_SEGMENTS,
    ServiceAddForm,
    ServiceChangeForm,
    ServiceCredentialChangeForm,
    field_verbose_name,
    mask,
)
from .models.services import NLXConfig, Service
from .widgets import NoDownloadPrivateFileWidget


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("label", "api_type", "api_root", "slug", "nlx", "auth_type")
    list_filter = ("api_type", "auth_type")
    search_fields = ("label", "api_root", "nlx", "uuid", "slug")
    readonly_fields = ("get_connection_check",)
    prepopulated_fields: ClassVar[dict[str, Sequence[str]]] = {"slug": ["label"]}  # pyright: ignore[reportIncompatibleVariableOverride]
    form = ServiceChangeForm
    add_form = ServiceAddForm
    change_credential_template = "admin/zgw_consumers/service/change_credential.html"

    #: credential field -> admin display method showing the masked hint, used
    #: instead of the field for users who may view but not change a service
    credential_hint_fields: ClassVar[dict[str, str]] = {
        "secret": "get_secret_hint",
        "header_value": "get_header_value_hint",
    }

    def get_form(self, request, obj=None, change=False, **kwargs):
        if obj is None:
            kwargs["form"] = self.add_form
        return super().get_form(request, obj, change=change, **kwargs)

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if obj is None or self.has_change_permission(request, obj):
            return fields
        # In view-only mode the admin renders every field as readonly, reading the
        # raw value from the instance (bypassing the form widget). Swap the
        # credentials for display methods that only show the masked hint (the admin
        # makes all of them readonly and excludes them from the form).
        swapped = [
            # (tuples are fields rendered on one line)
            self.credential_hint_fields.get(f, f) if isinstance(f, str) else f
            for f in fields
        ]
        return list(dict.fromkeys(swapped))

    @admin.display(description=field_verbose_name("secret"))
    def get_secret_hint(self, obj: Service) -> str | Promise:
        return mask(obj.secret) or _("(not set)")

    @admin.display(description=field_verbose_name("header_value"))
    def get_header_value_hint(self, obj: Service) -> str | Promise:
        return mask(obj.header_value) or _("(not set)")

    def get_urls(self):
        info = self.opts.app_label, self.opts.model_name
        return [
            path(
                f"<id>/{segment}/",
                self.admin_site.admin_view(self.change_credential_view),
                kwargs={"field_name": field_name},
                name="{}_{}_change_{}".format(*info, field_name),
            )
            for field_name, segment in CREDENTIAL_URL_SEGMENTS.items()
        ] + super().get_urls()

    def change_credential_view(self, request: HttpRequest, id: str, field_name: str):
        service = self.get_object(request, unquote(id))
        if service is None:
            raise Http404
        if not self.has_change_permission(request, service):
            raise PermissionDenied

        form = ServiceCredentialChangeForm(
            data=request.POST if request.method == "POST" else None,
            instance=service,
            field_name=field_name,
        )
        field_label = form.title_label
        # snapshot before validation mutates the instance
        current_hint = mask(getattr(service, field_name)) or _("(not set)")

        if form.is_valid():
            form.save()
            change_message = self.construct_change_message(
                request,
                form,  # pyright: ignore[reportArgumentType] the stubs only accept a Form, not a ModelForm
                [],
            )
            self.log_change(request, service, change_message)
            self.message_user(
                request,
                _("The {field} of {service} was changed successfully.").format(
                    field=field_label, service=service
                ),
                messages.SUCCESS,
            )
            return HttpResponseRedirect(
                reverse(
                    f"admin:{self.opts.app_label}_{self.opts.model_name}_change",
                    args=(service.pk,),
                    current_app=self.admin_site.name,
                )
            )

        context = {
            **self.admin_site.each_context(request),
            "title": _("Change {field}").format(field=field_label),
            "field_label": field_label,
            "hint_label": field_verbose_name(field_name),
            "current_hint": current_hint,
            "form": form,
            "is_popup": False,
            "opts": self.opts,
            "original": service,
            "has_view_permission": self.has_view_permission(request, service),
        }
        request.current_app = self.admin_site.name
        return TemplateResponse(request, self.change_credential_template, context)

    @admin.display(description=_("Connection check status code"))
    def get_connection_check(self, obj):
        if obj.pk is None:
            return _("n/a")

        return obj.connection_check

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "nlx":
            return get_nlx_field(db_field, request, **kwargs)

        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(NLXConfig)
class NLXConfigAdmin(PrivateMediaMixin, SingletonModelAdmin):
    private_media_fields = ("certificate", "certificate_key")
    private_media_file_widget = NoDownloadPrivateFileWidget
