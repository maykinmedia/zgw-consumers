from django.db import models
from django.utils.translation import gettext_lazy as _


class APITypes(models.TextChoices):
    ac = "ac", _("AC (Authorizations)")
    nrc = "nrc", _("NRC (Notifications)")

    zrc = "zrc", _("ZRC (Zaken)")
    ztc = "ztc", _("ZTC (Zaaktypen)")
    drc = "drc", _("DRC (Informatieobjecten)")
    brc = "brc", _("BRC (Besluiten)")

    cmc = "cmc", _("Contactmomenten API")
    kc = "kc", _("Klanten API")
    vrc = "vrc", _("Verzoeken API")

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
