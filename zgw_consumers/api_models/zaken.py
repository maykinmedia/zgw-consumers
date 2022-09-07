from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Optional

from .base import ZGWModel
from .catalogi import Eigenschap
from .constants import RolOmschrijving, RolTypes, VertrouwelijkheidsAanduidingen


@dataclass
class Zaak(ZGWModel):
    url: str  # bug: not required according to OAS
    bronorganisatie: str
    zaaktype: str
    identificatie: str  # bug: not required according to OAS
    registratiedatum: date  # bug: not required according to OAS
    verantwoordelijke_organisatie: str
    startdatum: date
    vertrouwelijkheidaanduiding: str  # bug: not required according to OAS

    omschrijving: str = ""
    toelichting: str = ""
    einddatum: Optional[date] = None
    einddatum_gepland: Optional[date] = None
    uiterlijke_einddatum_afdoening: Optional[date] = None
    publicatiedatum: Optional[date] = None
    status: Optional[str] = None
    resultaat: Optional[str] = None
    relevante_andere_zaken: list = field(default_factory=list)
    zaakgeometrie: dict = field(default_factory=dict)

    def get_vertrouwelijkheidaanduiding_display(self):
        return VertrouwelijkheidsAanduidingen.values[self.vertrouwelijkheidaanduiding]


@dataclass
class Status(ZGWModel):
    url: str  # bug: not required according to OAS
    zaak: str
    statustype: str
    datum_status_gezet: datetime
    statustoelichting: str = ""


@dataclass
class ZaakObject(ZGWModel):
    url: str  # bug: not required according to OAS
    zaak: str
    object_type: str
    object: str = ""
    object_type_overige: str = ""
    relatieomschrijving: str = ""
    object_identificatie: dict = field(default_factory=dict)


@dataclass
class ZaakEigenschap(ZGWModel):
    url: str  # bug: not required according to OAS
    # uuid: uuid.UUID
    zaak: str
    eigenschap: str
    waarde: str
    naam: str = ""

    def get_waarde(self) -> Any:
        assert isinstance(
            self.eigenschap, Eigenschap
        ), "Ensure eigenschap has been resolved"
        return self.eigenschap.to_python(self.waarde)


@dataclass
class Resultaat(ZGWModel):
    url: str  # bug: not required according to OAS
    zaak: str
    resultaattype: str
    toelichting: str = ""


@dataclass
class Rol(ZGWModel):
    url: str  # bug: not required according to OAS
    zaak: str
    betrokkene_type: str
    roltype: str
    roltoelichting: str
    betrokkene: str = ""
    omschrijving: str = ""
    omschrijving_generiek: str = ""
    registratiedatum: Optional[datetime] = None
    indicatie_machtiging: str = ""
    betrokkene_identificatie: dict = field(default_factory=dict)

    def get_betrokkene_type_display(self):
        return RolTypes.values[self.betrokkene_type]

    def get_omschrijving_generiek_display(self):
        return RolOmschrijving.values[self.omschrijving_generiek]


@dataclass
class ZaakInformatieObject(ZGWModel):
    url: str  # bug: not required according to OAS
    informatieobject: str
    zaak: str
    aard_relatie_weergave: str = ""
    titel: str = ""
    beschrijving: str = ""
    registratiedatum: Optional[datetime] = None
