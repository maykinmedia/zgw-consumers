import time

import jwt
import pytest
from freezegun import freeze_time

from zgw_consumers.client import ZGWAuth
from zgw_consumers.constants import AuthTypes
from zgw_consumers.test.factories import ServiceFactory


@pytest.mark.django_db
def test_zgw_auth_refresh_token():
    service = ServiceFactory.create(
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
