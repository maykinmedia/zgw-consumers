import pytest
import requests_mock
from ape_pie import APIClient
from simple_certmanager.constants import CertificateTypes
from simple_certmanager.test.factories import CertificateFactory

from zgw_consumers.client import ServiceConfigAdapter
from zgw_consumers.constants import AuthTypes
from zgw_consumers.test.factories import ServiceFactory

pytestmark = [pytest.mark.usefixtures("temp_private_root")]


@pytest.fixture
def client_cert_only(db):
    return CertificateFactory.create(
        label="Gateway client certificate",
        type=CertificateTypes.cert_only,
        public_certificate__filename="client_cert.pem",
    )


@pytest.fixture
def client_cert_and_privkey(db):
    return CertificateFactory.create(
        label="Gateway client certificate",
        with_private_key=True,
        public_certificate__filename="client_cert.pem",
        private_key__filename="client_key.pem",
    )


@pytest.fixture
def server_cert(db):
    return CertificateFactory.create(
        label="Gateway server certificate",
        type=CertificateTypes.cert_only,
        public_certificate__filename="server.pem",
    )


def test_no_server_cert_specified():
    service = ServiceFactory.build()
    adapter = ServiceConfigAdapter(service)

    client = APIClient.configure_from(adapter)

    assert client.verify is True  # not just truthy, but identity check


def test_server_cert_specified(server_cert):
    service = ServiceFactory.build(server_certificate=server_cert)
    adapter = ServiceConfigAdapter(service)

    client = APIClient.configure_from(adapter)

    assert client.verify == server_cert.public_certificate.path


def test_no_client_cert_specified():
    service = ServiceFactory.build()
    adapter = ServiceConfigAdapter(service)

    client = APIClient.configure_from(adapter)

    assert client.cert is None


def test_client_cert_only_public_cert_specified(client_cert_only):
    service = ServiceFactory.build(client_certificate=client_cert_only)
    adapter = ServiceConfigAdapter(service)

    client = APIClient.configure_from(adapter)

    assert client.cert == client_cert_only.public_certificate.path


def test_client_cert_public_cert_and_privkey_specified(client_cert_and_privkey):
    service = ServiceFactory.build(client_certificate=client_cert_and_privkey)
    adapter = ServiceConfigAdapter(service)

    client = APIClient.configure_from(adapter)

    assert client.cert == (
        client_cert_and_privkey.public_certificate.path,
        client_cert_and_privkey.private_key.path,
    )


def test_no_auth():
    service = ServiceFactory.build(auth_type=AuthTypes.no_auth)
    adapter = ServiceConfigAdapter(service)

    client = APIClient.configure_from(adapter)

    assert client.auth is None


def test_api_key_auth():
    service = ServiceFactory.build(
        api_root="https://example.com/",
        auth_type=AuthTypes.api_key,
        header_key="Some-Auth-Header",
        header_value="some-api-key",
    )
    adapter = ServiceConfigAdapter(service)
    client = APIClient.configure_from(adapter)

    assert client.auth is not None

    with requests_mock.Mocker() as m, client:
        m.get("https://example.com/foo")

        client.get("foo")

    headers = m.last_request.headers
    assert "Some-Auth-Header" in headers
    assert headers["Some-Auth-Header"] == "some-api-key"


def test_zgw_auth():
    service = ServiceFactory.build(
        api_root="https://example.com/",
        auth_type=AuthTypes.zgw,
        client_id="my-client-id",
        secret="my-secret",
    )
    adapter = ServiceConfigAdapter(service)
    client = APIClient.configure_from(adapter)

    assert client.auth is not None

    with requests_mock.Mocker() as m, client:
        m.get("https://example.com/foo")

        client.get("foo")

    headers = m.last_request.headers
    assert "Authorization" in headers


def test_default_timeout():
    service = ServiceFactory.build(api_root="https://example.com/")
    adapter = ServiceConfigAdapter(service)
    client = APIClient.configure_from(adapter)

    with requests_mock.Mocker() as m, client:
        m.get("https://example.com/foo")

        client.get("foo")

    timeout = m.last_request.timeout
    assert timeout == 10


def test_custom_timeout():
    service = ServiceFactory.build(api_root="https://example.com/", timeout=30)
    adapter = ServiceConfigAdapter(service)
    client = APIClient.configure_from(adapter)

    with requests_mock.Mocker() as m, client:
        m.get("https://example.com/foo")

        client.get("foo")

    timeout = m.last_request.timeout
    assert timeout == 30
