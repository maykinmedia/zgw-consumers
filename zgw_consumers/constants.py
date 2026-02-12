from django.db import models
from django.utils.translation import gettext_lazy as _


class APITypes(models.TextChoices):
    ac = "ac", _("AC (Authorizations)")
    nrc = "nrc", _("NRC (Notifications)")
    zrc = "zrc", _("ZRC (Zaken)")
    ztc = "ztc", _("ZTC (Zaaktypen)")
    drc = "drc", _("DRC (Informatieobjecten)")
    brc = "brc", _("BRC (Besluiten)")
    rc = "rc", _("Referentielijsten API")
    kic = "kic", _("Klantinteracties API")
    oc = "oc", _("Organisatie API")
    ic = "ic", _("Identiteit API")
    pc = "pc", _("Producten API")
    ptc = "ptc", _("Producttypen API")
    vrc = "vrc", _("Verzoeken API")
    tc = "tc", _("Taken API")
    bc = "bc", _("Berichten API")

    # XXX: Deprecated choices, will be removed in the next major release
    # Note: Update data migration to handle this change
    cmc = "cmc", _("Contactmomenten API - (Deprecated)")
    kc = "kc", _("Klanten API - (Deprecated)")

    orc = "orc", _("ORC (Overige)")


class AuthTypes(models.TextChoices):
    no_auth = "no_auth", _("No authorization")
    api_key = "api_key", _("API key")
    zgw = "zgw", _("ZGW client_id + secret")
    oauth2_client_credentials = (
        "oauth2_client_credentials",
        _("OAuth2 client credentials flow"),
    )


class NLXDirectories(models.TextChoices):
    demo = "demo", _("Demo")
    prod = "prod", _("Prod")
