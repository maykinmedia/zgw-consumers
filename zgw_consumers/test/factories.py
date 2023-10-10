import factory
from faker.providers.internet import Provider as InternetProvider

from zgw_consumers.models import Service


class ApiRootProvider(InternetProvider):
    def api_root(self) -> str:
        base = self.url()
        # faker generates them with a trailing slash, but let's make sure this stays true
        # zgw_consumers.Service normalizes api_root to append missing trailing slashes
        if not base.endswith("/"):
            base = f"{base}/"
        page = self.uri_page()
        return f"{base}{page}"


factory.Faker.add_provider(ApiRootProvider)


class ServiceFactory(factory.django.DjangoModelFactory):
    label = factory.Sequence(lambda n: f"API-{n}")
    api_root = factory.Faker("api_root")

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
