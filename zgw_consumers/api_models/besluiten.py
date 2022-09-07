from dataclasses import dataclass
from datetime import date
from typing import Optional

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
    vervaldatum: Optional[date] = None
    vervalreden: str = ""
    vervalreden_weergave: str = ""
    publicatiedatum: Optional[date] = None
    verzenddatum: Optional[date] = None
    uiterlijke_reactiedatum: Optional[date] = None

    def get_vervalreden_display(self) -> str:
        return VervalRedenen.labels[self.vervalreden]


@dataclass
class BesluitDocument(ZGWModel):
    url: str  # bug: not required according to OAS
    informatieobject: str
    besluit: str
