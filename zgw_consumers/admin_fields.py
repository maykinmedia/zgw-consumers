import logging

from django import forms
from django.db.models import Field
from django.http import HttpRequest
from django.utils.translation import gettext as _

from .models.services import NLXConfig
from .nlx import ServiceType, get_nlx_services
from .utils import cache_on_request

logger = logging.getLogger(__name__)


def get_nlx_field(db_field: Field, request: HttpRequest, **kwargs):
    with cache_on_request(request, "_nlx_services", get_nlx_services) as cached:
        try:
            nlx_services = cached.value
        except Exception:
            logger.warning("Failed fetching the NLX services", exc_info=True)
            nlx_services = []

    nlx_outway = NLXConfig.get_solo().outway

    def _get_choice(service: ServiceType) -> tuple[str, str]:
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
