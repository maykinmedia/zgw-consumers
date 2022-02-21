import logging
from functools import lru_cache
from typing import Any, Dict, List, Tuple
from urllib.parse import parse_qs, urlparse

from django import forms
from django.contrib.admin import widgets
from django.db.models import Field
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from .constants import APITypes
from .models.services import NLXConfig, Service
from .nlx import ServiceType, get_nlx_services
from .utils import cache_on_request

logger = logging.getLogger(__name__)


# TODO: parallelize
@lru_cache()
def get_zaaktypen() -> Dict[Service, List[Dict[str, Any]]]:
    services = Service.objects.filter(api_type=APITypes.ztc)

    zaaktypen_per_service = {}

    for service in services:
        client = service.build_client()
        logger.debug("Fetching zaaktype list for service %r", service)
        zaaktypen_per_service[service] = []
        response = client.list("zaaktype")
        zaaktypen_per_service[service] += response["results"]
        while response["next"]:
            next_url = urlparse(response["next"])
            query = parse_qs(next_url.query)
            new_page = int(query["page"][0]) + 1
            query["page"] = [new_page]
            response = client.list(
                "zaaktype",
                query_params=query,
            )
            zaaktypen_per_service[service] += response["results"]

    return zaaktypen_per_service


def get_zaaktype_field(db_field: Field, request: HttpRequest, **kwargs):
    zaaktypen = get_zaaktypen()

    def _get_choice(zaaktype: dict) -> Tuple[str, str]:
        return (
            zaaktype["url"],
            f"{zaaktype['identificatie']} - {zaaktype['omschrijving']}",
        )

    choices = [
        (
            f"Service: {service.label}",
            [_get_choice(zaaktype) for zaaktype in _zaaktypen],
        )
        for service, _zaaktypen in zaaktypen.items()
    ]

    return forms.ChoiceField(
        label=db_field.verbose_name.capitalize(),
        widget=widgets.AdminRadioSelect(),
        choices=choices,
        required=False,
        help_text=db_field.help_text,
    )


def get_nlx_field(db_field: Field, request: HttpRequest, **kwargs):
    with cache_on_request(request, "_nlx_services", get_nlx_services) as cached:
        try:
            nlx_services = cached.value
        except Exception:
            logger.warning("Failed fetching the NLX services", exc_info=True)
            nlx_services = []

    nlx_outway = NLXConfig.get_solo().outway

    def _get_choice(service: ServiceType) -> Tuple[str, str]:
        org_id = service["organization"]["serial_number"]
        name = service["name"]
        url = f"{nlx_outway}{org_id}/{name}/"
        return (url, name)

    choices = [
        (
            f"{organization['name']} (ID: {organization['serial_number']})",
            [_get_choice(service) for service in services],
        )
        for organization, services in nlx_services
    ]
    choices.insert(0, (_("No NLX"), [("", "---------")]))

    return forms.ChoiceField(
        label=db_field.verbose_name.capitalize(),
        choices=choices,
        required=False,
        help_text=db_field.help_text,
    )
