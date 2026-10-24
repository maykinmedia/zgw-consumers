import logging
from collections.abc import Callable, Iterable
from typing import NotRequired, TypedDict

from django.http import HttpRequest

from ape_pie.client import APIClient

logger = logging.getLogger(__name__)


class NotSet:
    pass


NOTSET = NotSet()


class cache_on_request[T]:
    def __init__(self, request: HttpRequest, key: str, callback: Callable[[], T]):

        self.request = request
        self.key = key
        self.callback = callback

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass

    @property
    def value(self) -> T:
        # check if it's cached on the request
        cached_value = getattr(self.request, self.key, NOTSET)
        if isinstance(cached_value, NotSet):
            value = self.callback()
            setattr(self.request, self.key, value)
            cached_value = value
        return cached_value


class PaginatedResponseData[T](TypedDict):
    count: int
    next: NotRequired[str | None]
    previous: NotRequired[str | None]
    results: Iterable[T]


def pagination_helper[T](
    client: APIClient,
    paginated_data: PaginatedResponseData[T],
    max_requests: int | None = None,
    **kwargs,
) -> Iterable[T | object]:
    """
    Fetch results from a paginated API endpoint, and optionally limit the number of
    requests to perform when fetching new pages by specifying the ``max_requests``
    argument.
    """

    def _iter(_data: PaginatedResponseData[T], num_requests=0):
        yield from _data["results"]
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
