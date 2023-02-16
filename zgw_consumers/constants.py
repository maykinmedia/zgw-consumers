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


class NLXDirectories(models.TextChoices):
    demo = "demo", _("Demo")
    preprod = "preprod", _("Pre-prod")
    prod = "prod", _("Prod")
