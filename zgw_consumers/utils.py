import logging
from typing import Optional, TypedDict

from django.http import HttpRequest

from ape_pie.client import APIClient

logger = logging.getLogger(__name__)
NOTSET = object()


class cache_on_request:
    def __init__(self, request: HttpRequest, key: str, callback: callable):
        self.request = request
        self.key = key
        self.callback = callback

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass

    @property
    def value(self):
        # check if it's cached on the request
        cached_value = getattr(self.request, self.key, NOTSET)
        if cached_value is NOTSET:
            value = self.callback()
            setattr(self.request, self.key, value)
            cached_value = value
        return cached_value


class PaginatedResponseData(TypedDict):
    count: int
    next: str
    previous: str
    results: list


def pagination_helper(
    client: APIClient,
    paginated_data: PaginatedResponseData,
    max_requests: Optional[int] = None,
    **kwargs,
):
    """
    Fetch results from a paginated API endpoint, and optionally limit the number of
    requests to perform when fetching new pages by specifying the ``max_requests`` argument
    """

    def _iter(_data, num_requests=0):
        for result in _data["results"]:
            yield result
        if next_url := _data.get("next"):
            if max_requests and num_requests >= max_requests:
                logger.info(
                    "Number of requests while retrieving paginated results reached "
                    "maximum of %s requests, returning results",
                    max_requests,
                )
                return
            response = client.get(next_url, **kwargs)
            num_requests += 1
            response.raise_for_status()
            data = response.json()
            yield from _iter(data, num_requests)

    return _iter(paginated_data)
