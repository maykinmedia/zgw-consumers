from typing import List, Optional, Type
from urllib.parse import parse_qs, urlparse

from zds_client import Client

from zgw_consumers.api_models.base import ZGWModel, factory
from zgw_consumers.api_models.catalogi import Catalogus, InformatieObjectType
from zgw_consumers.concurrent import parallel
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service


def get_paginated_results(
    client: Client,
    resource: str,
    minimum: Optional[int] = None,
    test_func: Optional[callable] = None,
    *args,
    **kwargs,
) -> list:
    request_kwargs = kwargs.get("request_kwargs", {})
    request_params = request_kwargs.get("params", {})

    results = []
    response = client.list(resource, *args, **kwargs)

    def _get_results(response):
        _results = response["results"]
        if test_func:
            _results = [result for result in _results if test_func(result)]
        return _results

    results += _get_results(response)

    if minimum and len(results) >= minimum:
        return results

    while response.get("next"):
        next_url = urlparse(response["next"])
        query = parse_qs(next_url.query)
        new_page = int(query["page"][0])

        request_params["page"] = [new_page]
        request_kwargs["params"] = request_params
        kwargs["request_kwargs"] = request_kwargs

        response = client.list(resource, *args, **kwargs)
        results += _get_results(response)

        if minimum and len(results) >= minimum:
            return results

    return results


def _get_ztc_clients():
    services = Service.objects.filter(api_type=APITypes.ztc)
    clients = [service.build_client() for service in services]
    return clients


def _fetch_list(
    resource: str, clients: List[Client], model: Type[ZGWModel]
) -> List[ZGWModel]:
    def _fetch(client: Client):
        results = get_paginated_results(client, resource)
        return results

    with parallel() as executor:
        resp_data = executor.map(_fetch, clients)
        flattened = sum(resp_data, [])

    return factory(model, flattened)


def get_catalogi(clients: List[Client] = None):
    if clients is None:
        clients = _get_ztc_clients()

    return _fetch_list("catalogus", clients, Catalogus)


def get_informatieobjecttypen(
    clients: List[Client] = None,
) -> List[InformatieObjectType]:
    """
    Retrieve all informatieobjecttypen for all catalogi.
    """
    if clients is None:
        clients = _get_ztc_clients()

    catalogi = {cat.url: cat for cat in get_catalogi(clients=clients)}
    iots = _fetch_list("informatieobjecttype", clients, InformatieObjectType)

    # resolve relations
    for iot in iots:
        iot.catalogus = catalogi[iot.catalogus]

    return iots
