from __future__ import annotations

import importlib.util
import logging
import socket
import uuid
from urllib.parse import urlparse, urlsplit, urlunsplit

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Length
from django.utils.translation import gettext_lazy as _

from privates.fields import PrivateMediaFileField
from simple_certmanager.models import Certificate
from solo.models import SingletonModel
from typing_extensions import Self

from zgw_consumers import settings as zgw_settings

from ..constants import APITypes, AuthTypes, NLXDirectories
from .abstract import Service as _Service
from .validators import NonUrlValidator, validate_leading_slashes

logger = logging.getLogger(__name__)


class ServiceManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class Service(_Service):
    uuid = models.UUIDField(_("UUID"), default=uuid.uuid4)
    slug = models.SlugField(
        _("service slug"),
        blank=False,
        null=False,
        unique=True,
        help_text=_(
            "A unique, human-friendly slug to identify this service. Primarily useful for cross-instance import/export."
        ),
        max_length=255,
    )
    api_type = models.CharField(_("type"), max_length=20, choices=APITypes.choices)
    api_root = models.CharField(
        _("api root url"),
        help_text=_(
            "The root URL of the service that will be used to construct the URLs when making requests."
        ),
        max_length=255,
        unique=True,
    )
    api_connection_check_path = models.CharField(
        _("connection check endpoint"),
        help_text=_(
            "A relative URL to perform a connection test. If left blank, the API root itself is used. "
            "This connection check is only performed in the admin when viewing the service "
            "configuration."
        ),
        max_length=255,
        validators=[
            validate_leading_slashes,
            NonUrlValidator(),
        ],
        blank=True,
    )

    auth_type = models.CharField(
        _("authorization type"),
        max_length=30,
        choices=AuthTypes.choices,
        default=AuthTypes.zgw,
        help_text=_("The type of authorization to use for this service."),
    )
    # credentials for the API, ZGW auth
    client_id = models.CharField(
        max_length=255,
        blank=True,
        help_text=_(
            "The client ID used to construct the JSON Web Token to connect "
            "with the service (only needed if auth type is `zgw` or `oauth2_client_credentials`)."
        ),
    )
    secret = models.CharField(
        max_length=255,
        blank=True,
        help_text=_(
            "The secret used to construct the JSON Web Token to connect with "
            "the service (only needed if auth type is `zgw` or `oauth2_client_credentials`)."
        ),
    )
    # necessary only for OAuth2 client credentials flow
    oauth2_token_url = models.URLField(
        _("OAuth2 token url"),
        max_length=1000,
        blank=True,
        help_text=_(
            "OAuth2 token endpoint for client credentials flow. "
            "(Only needed if auth type is OAuth2)"
        ),
    )
    # necessary only for OAuth2 client credentials flow
    oauth2_scope = models.CharField(
        _("OAuth2 scope"),
        max_length=255,
        blank=True,
        help_text=_(
            "Optional OAuth2 scope (space-separated). "
            "Included in the token request body if defined. "
            "(Only needed if auth type is OAuth2)"
        ),
    )
    jwt_valid_for = models.PositiveIntegerField(
        _("JWT expires after"),
        default=12 * 60 * 60,  # 12 hours as default
        help_text=_(
            "How long a JWT is valid for, in seconds. This controls the 'exp' claim "
            "(only used if auth type is `zgw`)."
        ),
    )
    # credentials for the API, API key
    header_key = models.CharField(
        _("header key"),
        max_length=100,
        blank=True,
        help_text=_(
            "The header key used to store the API key (only needed if auth type is `api_key`)."
        ),
    )
    header_value = models.CharField(
        _("header value"),
        max_length=255,
        blank=True,
        help_text=_(
            "The API key to connect with the service (only needed if auth type is `api_key`)."
        ),
    )
    nlx = models.URLField(
        _("NLX url"), max_length=1000, blank=True, help_text=_("NLX (outway) address.")
    )
    user_id = models.CharField(
        _("user ID"),
        max_length=255,
        blank=True,
        help_text=_(
            "User ID to use for the audit trail. Although these external API credentials are typically used by"
            "this API itself instead of a user, the user ID is required."
        ),
    )
    user_representation = models.CharField(
        _("user representation"),
        max_length=255,
        blank=True,
        help_text=_("Human readable representation of the user."),
    )
    client_certificate = models.ForeignKey(
        Certificate,
        blank=True,
        null=True,
        help_text=_("The SSL/TLS certificate of the client"),
        on_delete=models.PROTECT,
        related_name="service_client",
    )
    server_certificate = models.ForeignKey(
        Certificate,
        blank=True,
        null=True,
        help_text=_("The SSL/TLS certificate of the server"),
        on_delete=models.PROTECT,
        related_name="service_server",
    )
    timeout = models.PositiveSmallIntegerField(
        _("timeout"),
        help_text=_("Timeout (in seconds) for HTTP calls."),
        default=10,
    )

    objects = ServiceManager()

    class Meta:
        verbose_name = _("service")
        verbose_name_plural = _("services")

    def __str__(self):
        return f"[{self.get_api_type_display()}] {self.label}"

    def natural_key(self):
        return (self.slug,)

    def save(self, *args, **kwargs):
        if not self.api_root.endswith("/"):
            self.api_root = f"{self.api_root}/"

        if self.nlx and not self.nlx.endswith("/"):
            self.nlx = f"{self.nlx}/"

        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        # validate header_key and header_value
        if self.header_key and not self.header_value:
            raise ValidationError(
                {
                    "header_value": _(
                        "If field '{header_key}' is set, field '{header_value}' must also be set"
                    ).format(
                        header_key=self._meta.get_field("header_key").verbose_name,
                        header_value=self._meta.get_field("header_value").verbose_name,
                    )
                }
            )
        if not self.header_key and self.header_value:
            raise ValidationError(
                {
                    "header_key": _(
                        "If field '{header_value}' is set, field '{header_key}' must also be set"
                    ).format(
                        header_value=self._meta.get_field("header_value").verbose_name,
                        header_key=self._meta.get_field("header_key").verbose_name,
                    )
                }
            )

        # validate required fields for oauth2_client_credentials type
        if self.auth_type == AuthTypes.oauth2_client_credentials:
            if importlib.util.find_spec("requests_oauthlib") is None:
                raise ValidationError(
                    {
                        "auth_type": _(
                            "Additional libraries are required to use OAuth, which aren't installed. Select another method."
                        )
                    }
                )

            missing = [
                field
                for field in (
                    "client_id",
                    "secret",
                    "oauth2_token_url",
                )
                if not getattr(self, field)
            ]
            if missing:
                raise ValidationError(
                    {
                        field: _(
                            "The field '{field_name}' is required for OAuth2 client credentials flow"
                        ).format(field_name=self._meta.get_field(field).verbose_name)
                        for field in missing
                    }
                )

    @property
    def connection_check(self) -> int | None:
        from zgw_consumers.client import build_client

        try:
            client = build_client(self)
            return client.get(
                self.api_connection_check_path or self.api_root
            ).status_code
        # Catching generic exceptions is not ideal but we cannot handle this kind of
        # situations in another way. This helps and informs the user about the problem
        # of the service configuration instead of crashing the application (change page).
        except Exception as e:
            logger.info(
                "Encountered an error while performing the connection check to service %s",
                self,
                exc_info=e,
            )

        return None

    @classmethod
    def get_service(cls, url: str) -> Self | None:
        split_url = urlsplit(url)
        scheme_and_domain = urlunsplit(split_url[:2] + ("", "", ""))

        candidates = (
            cls.objects.filter(api_root__startswith=scheme_and_domain)
            .annotate(api_root_length=Length("api_root"))
            .order_by("-api_root_length")
        )

        # select the one matching
        for candidate in candidates.iterator():
            if url.startswith(candidate.api_root):
                return candidate

        return None


class NLXConfig(SingletonModel):
    directory = models.CharField(
        _("NLX directory"), max_length=50, choices=NLXDirectories.choices, blank=True
    )
    outway = models.URLField(
        _("NLX outway address"),
        blank=True,
        help_text=_("Example: http://my-outway.nlx:8080"),
    )
    certificate = PrivateMediaFileField(
        upload_to="zgw-consumers/nlx/",
        blank=True,
        help_text=_(
            "Your organization TLS certificate for the NLX network. This is used to "
            "fetch the list of available services from the NLX directory API."
        ),
    )
    certificate_key = PrivateMediaFileField(
        upload_to="zgw-consumers/nlx/",
        help_text=_(
            "Your organization TLS private key for the NLX network. This is used to "
            "fetch the list of available services from the NLX directory API."
        ),
        blank=True,
    )

    class Meta:
        verbose_name = _("NLX configuration")

    @property
    def directory_url(self) -> str:
        nlx_directory_urls = zgw_settings.get_setting("NLX_DIRECTORY_URLS")
        return nlx_directory_urls.get(self.directory, "")

    def save(self, *args, **kwargs):
        if self.outway and not self.outway.endswith("/"):
            self.outway = f"{self.outway}/"

        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        if not self.outway:
            return

        # try to tcp connect to the port
        parsed = urlparse(self.outway)
        default_port = 80 if parsed.scheme == "http" else 443
        port = parsed.port or default_port

        nlx_outway_timeout = zgw_settings.get_setting("NLX_OUTWAY_TIMEOUT")
        with socket.socket() as s:
            s.settimeout(nlx_outway_timeout)
            try:
                s.connect((parsed.hostname, port))
            except (OSError, ConnectionRefusedError):
                raise ValidationError(
                    _("Connection refused. Please provide a correct address.")
                )
