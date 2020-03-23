from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

from .base import ZGWModel
from .constants import VertrouwelijkheidsAanduidingen


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
    einddatum: Optional[date]
    einddatum_gepland: Optional[date]
    uiterlijke_einddatum_afdoening: Optional[date]
    publicatiedatum: Optional[date]
    vertrouwelijkheidaanduiding: str
    status: str
    resultaat: str
    relevante_andere_zaken: list
    zaakgeometrie: dict

    def get_vertrouwelijkheidaanduiding_display(self):
        return VertrouwelijkheidsAanduidingen.values[self.vertrouwelijkheidaanduiding]


@dataclass
class Status(ZGWModel):
    url: str
    zaak: str
    statustype: str
    datum_status_gezet: datetime
    statustoelichting: str


@dataclass
class ZaakObject(ZGWModel):
    url: str
    zaak: str
    object: str
    object_type: str
    object_type_overige: str
    relatieomschrijving: str
