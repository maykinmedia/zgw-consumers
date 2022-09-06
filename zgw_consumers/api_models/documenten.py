from dataclasses import dataclass
from datetime import date
from typing import Optional

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
    bestandsomvang: Optional[int] = None
    formaat: str = ""  # noqa
    indicatie_gebruiksrecht: Optional[dict] = None
    inhoud: Optional[str] = None
    integriteit: Optional[dict] = None
    link: str = ""
    ondertekening: Optional[dict] = None
    ontvangstdatum: Optional[date] = None
    status: str = ""
    versie: int = 1
    verzenddatum: Optional[date] = None
    locked: bool = False

    def get_vertrouwelijkheidaanduiding_display(self):
        return VertrouwelijkheidsAanduidingen.values[self.vertrouwelijkheidaanduiding]
