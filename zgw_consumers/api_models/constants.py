from django.db import models
from django.utils.translation import gettext as _


class VertrouwelijkheidsAanduidingen(models.TextChoices):
    openbaar = "openbaar", "Openbaar"
    beperkt_openbaar = "beperkt_openbaar", "Beperkt openbaar"
    intern = "intern", "Intern"
    zaakvertrouwelijk = "zaakvertrouwelijk", "Zaakvertrouwelijk"
    vertrouwelijk = "vertrouwelijk", "Vertrouwelijk"
    confidentieel = "confidentieel", "Confidentieel"
    geheim = "geheim", "Geheim"
    zeer_geheim = "zeer_geheim", "Zeer geheim"


class RolTypes(models.TextChoices):
    natuurlijk_persoon = "natuurlijk_persoon", "Natuurlijk persoon"
    niet_natuurlijk_persoon = "niet_natuurlijk_persoon", "Niet-natuurlijk persoon"
    vestiging = "vestiging", "Vestiging"
    organisatorische_eenheid = "organisatorische_eenheid", "Organisatorische eenheid"
    medewerker = "medewerker", "Medewerker"


class RolOmschrijving(models.TextChoices):
    # "Kennis in dienst stellen van de behandeling van (een deel van) een zaak."
    adviseur = "adviseur", "Adviseur"
    # "De vakinhoudelijke behandeling doen van (een deel van) een zaak."
    behandelaar = "behandelaar", "Behandelaar"
    # "Vanuit eigen en objectief belang rechtstreeks betrokken "
    # "zijn bij de behandeling en/of de uitkomst van een zaak."
    belanghebbende = "belanghebbende", "Belanghebbende"
    # "Nemen van besluiten die voor de uitkomst van een zaak noodzakelijk zijn."
    beslisser = "beslisser", "Beslisser"
    # "Aanleiding geven tot de start van een zaak .."
    initiator = "initiator", "Initiator"
    # "Het eerste aanspreekpunt zijn voor vragen van burgers en bedrijven .."
    klantcontacter = "klantcontacter", "Klantcontacter"
    # "Er voor zorg dragen dat de behandeling van de zaak in samenhang "
    # "uitgevoerd wordt conform de daarover gemaakte afspraken."
    zaakcoordinator = "zaakcoordinator", "Zaakcoördinator"
    medeinitiator = "mede_initiator", "Mede-initiator"


class VervalRedenen(models.TextChoices):
    tijdelijk = "tijdelijk", "Besluit met tijdelijke werking"
    ingetrokken_overheid = "ingetrokken_overheid", "Besluit ingetrokken door overheid"
    ingetrokken_belanghebbende = (
        "ingetrokken_belanghebbende",
        "Besluit ingetrokken o.v.v. belanghebbende",
    )


class AardRelatieChoices(models.TextChoices):
    vervolg = "vervolg", _("Vervolg")
    bijdrage = "bijdrage", _("Bijdrage")
    onderwerp = "onderwerp", _("Onderwerp")
