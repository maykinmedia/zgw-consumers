import json
import logging
from collections.abc import Iterable
from itertools import groupby

import requests
from ape_pie import APIClient
from requests import JSONDecodeError
from requests.models import PreparedRequest, Request, Response
from requests.utils import guess_json_utf

from .models import NLXConfig, Service

logger = logging.getLogger(__name__)


def _rewrite_url(value: str, rewrites: Iterable[tuple[str, str]]) -> str | None:
    for start, replacement in rewrites:
        if not value.startswith(start):
            continue

        return value.replace(start, replacement, 1)

    return None


class Rewriter:
    def __init__(self):
        self.rewrites: list[tuple[str, str]] = Service.objects.exclude(
            nlx=""
        ).values_list("api_root", "nlx")

    @property
    def reverse_rewrites(self) -> list[tuple[str, str]]:
        return [(to_value, from_value) for from_value, to_value in self.rewrites]

    def forwards(self, data: list | dict) -> None:
        """
        Rewrite URLs from from_value to to_value.
        """
        self._rewrite(data, self.rewrites)

    def backwards(self, data: list | dict) -> None:
        """
        Rewrite URLs from to_value to from_value.
        """
        self._rewrite(data, self.reverse_rewrites)

    def _rewrite(self, data: list | dict, rewrites: Iterable[tuple[str, str]]) -> None:
        if isinstance(data, list):
            new_items = []
            for item in data:
                if isinstance(item, str):
                    new_value = _rewrite_url(item, rewrites)
                    if new_value:
                        new_items.append(new_value)
                    else:
                        new_items.append(item)
                else:
                    self._rewrite(item, rewrites=rewrites)
                    new_items.append(item)

            # replace list elements
            assert len(new_items) == len(data)
            for i in range(len(data)):
                data[i] = new_items[i]
            return

        if not isinstance(data, dict):
            return

        for key, value in data.items():
            if isinstance(value, (dict, list)):
                self._rewrite(value, rewrites=rewrites)
                continue

            elif not isinstance(value, str):
                continue

            assert isinstance(value, str)

            rewritten = _rewrite_url(value, rewrites)
            if rewritten is not None:
                data[key] = rewritten


def nlx_rewrite_hook(response: Response, *args, **kwargs):
    try:
        json_data = response.json()
    # it may be a different content type than JSON! Checking for application/json
    # content type header is a bit annoying because there are alternatives like
    # application/hal+json :(
    except JSONDecodeError:
        return response

    # rewrite the JSON
    logger.debug(
        "NLX client: Rewriting response JSON to replace outway URLs",
        extra={"request": response.request},
    )
    # apply similar logic to response.json() itself
    encoding = (
        response.encoding
        or guess_json_utf(response.content)
        or response.apparent_encoding
    )
    assert encoding
    rewriter = Rewriter()
    rewriter.backwards(json_data)
    response._content = json.dumps(json_data).encode(encoding)

    return response


class NLXMixin:
    base_url: str

    def __init__(self, *args, nlx_base_url: str = "", **kwargs):
        super().__init__(*args, **kwargs)
        self.nlx_base_url = nlx_base_url

        if self.nlx_base_url:
            self.hooks["response"].insert(0, nlx_rewrite_hook)  # type: ignore

    def prepare_request(self, request: Request) -> PreparedRequest:
        prepared_request = super().prepare_request(request)  # type: ignore

        if not self.nlx_base_url:
            return prepared_request

        # change the actual URL being called so that it uses NLX
        # XXX: it would be really nice if at some point NLX would be just a normal HTTP
        # proxy so we can instead just map DB configuration to proxy setup.
        new_url = (original := prepared_request.url).replace(
            self.base_url, self.nlx_base_url, 1
        )
        logger.debug(
            "NLX client: URL %s rewritten to %s",
            original,
            new_url,
            extra={
                "original_url": original,
                "base_url": self.base_url,
                "nlx_base_url": self.nlx_base_url,
                "client": self,
            },
        )
        prepared_request.url = new_url

        return prepared_request


class NLXClient(NLXMixin, APIClient):
    """A :class:`ape_pie.APIClient` implementation that will take care of rewriting
    URLs with :external:ref:`an event hook <event-hooks>`.
    """

    pass


Organization = dict[str, str]
ServiceType = dict[str, str]


def get_nlx_services() -> list[tuple[Organization, list[ServiceType]]]:
    config = NLXConfig.get_solo()
    if not config.outway or not config.directory_url:
        return []

    directory = config.directory_url
    url = f"{directory}api/directory/list-services"

    cert = (
        (config.certificate.path, config.certificate_key.path)
        if (config.certificate and config.certificate_key)
        else None
    )

    response = requests.get(url, cert=cert)
    response.raise_for_status()

    services = response.json()["services"]
    services.sort(key=lambda s: (s["organization"]["serial_number"], s["name"]))

    services_per_organization = [
        (k, list(v)) for k, v in groupby(services, key=lambda s: s["organization"])
    ]
    return services_per_organization
