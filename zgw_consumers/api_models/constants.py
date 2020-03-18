from djchoices import ChoiceItem, DjangoChoices


class VertrouwelijkheidsAanduidingen(DjangoChoices):
    openbaar = ChoiceItem("openbaar", label="Openbaar")
    beperkt_openbaar = ChoiceItem("beperkt_openbaar", label="Beperkt openbaar")
    intern = ChoiceItem("intern", label="Intern")
    zaakvertrouwelijk = ChoiceItem("zaakvertrouwelijk", label="Zaakvertrouwelijk")
    vertrouwelijk = ChoiceItem("vertrouwelijk", label="Vertrouwelijk")
    confidentieel = ChoiceItem("confidentieel", label="Confidentieel")
    geheim = ChoiceItem("geheim", label="Geheim")
    zeer_geheim = ChoiceItem("zeer_geheim", label="Zeer geheim")
