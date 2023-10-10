import logging
from dataclasses import dataclass, field
from typing import Any, TypeVar

from requests.auth import AuthBase
from requests.models import PreparedRequest
from zds_client import ClientAuth

from zgw_consumers.constants import AuthTypes
from zgw_consumers.models import Service

# For backwards compatibility:
from .legacy.client import UnknownService, ZGWClient, get_client_class, load_schema_file
from .nlx import NLXClient

logger = logging.getLogger(__name__)


ClientT = TypeVar("ClientT", bound=NLXClient)


def build_client(
    service: Service, client_factory: type[ClientT] = NLXClient, **kwargs
) -> ClientT:
    """
    Build a client for a given :class:`zgw_consumers.models.Service`.
    """
    config_provider = ServiceConfigProvider(service)
    return client_factory.configure_from(
        config_provider, nlx_base_url=service.nlx, **kwargs
    )


@dataclass
class ServiceConfigProvider:
    """An ``ape-pie`` config provider that will extract session kwargs
    from a given :class:`zgw_consumers.models.Service`.
    """

    service: Service

    def get_client_base_url(self) -> str:
        return self.service.api_root

    def get_client_session_kwargs(self) -> dict[str, Any]:
        kwargs = {}

        # mTLS: verify server certificate if configured
        if server_cert := self.service.server_certificate:
            # NOTE: this only works with a file-system based storage!
            kwargs["verify"] = server_cert.public_certificate.path

        # mTLS: offer client certificate if configured
        if client_cert := self.service.client_certificate:
            client_cert_path = client_cert.public_certificate.path
            # decide between single cert or cert,key tuple variant
            kwargs["cert"] = (
                (client_cert_path, privkey.path)
                if (privkey := client_cert.private_key)
                else client_cert_path
            )

        if self.service.auth_type is AuthTypes.api_key:
            kwargs["auth"] = APIKeyAuth(
                header=self.service.header_key,
                key=self.service.header_value,
            )
        elif self.service.auth_type is AuthTypes.zgw:
            kwargs["auth"] = ZGWAuth(service=self.service)

        return kwargs


@dataclass
class APIKeyAuth(AuthBase):
    header: str
    key: str

    def __call__(self, request: PreparedRequest):
        request.headers[self.header] = self.key
        return request


@dataclass
class ZGWAuth(AuthBase):
    service: Service
    auth: ClientAuth = field(init=False)

    def __post_init__(self):
        self.auth = ClientAuth(
            client_id=self.service.client_id,
            secret=self.service.secret,
            user_id=self.service.user_id,
            user_representation=self.service.user_representation,
        )

    def __call__(self, request: PreparedRequest):
        request.headers.update(self.auth.credentials())
        return request
