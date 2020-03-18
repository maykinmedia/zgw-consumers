from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

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
    einddatum_gepland: Optional[date]
    uiterlijke_einddatum_afdoening: Optional[date]
    publicatiedatum: Optional[date]
    vertrouwelijkheidaanduiding: str
    status: str
    resultaat: str
    relevante_andere_zaken: list
    zaakgeometrie: dict


@dataclass
class Status(ZGWModel):
    url: str
    zaak: str
    statustype: str
    datum_status_gezet: datetime
    statustoelichting: str
