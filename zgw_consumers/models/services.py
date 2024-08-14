from __future__ import annotations

import logging
import socket
import uuid
from typing import TYPE_CHECKING
from urllib.parse import urlparse, urlsplit, urlunsplit

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Length
from django.utils.translation import gettext_lazy as _

from privates.fields import PrivateMediaFileField
from requests.exceptions import RequestException
from simple_certmanager.models import Certificate
from solo.models import SingletonModel
from typing_extensions import Self, deprecated

from zgw_consumers import settings as zgw_settings

from ..constants import APITypes, AuthTypes, NLXDirectories
from .abstract import RestAPIService
from .validators import NonUrlValidator, validate_leading_slashes

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ..legacy.client import ZGWClient


class ServiceManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class Service(RestAPIService):
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
    api_root = models.CharField(_("api root url"), max_length=255, unique=True)
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

    # credentials for the API
    client_id = models.CharField(max_length=255, blank=True)
    secret = models.CharField(max_length=255, blank=True)
    auth_type = models.CharField(
        _("authorization type"),
        max_length=20,
        choices=AuthTypes.choices,
        default=AuthTypes.zgw,
    )
    header_key = models.CharField(_("header key"), max_length=100, blank=True)
    header_value = models.CharField(_("header value"), max_length=255, blank=True)
    nlx = models.URLField(
        _("NLX url"), max_length=1000, blank=True, help_text=_("NLX (outway) address")
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
                        "If header_key is set, header_value must also be set"
                    )
                }
            )
        if not self.header_key and self.header_value:
            raise ValidationError(
                {"header_key": _("If header_value is set, header_key must also be set")}
            )

    @property
    def connection_check(self) -> int | None:
        from zgw_consumers.client import build_client

        try:
            client = build_client(self)
            return client.get(
                self.api_connection_check_path or self.api_root
            ).status_code
        except RequestException as e:
            logger.info(
                "Encountered an error while performing the connection check to service %s",
                self,
                exc_info=e,
            )

        return None

    @deprecated(
        "The `build_client` method is deprecated and will be removed in the next major release. "
        "Instead, use the new `ape_pie.APIClient` or `zgw_consumers.nlx.NLXClient`.",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def build_client(self, **claims):
        """
        Build an API client from the service configuration.
        """
        from ..legacy.client import ClientAuth, get_client_class

        api_root = self.api_root
        if self.nlx:
            api_root = api_root.replace(self.api_root, self.nlx, 1)

        Client = get_client_class()
        client = Client(api_root, schema_url=self.oas, schema_file=self.oas_file)

        if self.server_certificate:
            client.server_certificate_path = (
                self.server_certificate.public_certificate.path
            )

        if self.client_certificate:
            client.client_certificate_path = (
                self.client_certificate.public_certificate.path
            )

            if self.client_certificate.private_key:
                client.client_private_key_path = (
                    self.client_certificate.private_key.path
                )

        if self.auth_type == AuthTypes.zgw:
            client.auth = ClientAuth(
                client_id=self.client_id,
                secret=self.secret,
                user_id=self.user_id,
                user_representation=self.user_representation,
                **claims,
            )
        elif self.auth_type == AuthTypes.api_key:
            client.auth_value = {self.header_key: self.header_value}

        return client

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

    @classmethod
    @deprecated(
        "The `get_client` class method is deprecated and will be removed in the next "
        "major release. Instead, use the `get_service` class method combined with "
        "zgw_consumers.client.build_client.",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def get_client(cls, url: str, **kwargs) -> ZGWClient | None:
        service = cls.get_service(url)
        if not service:
            return None

        return service.build_client(**kwargs)

    @classmethod
    @deprecated(
        "The `get_auth_header` class method is deprecated and will be removed in 1.0.",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def get_auth_header(cls, url: str, **kwargs) -> dict | None:
        client = cls.get_client(url, **kwargs)
        if not client:
            return None

        return client.auth_header


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
