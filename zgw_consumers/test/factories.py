import factory

from zgw_consumers.models import Service


class UrlTrailingFaker(factory.Faker):
    def __init__(self, **kwargs):
        super().__init__("url", **kwargs)

    def generate(self, extra_kwargs=None):
        url: str = super().generate(extra_kwargs)
        # faker generates them with a trailing slash, but let's make sure this stays true
        # zgw_consumers.Service normalizes api_root to append missing trailing slashes
        if not url.endswith("/"):
            url = f"{url}/"
        return url


class ServiceFactory(factory.django.DjangoModelFactory):
    label = factory.Sequence(lambda n: f"API-{n}")
    api_root = UrlTrailingFaker()

    class Meta:
        model = Service
        django_get_or_create = ("api_root",)

    class Params:
        with_server_cert = factory.Trait(
            server_certificate=factory.SubFactory(
                "simple_certmanager.test.factories.CertificateFactory",
                public_certificate__filename="server.cert",
            ),
        )
        with_client_cert = factory.Trait(
            client_certificate=factory.SubFactory(
                "simple_certmanager.test.factories.CertificateFactory",
                public_certificate__filename="client.cert",
            ),
        )
