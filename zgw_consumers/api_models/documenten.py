from dataclasses import dataclass
from datetime import date

from .base import ZGWModel
from .constants import VertrouwelijkheidsAanduidingen


@dataclass
class Document(ZGWModel):
    url: str  # bug: not required according to OAS
    identificatie: str  # bug: not required according to OAS
    bronorganisatie: str
    creatiedatum: date
    titel: str
    vertrouwelijkheidaanduiding: str  # bug: not required according to OAS
    auteur: str
    taal: str
    informatieobjecttype: str

    beschrijving: str = ""
    bestandsnaam: str = ""
    bestandsomvang: int | None = None
    formaat: str = ""
    indicatie_gebruiksrecht: dict | None = None
    inhoud: str | None = None
    integriteit: dict | None = None
    link: str = ""
    ondertekening: dict | None = None
    ontvangstdatum: date | None = None
    status: str = ""
    versie: int = 1
    verzenddatum: date | None = None
    locked: bool = False

    def get_vertrouwelijkheidaanduiding_display(self):
        return VertrouwelijkheidsAanduidingen(self.vertrouwelijkheidaanduiding).label
