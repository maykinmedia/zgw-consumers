from typing import List, Optional, Type, TypedDict

from ape_pie.client import APIClient
from zds_client import Client

from .api_models.base import ZGWModel, factory
from .api_models.catalogi import Catalogus, InformatieObjectType
from .client import build_client
from .concurrent import parallel
from .constants import APITypes
from .models import Service


class PaginatedResponseData(TypedDict):
    count: int
    next: str
    previous: str
    results: list


def pagination_helper(
    client: APIClient,
    paginated_data: PaginatedResponseData,
    max_requests: Optional[int] = None,
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
                return
            response = client.get(next_url)
            num_requests += 1
            response.raise_for_status()
            data = response.json()
            yield from _iter(data, num_requests)

    return _iter(paginated_data)


def _get_ztc_clients():
    services = Service.objects.filter(api_type=APITypes.ztc)
    clients = [build_client(service) for service in services]
    return clients


def _fetch_list(
    path: str, clients: List[Client], model: Type[ZGWModel]
) -> List[ZGWModel]:
    def _fetch(client: Client):
        response = client.get(path)
        response.raise_for_status()
        data = response.json()
        all_data = pagination_helper(client, data)
        return all_data

    with parallel() as executor:
        resp_data = executor.map(_fetch, clients)
        flattened = sum(resp_data, [])

    return factory(model, flattened)


def get_catalogi(clients: List[Client] = None):
    if clients is None:
        clients = _get_ztc_clients()

    return _fetch_list("catalogussen", clients, Catalogus)


def get_informatieobjecttypen(
    clients: List[Client] = None,
) -> List[InformatieObjectType]:
    """
    Retrieve all informatieobjecttypen for all catalogi.
    """
    if clients is None:
        clients = _get_ztc_clients()

    catalogi = {cat.url: cat for cat in get_catalogi(clients=clients)}
    iots = _fetch_list("informatieobjecttypen", clients, InformatieObjectType)

    # resolve relations
    for iot in iots:
        iot.catalogus = catalogi[iot.catalogus]

    return iots
