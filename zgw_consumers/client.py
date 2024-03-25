import logging
import time
from dataclasses import dataclass
from typing import Any, TypeVar

import jwt
from ape_pie import APIClient
from requests.auth import AuthBase
from requests.models import PreparedRequest

from zgw_consumers.constants import AuthTypes
from zgw_consumers.models import Service

from .nlx import NLXClient

logger = logging.getLogger(__name__)


ClientT = TypeVar("ClientT", bound=APIClient)


def build_client(
    service: Service, client_factory: type[ClientT] = NLXClient, **kwargs
) -> ClientT:
    """
    Build a client for a given :class:`zgw_consumers.models.Service`.
    """
    config_adapter = ServiceConfigAdapter(service)
    return client_factory.configure_from(
        config_adapter, nlx_base_url=service.nlx, **kwargs
    )


@dataclass
class ServiceConfigAdapter:
    """An implementation of :class:`ape_pie.ConfigAdapter` that will extract session kwargs
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

        match self.service.auth_type:
            case AuthTypes.api_key:
                kwargs["auth"] = APIKeyAuth(
                    header=self.service.header_key,
                    key=self.service.header_value,
                )
            case AuthTypes.zgw:
                kwargs["auth"] = ZGWAuth(service=self.service)

        # set timeout for the requests
        kwargs["timeout"] = self.service.timeout

        return kwargs


@dataclass
class APIKeyAuth(AuthBase):
    """API Key based :class:`requests.auth.AuthBase` implementation."""

    header: str
    key: str

    def __call__(self, request: PreparedRequest):
        request.headers[self.header] = self.key
        return request


@dataclass
class ZGWAuth(AuthBase):
    """
    :class:`requests.auth.AuthBase` implementation for ZGW APIs auth.
    """

    service: Service

    def __post_init__(self):
        # Generate the JWT Bearer token. Ported from gemma-zds-client ClientAuth.
        payload = {
            # standard claims
            "iss": self.service.client_id,
            "iat": int(time.time()),
            # custom claims
            "client_id": self.service.client_id,
            "user_id": self.service.user_id,
            "user_representation": self.service.user_representation,
        }

        self._token: str = jwt.encode(payload, self.service.secret, algorithm="HS256")

    def __call__(self, request: PreparedRequest):
        request.headers["Authorization"] = f"Bearer {self._token}"
        return request
