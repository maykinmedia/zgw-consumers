from dataclasses import dataclass
from datetime import date

from .base import ZGWModel
from .constants import VervalRedenen


@dataclass
class Besluit(ZGWModel):
    url: str  # bug: not required according to OAS
    identificatie: str  # bug: not required according to OAS
    verantwoordelijke_organisatie: str
    besluittype: str
    datum: date
    ingangsdatum: date

    zaak: str = ""
    toelichting: str = ""
    bestuursorgaan: str = ""
    vervaldatum: date | None = None
    vervalreden: str = ""
    vervalreden_weergave: str = ""
    publicatiedatum: date | None = None
    verzenddatum: date | None = None
    uiterlijke_reactiedatum: date | None = None

    def get_vervalreden_display(self) -> str:
        return VervalRedenen(self.vervalreden).label


@dataclass
class BesluitDocument(ZGWModel):
    url: str  # bug: not required according to OAS
    informatieobject: str
    besluit: str
