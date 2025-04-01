import time

import jwt
import requests_mock
from freezegun import freeze_time

from zgw_consumers.client import build_client
from zgw_consumers.constants import AuthTypes
from zgw_consumers.test.factories import ServiceFactory


def test_retry_request_on_403_auth_zgw():
    service = ServiceFactory.build(
        api_root="https://example.com/",
        auth_type=AuthTypes.zgw,
        client_id="my-client-id",
        secret="my-secret",
    )

    with requests_mock.Mocker() as m:
        m.get(
            "https://example.com/",
            status_code=403,
        )

        with freeze_time("2024-11-27T10:00:00+02:00"):
            initial_time = int(time.time())
            client = build_client(service)

        with freeze_time("2024-11-27T15:00:00+02:00"):  # 5h later
            later_time = int(time.time())
            with client:
                client.get("https://example.com/")

        history = m.request_history

        assert len(history) == 2

        first_request = history[0]
        first_token = first_request.headers["Authorization"].removeprefix("Bearer ")
        time1 = jwt.decode(
            first_token,
            service.secret,
            algorithms=["HS256"],
            options={"verify_exp": False},
        )["iat"]

        assert time1 == initial_time

        second_request = history[1]
        second_token = second_request.headers["Authorization"].removeprefix("Bearer ")
        time2 = jwt.decode(
            second_token,
            service.secret,
            algorithms=["HS256"],
            options={"verify_exp": False},
        )["iat"]

        assert time2 == later_time


def test_retry_request_on_403_auth_api_key():
    service = ServiceFactory.build(
        api_root="https://example.com/",
        auth_type=AuthTypes.api_key,
        header_key="Some-Auth-Header",
        header_value="some-api-key",
    )

    with requests_mock.Mocker() as m:
        m.get(
            "https://example.com/",
            status_code=403,
        )

        with freeze_time("2024-11-27T10:00:00+02:00"):
            client = build_client(service)

        with freeze_time("2024-11-27T15:00:00+02:00"):  # 5h later
            with client:
                client.get("https://example.com/")

        history = m.request_history

        assert len(history) == 1


def test_retry_request_on_403_no_auth():
    service = ServiceFactory.build(
        api_root="https://example.com/",
        auth_type=AuthTypes.no_auth,
    )

    with requests_mock.Mocker() as m:
        m.get(
            "https://example.com/",
            status_code=403,
        )

        with freeze_time("2024-11-27T10:00:00+02:00"):
            client = build_client(service)

        with freeze_time("2024-11-27T15:00:00+02:00"):  # 5h later
            with client:
                client.get("https://example.com/")

        history = m.request_history

        assert len(history) == 1
