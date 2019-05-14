from django.utils.translation import ugettext_lazy as _

from djchoices import ChoiceItem, DjangoChoices


class APITypes(DjangoChoices):
    ac = ChoiceItem("ac", _("AC (Authorizations)"))
    nrc = ChoiceItem("nrc", _("NRC (Notifications)"))

    zrc = ChoiceItem("zrc", _("ZRC (Zaken)"))
    ztc = ChoiceItem("ztc", _("ZTC (Zaaktypen)"))
    drc = ChoiceItem("drc", _("DRC (Informatieobjecten"))
    brc = ChoiceItem("brc", _("BRC (Besluiten)"))

    orc = ChoiceItem("orc", _("ORC (Overige)"))
