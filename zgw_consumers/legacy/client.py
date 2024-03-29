import logging
import warnings
from typing import IO, Any, Dict, List, Optional, Union
from urllib.parse import urljoin

from django.utils.module_loading import import_string

import yaml
from zds_client import Client, ClientAuth
from zds_client.oas import schema_fetcher

from ..settings import get_setting

__all__ = [
    "get_client_class",
    "load_schema_file",
    "ZGWClient",
    "UnknownService",
    "ClientAuth",
]

logger = logging.getLogger(__name__)

Object = Dict[str, Any]


def get_client_class() -> type:
    client_class = get_setting("ZGW_CONSUMERS_CLIENT_CLASS")
    Client = import_string(client_class)
    return Client


def load_schema_file(file: IO):
    spec = yaml.safe_load(file)
    return spec


class ZGWClient(Client):
    def __init__(
        self,
        *args,
        auth_value: Optional[Dict[str, str]] = None,
        schema_url: str = "",
        schema_file: IO = None,
        client_certificate_path=None,
        client_private_key_path=None,
        server_certificate_path=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        warnings.warn(
            f"{self.__class__.__name__} is deprecated and will be removed in the next major release. "
            "Instead, use the new `ape_pie.APIClient` or `zgw_consumers.nlx.NLXClient`.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.auth_value = auth_value
        self.schema_url = schema_url
        self.schema_file = schema_file
        self.client_certificate_path = client_certificate_path
        self.client_private_key_path = client_private_key_path
        self.server_certificate_path = server_certificate_path

    def fetch_schema(self) -> None:
        """support custom OAS resolution"""
        if self.schema_file:
            logger.info("Loaded schema from file '%s'", self.schema_file)
            self._schema = load_schema_file(self.schema_file)
        else:
            url = self.schema_url or urljoin(self.base_url, "schema/openapi.yaml")
            logger.info("Fetching schema at '%s'", url)
            self._schema = schema_fetcher.fetch(url, {"v": "3"})

    def pre_request(self, method: str, url: str, kwargs: Optional[dict] = None):
        """
        Add authorization header to requests for APIs without jwt.
        """
        kwargs = kwargs or {}

        if not self.auth and self.auth_value:
            headers = kwargs.get("headers", {})
            headers.update(self.auth_value)

        super_kwargs = {"kwargs": kwargs}

        return super().pre_request(method, url, **super_kwargs)

    @property
    def auth_header(self) -> dict:
        if self.auth:
            return self.auth.credentials()

        return self.auth_value or {}

    def request(
        self,
        path: str,
        operation: str,
        method="GET",
        expected_status=200,
        request_kwargs: Optional[dict] = None,
        **kwargs,
    ) -> Union[List[Object], Object]:
        if self.server_certificate_path:
            kwargs.update({"verify": self.server_certificate_path})

        if self.client_certificate_path:
            if self.client_private_key_path:
                kwargs.update(
                    {
                        "cert": (
                            self.client_certificate_path,
                            self.client_private_key_path,
                        )
                    }
                )
            else:
                kwargs.update({"cert": self.client_certificate_path})

        return super().request(
            path, operation, method, expected_status, request_kwargs, **kwargs
        )


class UnknownService(Exception):
    pass
