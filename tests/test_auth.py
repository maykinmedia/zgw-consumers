import time
from datetime import datetime, timezone

from django.core.cache import cache

import jwt
import pytest
import requests_mock
from freezegun import freeze_time

from zgw_consumers.client import ZGWAuth, build_client
from zgw_consumers.constants import AuthTypes
from zgw_consumers.test.factories import ServiceFactory


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


def test_zgw_auth_refresh_token():
    service = ServiceFactory.build(
        api_root="https://example.com/",
        auth_type=AuthTypes.zgw,
        client_id="my-client-id",
        secret="my-secret",
    )

    with freeze_time("2024-11-27T10:00:00+02:00"):
        auth = ZGWAuth(service)
        token = jwt.decode(auth._token, service.secret, algorithms=["HS256"])

        assert token["iat"] == int(time.time())

    with freeze_time("2024-11-27T15:00:00+02:00"):  # 5 hours later
        auth.refresh_token()
        token = jwt.decode(auth._token, service.secret, algorithms=["HS256"])

        assert token["iat"] == int(time.time())


@freeze_time("2025-04-01T11:52:13Z")
def test_jwt_exp_configuration():
    service = ServiceFactory.build(
        auth_type=AuthTypes.zgw,
        client_id="my-client-id",
        secret="my-secret",
        jwt_valid_for=5 * 60,  # 5 minutes
    )

    with (
        requests_mock.Mocker() as m,
        build_client(service) as client,
    ):
        m.get(requests_mock.ANY, status_code=200)

        resp = client.get("irrelevant")
        assert resp.status_code == 200

        auth_header = resp.request.headers["Authorization"]

    type, token = auth_header.split(" ")
    assert type == "Bearer"

    decoded = jwt.decode(token, "my-secret", algorithms=["HS256"])
    assert "exp" in decoded
    # https://www.rfc-editor.org/rfc/rfc7519#section-2 NumericDate (number of seconds
    # since epoch, in UTC)
    exp = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
    # 5 minutes later than "now"
    assert exp == datetime(2025, 4, 1, 11, 57, 13, tzinfo=timezone.utc)


@pytest.fixture
def oauth2_service():
    return ServiceFactory.build(
        api_root="https://example.com/",
        auth_type=AuthTypes.oauth2_client_credentials,
        client_id="my-client-id",
        secret="my-secret",
        oauth2_token_url="https://example.com/token/",
    )


def mock_token_response(m, access_token="mock-access-token", expires_in=3600):
    m.post(
        "https://example.com/token/",
        json={
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": expires_in,
        },
    )


def test_oauth2_token_is_added_to_the_headers(oauth2_service):
    with requests_mock.Mocker() as m:
        mock_token_response(m)
        m.get("https://example.com/irrelevant", text="OK")

        with build_client(oauth2_service) as client:
            resp = client.get("irrelevant")

        assert resp.status_code == 200
        last_req = m.request_history[-1]
        assert last_req.headers["Authorization"] == "Bearer mock-access-token"


def test_non_oauth2_auth_type_does_not_fetch_token():
    service = ServiceFactory.build(
        api_root="https://example.com/",
        auth_type=AuthTypes.no_auth,
    )

    with requests_mock.Mocker() as m:
        m.get("https://example.com/irrelevant", text="OK")

        with build_client(service) as client:
            resp = client.get("irrelevant")

        assert resp.status_code == 200
        assert not any(r.method == "POST" for r in m.request_history)


@freeze_time("2025-04-01T00:00:00Z")
def test_token_refresh_on_expiry(oauth2_service):
    with requests_mock.Mocker() as m:
        mock_token_response(m, access_token="first-token", expires_in=12)
        m.get("https://example.com/irrelevant", text="OK")

        with build_client(oauth2_service) as client:
            client.get("irrelevant")

        # force token expiry
        with freeze_time("2025-04-01T00:00:15Z"):
            mock_token_response(m, access_token="second-token")
            with build_client(oauth2_service) as client:
                client.get("irrelevant")

        # the second call should fetch a new token
        post_requests = [r for r in m.request_history if r.method == "POST"]
        assert len(post_requests) == 2


def test_token_is_cached(oauth2_service):
    with requests_mock.Mocker() as m:
        mock_token_response(m, access_token="cached-token")
        m.get("https://example.com/irrelevant", text="OK")

        # first call -> fetches token and caches it
        with build_client(oauth2_service) as client:
            client.get("irrelevant")

        # second call -> uses cached token (no POST expected)
        with build_client(oauth2_service) as client:
            client.get("irrelevant")

        post_requests = [r for r in m.request_history if r.method == "POST"]
        assert len(post_requests) == 1
