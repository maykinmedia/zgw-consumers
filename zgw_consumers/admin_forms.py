"""
Admin forms for the :class:`~zgw_consumers.models.Service` credentials.

The credential fields (``secret`` and ``header_value``) are write-only in the admin:
the change form only shows a masked hint of the stored value, and changing it
happens through a dedicated form (similar to how ``django.contrib.auth`` handles
user passwords).
"""

from typing import TYPE_CHECKING, ClassVar

from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from django.db import models
from django.utils.functional import Promise
from django.utils.translation import gettext_lazy as _

from .models import Service

if TYPE_CHECKING:
    from django_stubs_ext import StrOrPromise

#: The credential fields that are masked in the admin -> the URL path segment (below
#: the change page of a service) of the admin view that changes it.
CREDENTIAL_URL_SEGMENTS: dict[str, str] = {
    "secret": "secret",
    # the header key is changed together with its value
    "header_value": "header-key-value",
}

CREDENTIAL_FIELDS = tuple(CREDENTIAL_URL_SEGMENTS)


def credential_change_url(field_name: str) -> str:
    """URL of the change view of a credential, relative to the service change page."""
    return f"../{CREDENTIAL_URL_SEGMENTS[field_name]}/"


def field_verbose_name(field_name: str) -> "StrOrPromise":
    field = Service._meta.get_field(field_name)
    # narrow away relations, which have no verbose name
    assert isinstance(field, models.Field)
    return field.verbose_name


#: Number of trailing characters to reveal. The end of a credential tells values
#: apart better than the start, which is often a fixed scheme or vendor marker
#: (``Token ``, ``Bearer ``, ``sk_live_``). Values that are not longer than this
#: reveal nothing (the suffix would be the whole value), so the hint only tells
#: whether a value is trivially short - nothing more about its length.
REVEAL_CHARS = 4

#: Fixed-length mask, so the hint does not leak the length of the credential.
MASK_PREFIX = "*" * 12


def mask(value: str) -> str:
    """
    Return a masked hint for ``value``.

    The last :data:`REVEAL_CHARS` characters are shown, unless that would reveal
    the whole value - then none are. The mask has a fixed length.
    """
    if not value:
        return ""
    suffix = value[-REVEAL_CHARS:] if len(value) > REVEAL_CHARS else ""
    return f"{MASK_PREFIX}{suffix}"


class MaskedCredentialWidget(forms.Widget):
    """
    Display-only widget: shows the (masked) value and a button linking to the
    flow that changes it.

    Pass ``masked=False`` for non-secret values that are changed in a credential
    flow, like the header key.
    """

    template_name = "admin/zgw_consumers/widgets/masked_credential.html"

    def __init__(self, change_url: str = "", masked: bool = True, attrs=None):
        self.change_url = change_url
        self.masked = masked
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        value = value or ""
        context["widget"].update(
            {
                # never ship the actual credential to the browser
                "value": None,
                "display_value": mask(value) if self.masked else value,
                "change_url": self.change_url,
            }
        )
        return context

    def id_for_label(self, id_):
        # there is no labelable element (empty -> the label gets no ``for``)
        return ""


class MaskedCredentialField(forms.CharField):
    """
    Display-only field - submitted data is ignored because the field is disabled, so
    the instance keeps (and model validation sees) the stored value.
    """

    widget = MaskedCredentialWidget

    def __init__(self, *args, change_url: str = "", **kwargs):
        kwargs.setdefault("required", False)
        kwargs.setdefault("disabled", True)
        kwargs.setdefault("widget", MaskedCredentialWidget(change_url=change_url))
        super().__init__(*args, **kwargs)


class ServiceAddForm(forms.ModelForm):
    """
    Credentials can be entered directly when creating a service. Only the submitted
    value is rendered back (masked) when the form has errors.
    """

    class Meta:
        model = Service
        # the admin passes the actual field list to modelform_factory
        fields = "__all__"  # noqa: DJ007
        widgets: ClassVar = {
            # render_value: on validation errors, echo back what the user just
            # submitted (never a stored value - this form is only used for adding).
            # new-password prevents browsers from autofilling a saved login.
            "secret": forms.PasswordInput(
                render_value=True, attrs={"autocomplete": "new-password"}
            ),
            "header_value": forms.PasswordInput(
                render_value=True, attrs={"autocomplete": "new-password"}
            ),
        }


class ServiceChangeForm(forms.ModelForm):
    class Meta:
        model = Service
        # the admin passes the actual field list to modelform_factory
        fields = "__all__"  # noqa: DJ007

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The model requires the header key and value to be both set or both empty,
        # so they are only changed together, in the header value flow.
        if (header_key := self.fields.get("header_key")) is not None:
            # Disabled rather than an admin readonly field: model validation errors
            # on ``header_key`` (inconsistent stored data) need a form field to
            # attach to.
            header_key.disabled = True
            header_key.widget = MaskedCredentialWidget(
                change_url=credential_change_url("header_value"),
                masked=False,
            )

        for name in CREDENTIAL_FIELDS:
            if (original := self.fields.get(name)) is None:
                continue
            self.fields[name] = MaskedCredentialField(
                label=original.label,
                help_text=original.help_text,
                change_url=credential_change_url(name),
            )


class ServiceCredentialChangeForm(forms.ModelForm):
    """
    Write a credential field of a service, together with the (non-secret) fields
    that belong to it.

    Model validation (``Service.clean``) still runs against the full instance, so e.g.
    clearing the secret of a service using ZGW auth is rejected.
    """

    #: credential field -> non-secret fields that are edited together with it
    paired_fields: ClassVar[dict[str, tuple[str, ...]]] = {
        "secret": (),
        # the model requires the header key and value to be both set or both empty
        "header_value": ("header_key",),
    }

    def __init__(self, *args, field_name: str, **kwargs):
        assert field_name in CREDENTIAL_FIELDS
        self.field_name = field_name
        super().__init__(*args, **kwargs)
        # only keep the fields we're editing
        keep = {field_name, *self.paired_fields[field_name]}
        for name in list(self.fields):
            if name not in keep:
                del self.fields[name]

        # keep the model field label - the admin history message is built from it
        field = self.fields[field_name]
        attrs = {"autocomplete": "new-password"}
        # hint at the stored value - computed now, before validation of submitted
        # data can modify the instance
        if current := mask(getattr(self.instance, field_name)):
            attrs["placeholder"] = current
        field.widget = forms.PasswordInput(render_value=False, attrs=attrs)
        if field_name == "header_value":
            field.help_text = _(
                "The current value is never shown, so enter it again when changing "
                "the header key. Leave both fields empty to stop using API key "
                "authentication."
            )

    class Meta:
        model = Service
        # paired fields first, so they render above the credential
        fields = ("header_key", *CREDENTIAL_FIELDS)

    @property
    def title_label(self) -> str | Promise:
        """
        Human readable name of what this form changes.
        """
        if self.field_name == "header_value":
            return _("header key and value")
        return field_verbose_name(self.field_name)

    def _update_errors(self, errors):
        # Service.clean may raise errors for fields not in this form (e.g. setting
        # a header value without a header key flags ``header_key``). Surface those
        # as non-field errors instead of crashing.
        error_dict = getattr(errors, "error_dict", None)
        if error_dict:
            for name in list(error_dict):
                if name not in self.fields and name != NON_FIELD_ERRORS:
                    error_dict.setdefault(NON_FIELD_ERRORS, []).extend(
                        error_dict.pop(name)
                    )
        super()._update_errors(errors)  # pyright: ignore[reportAttributeAccessIssue] private Django API, missing from the stubs
