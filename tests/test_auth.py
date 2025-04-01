import time
from datetime import datetime, timezone

import jwt
import requests_mock
from freezegun import freeze_time

from zgw_consumers.client import ZGWAuth, build_client
from zgw_consumers.constants import AuthTypes
from zgw_consumers.test.factories import ServiceFactory


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
