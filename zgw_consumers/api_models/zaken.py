from dataclasses import dataclass
from datetime import date
from typing import Union

from .base import ZGWModel


@dataclass
class Zaak(ZGWModel):
    url: str
    identificatie: str
    bronorganisatie: str
    omschrijving: str
    toelichting: str
    zaaktype: str
    registratiedatum: date
    startdatum: date
    einddatum_gepland: Union[date, None]
    uiterlijke_einddatum_afdoening: Union[date, None]
    publicatiedatum: Union[date, None]
    vertrouwelijkheidaanduiding: str
    status: str
    resultaat: str
    relevante_andere_zaken: list
    zaakgeometrie: dict
