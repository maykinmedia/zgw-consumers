from dataclasses import dataclass
from datetime import date
from typing import Optional

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
    doel: str
    aanleiding: str
    toelichting: str
    indicatie_intern_of_extern: str
    handeling_initiator: str
    onderwerp: str
    handeling_behandelaar: str
    doorlooptijd: relativedelta
    servicenorm: Optional[relativedelta]
    opschorting_en_aanhouding_mogelijk: bool
    verlenging_mogelijk: bool
    verlengingstermijn: Optional[relativedelta]
    trefwoorden: list
    publicatie_indicatie: bool
    publicatietekst: str
    verantwoordingsrelatie: list
    producten_of_diensten: list
    # selectielijst_procestype: ProcesType
    statustypen: list
    resultaattypen: list
    eigenschappen: list
    informatieobjecttypen: list
    roltypen: list
    besluittypen: list
    deelzaaktypen: list

    begin_geldigheid: date
    einde_geldigheid: Optional[date]
    versiedatum: date
    concept: bool


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
    begin_geldigheid: date
    einde_geldigheid: Optional[date]
    concept: bool


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
