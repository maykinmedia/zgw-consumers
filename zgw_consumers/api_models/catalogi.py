from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Union

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

from .base import Model, ZGWModel, factory


@dataclass
class Catalogus(ZGWModel):
    url: str  # bug: not required according to OAS
    domein: str
    rsin: str
    contactpersoon_beheer_naam: str
    contactpersoon_beheer_emailadres: str = ""
    contactpersoon_beheer_telefoonnummer: str = ""
    besluittypen: list = field(default_factory=list)
    informatieobjecttypen: list = field(default_factory=list)
    zaaktypen: list = field(default_factory=list)


@dataclass
class ZaakType(ZGWModel):
    url: str  # bug: not required according to OAS
    catalogus: str
    identificatie: str  # bug: not required according to OAS
    omschrijving: str
    vertrouwelijkheidaanduiding: str
    doel: str
    aanleiding: str
    indicatie_intern_of_extern: str
    handeling_initiator: str
    onderwerp: str
    handeling_behandelaar: str
    doorlooptijd: relativedelta
    opschorting_en_aanhouding_mogelijk: bool
    verlenging_mogelijk: bool
    publicatie_indicatie: bool
    producten_of_diensten: list
    besluittypen: list
    begin_geldigheid: date
    versiedatum: date

    omschrijving_generiek: str = ""
    toelichting: str = ""
    servicenorm: Optional[relativedelta] = None
    verlengingstermijn: Optional[relativedelta] = None
    trefwoorden: list = field(default_factory=list)
    publicatietekst: str = ""
    verantwoordingsrelatie: list = field(default_factory=list)
    # selectielijst_procestype: ProcesType
    statustypen: list = field(default_factory=list)
    resultaattypen: list = field(default_factory=list)
    eigenschappen: list = field(default_factory=list)
    informatieobjecttypen: list = field(default_factory=list)
    roltypen: list = field(default_factory=list)
    deelzaaktypen: list = field(default_factory=list)

    einde_geldigheid: Optional[date] = None
    concept: bool = False


@dataclass
class StatusType(ZGWModel):
    url: str  # bug: not required according to OAS
    zaaktype: str
    omschrijving: str
    volgnummer: int
    omschrijving_generiek: str = ""
    statustekst: str = ""
    is_eindstatus: bool = False


@dataclass
class InformatieObjectType(ZGWModel):
    url: str  # bug: not required according to OAS
    catalogus: str
    omschrijving: str
    vertrouwelijkheidaanduiding: str
    begin_geldigheid: date
    einde_geldigheid: Optional[date] = None
    concept: bool = False


@dataclass
class ResultaatType(ZGWModel):
    url: str  # bug: not required according to OAS
    zaaktype: str
    omschrijving: str
    resultaattypeomschrijving: str
    selectielijstklasse: str

    omschrijving_generiek: str = ""
    toelichting: str = ""
    archiefnominatie: str = ""
    archiefactietermijn: Optional[relativedelta] = None
    brondatum_archiefprocedure: Optional[dict] = None


@dataclass
class EigenschapSpecificatie(Model):
    formaat: str
    lengte: str
    kardinaliteit: str
    groep: str = ""
    waardenverzameling: list = field(default_factory=list)


EIGENSCHAP_FORMATEN = {
    "tekst": str,
    "getal": lambda val: Decimal(val.replace(",", ".")),
    "datum": date.fromisoformat,
    "datum_tijd": parse,
}


@dataclass
class Eigenschap(ZGWModel):
    url: str  # bug: not required according to OAS
    zaaktype: str
    naam: str
    definitie: str
    specificatie: dict
    toelichting: str = ""

    def __post_init__(self):
        super().__post_init__()
        self.specificatie = factory(EigenschapSpecificatie, self.specificatie)

    def to_python(self, value: str) -> Union[str, Decimal, date, datetime]:
        """
        Cast the string value into the appropriate python type based on the spec.
        """
        formaat = self.specificatie.formaat
        assert formaat in EIGENSCHAP_FORMATEN, f"Unknown format {formaat}"

        converter = EIGENSCHAP_FORMATEN[formaat]
        return converter(value)


@dataclass
class RolType(ZGWModel):
    url: str  # bug: not required according to OAS
    zaaktype: str
    omschrijving: str
    omschrijving_generiek: str


@dataclass
class BesluitType(ZGWModel):
    url: str  # bug: not required according to OAS
    catalogus: str
    zaaktypen: List[str]
    publicatie_indicatie: bool
    informatieobjecttypen: List[str]
    begin_geldigheid: date

    omschrijving: str = ""
    omschrijving_generiek: str = ""
    besluitcategorie: str = ""
    reactietermijn: Optional[relativedelta] = None
    publicatietekst: str = ""
    publicatietermijn: Optional[relativedelta] = None
    toelichting: str = ""
    einde_geldigheid: Optional[date] = None
    concept: bool = False
