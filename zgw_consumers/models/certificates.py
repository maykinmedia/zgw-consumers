from simple_certmanager.models import Certificate as NewCertificate


class Certificate(NewCertificate):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        proxy = True
