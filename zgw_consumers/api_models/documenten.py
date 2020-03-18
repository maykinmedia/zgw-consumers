from dataclasses import dataclass
from datetime import date
from typing import Optional

from .base import ZGWModel
from .constants import VertrouwelijkheidsAanduidingen


@dataclass
class Document(ZGWModel):
    url: str
    auteur: str
    identificatie: str
    beschrijving: str
    bestandsnaam: str
    bestandsomvang: int
    bronorganisatie: str
    creatiedatum: date
    formaat: str  # noqa
    indicatie_gebruiksrecht: dict
    informatieobjecttype: str
    inhoud: str
    integriteit: dict
    link: str
    ondertekening: dict
    ontvangstdatum: Optional[date]
    status: str
    taal: str
    titel: str
    vertrouwelijkheidaanduiding: str
    verzenddatum: Optional[date]

    def get_vertrouwelijkheidaanduiding_display(self):
        return VertrouwelijkheidsAanduidingen.values[self.vertrouwelijkheidaanduiding]
