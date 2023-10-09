import factory

from zgw_consumers.models import Service


class ServiceFactory(factory.django.DjangoModelFactory):
    label = factory.Sequence(lambda n: f"API-{n}")
    api_root = factory.Faker("url", schemes=["https"])

    class Meta:
        model = Service
        django_get_or_create = ("api_root",)

    class Params:
        with_server_cert = factory.Trait(
            server_certificate=factory.SubFactory(
                "simple_certmanager_ext.tests.factories.CertificateFactory",
                public_certificate__filename="server.cert",
            ),
        )
        with_client_cert = factory.Trait(
            client_certificate=factory.SubFactory(
                "simple_certmanager_ext.tests.factories.CertificateFactory",
                public_certificate__filename="client.cert",
            ),
        )
