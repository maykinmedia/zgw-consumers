from dataclasses import dataclass

from dateutil.relativedelta import relativedelta

from .base import ZGWModel
from .selectielijst import ProcesType, Resultaat


@dataclass
class ZaakType(ZGWModel):
    url: str
    catalogus: str
    identificatie: int
    omschrijving: str
    omschrijving_generiek: str
    vertrouwelijkheidaanduiding: str
    aanleiding: str
    toelichting: str
    doorlooptijd: str

    # selectielijst_procestype: ProcesType


@dataclass
class StatusType(ZGWModel):
    url: str
    zaaktype: str
    omschrijving: str
    omschrijving_generiek: str
    statustekst: str
    volgnummer: int
    is_eindstatus: bool


@dataclass
class InformatieObjectType(ZGWModel):
    url: str
    catalogus: str
    omschrijving: str
    vertrouwelijkheidaanduiding: str


@dataclass
class ResultaatType(ZGWModel):
    url: str
    zaaktype: ZaakType
    omschrijving: str
    resultaattypeomschrijving: str
    omschrijving_generiek: str
    selectielijstklasse: Resultaat
    toelichting: str
    archiefnominatie: str
    archiefactietermijn: relativedelta
    brondatum_archiefprocedure: dict
