from django.utils.translation import ugettext_lazy as _

from djchoices import ChoiceItem, DjangoChoices


class APITypes(DjangoChoices):
    ac = ChoiceItem("ac", _("AC (Authorizations)"))
    nrc = ChoiceItem("nrc", _("NRC (Notifications)"))

    zrc = ChoiceItem("zrc", _("ZRC (Zaken)"))
    ztc = ChoiceItem("ztc", _("ZTC (Zaaktypen)"))
    drc = ChoiceItem("drc", _("DRC (Informatieobjecten)"))
    brc = ChoiceItem("brc", _("BRC (Besluiten)"))
    kic = ChoiceItem("kic", _("KIC (Klantinteracties)"))

    orc = ChoiceItem("orc", _("ORC (Overige)"))


class AuthTypes(DjangoChoices):
    no_auth = ChoiceItem("no_auth", _("No authorization"))
    api_key = ChoiceItem("api_key", _("API key"))
    zgw = ChoiceItem("zgw", _("ZGW client_id + secret"))
