"""
The service credentials (``secret`` and ``header_value``) are write-only in the admin.

The stored values must never end up in a response - only a masked hint - so that
an XSS in the admin cannot exfiltrate them.
"""

from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Permission, User
from django.test import Client
from django.urls import reverse

import pytest
import requests_mock
from pytest_django.asserts import assertContains, assertNotContains

from zgw_consumers.admin_forms import mask
from zgw_consumers.constants import APITypes, AuthTypes
from zgw_consumers.models import Service
from zgw_consumers.test.factories import ServiceFactory

SECRET = "zgw-secret-that-is-sufficiently-long"
API_KEY = "api-key-that-is-sufficiently-long"


@pytest.fixture(autouse=True)
def mock_connection_check():
    # the change page performs a connection check against the API root
    with requests_mock.Mocker() as m:
        m.get(requests_mock.ANY, status_code=200)
        yield m


@pytest.fixture
def service() -> Service:
    return ServiceFactory.create(
        api_root="https://example.com/",
        # the factory leaves it blank, but the change form requires it
        api_type=APITypes.zrc,
        auth_type=AuthTypes.zgw,
        client_id="my-client-id",
        secret=SECRET,
        header_key="Authorization",
        header_value=API_KEY,
    )


@pytest.fixture
def read_only_client(db) -> Client:
    user = User.objects.create_user(username="viewer", password="x", is_staff=True)
    user.user_permissions.add(
        Permission.objects.get(
            content_type__app_label="zgw_consumers", codename="view_service"
        )
    )
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def change_url_for_a_service(service: Service) -> str:
    return reverse("admin:zgw_consumers_service_change", args=(service.pk,))


def _credential_url(service: Service, field_name: str) -> str:
    return reverse(
        f"admin:zgw_consumers_service_change_{field_name}", args=(service.pk,)
    )


def _change_form_data(service: Service, **overrides) -> dict:
    data = {
        "label": service.label,
        "slug": service.slug,
        "uuid": str(service.uuid),
        "api_type": service.api_type,
        "api_root": service.api_root,
        "api_connection_check_path": service.api_connection_check_path,
        "auth_type": service.auth_type,
        "client_id": service.client_id,
        "oauth2_token_url": service.oauth2_token_url,
        "oauth2_scope": service.oauth2_scope,
        "oauth2_token_endpoint_auth_method": service.oauth2_token_endpoint_auth_method,
        "jwt_valid_for": service.jwt_valid_for,
        "header_key": service.header_key,
        "nlx": service.nlx,
        "user_id": service.user_id,
        "user_representation": service.user_representation,
        "timeout": service.timeout,
    }
    data.update(overrides)
    return data


class TestChangePage:
    def test_credentials_are_masked(
        self, admin_client: Client, change_url_for_a_service
    ):
        response = admin_client.get(change_url_for_a_service)

        assert response.status_code == 200
        assertNotContains(response, SECRET)
        assertNotContains(response, API_KEY)
        assertContains(response, mask(SECRET))
        assertContains(response, mask(API_KEY))
        assertContains(response, 'href="../secret/"')
        assertContains(response, 'href="../header-key-value/"')

    def test_header_key_is_rendered_as_text(
        self, admin_client: Client, change_url_for_a_service
    ):
        response = admin_client.get(change_url_for_a_service)

        assertContains(response, "<code>Authorization</code>", html=True)
        assertNotContains(response, 'name="header_key"')
        # both header fields link to the same flow, which changes them together
        assertContains(response, 'href="../header-key-value/"', count=2)

    def test_header_key_is_read_only(
        self, admin_client: Client, service, change_url_for_a_service
    ):
        # changed together with the header value, in its own flow
        data = _change_form_data(service, header_key="")

        response = admin_client.post(change_url_for_a_service, data)

        assert response.status_code == 302, response.context["adminform"].form.errors
        service.refresh_from_db()
        assert service.header_key == "Authorization"
        assert service.header_value == API_KEY

    def test_credential_not_set_hint(self, admin_client: Client):
        service = ServiceFactory.create(
            api_root="https://example.com/", auth_type=AuthTypes.no_auth
        )

        response = admin_client.get(
            reverse("admin:zgw_consumers_service_change", args=(service.pk,))
        )

        assertContains(response, "Not set")

    def test_submitted_credentials_are_ignored(
        self, admin_client: Client, service, change_url_for_a_service
    ):
        data = _change_form_data(
            service, label="Renamed", secret="injected", header_value="injected"
        )

        response = admin_client.post(change_url_for_a_service, data)

        assert response.status_code == 302, response.context["adminform"].form.errors
        service.refresh_from_db()
        assert service.label == "Renamed"
        assert service.secret == SECRET
        assert service.header_value == API_KEY

    def test_submitted_credentials_are_not_rendered_on_validation_error(
        self, admin_client: Client, service, change_url_for_a_service
    ):
        data = _change_form_data(
            service,
            label="",  # required -> validation error
            secret="injected-secret",
            header_value="injected-api-key",
        )

        response = admin_client.post(change_url_for_a_service, data)

        assert response.status_code == 200
        assert "label" in response.context["adminform"].form.errors
        assertNotContains(response, "injected-secret")
        assertNotContains(response, "injected-api-key")
        assertNotContains(response, SECRET)
        assertNotContains(response, API_KEY)
        assertContains(response, mask(SECRET))
        assertContains(response, mask(API_KEY))

    def test_model_validation_sees_stored_credentials(
        self, admin_client: Client, service, change_url_for_a_service
    ):
        # ZGW auth requires a secret - the (disabled) field must still carry the
        # stored value into model validation
        data = _change_form_data(service, label="Renamed")

        response = admin_client.post(change_url_for_a_service, data)

        assert response.status_code == 302, response.context["adminform"].form.errors


class TestReadOnlyChangePage:
    def test_credentials_are_masked(
        self, read_only_client: Client, change_url_for_a_service
    ):
        response = read_only_client.get(change_url_for_a_service)

        assert response.status_code == 200
        assertNotContains(response, SECRET)
        assertNotContains(response, API_KEY)
        assertContains(response, mask(SECRET))
        assertContains(response, mask(API_KEY))

    @pytest.mark.parametrize("field_name", ["secret", "header_value"])
    def test_cannot_access_credential_form(
        self, read_only_client: Client, service, field_name
    ):
        response = read_only_client.get(_credential_url(service, field_name))

        assert response.status_code == 403


class TestCredentialChangeForm:
    @pytest.mark.parametrize("field_name", ["secret", "header_value"])
    def test_does_not_render_stored_value(
        self, admin_client: Client, service, field_name
    ):
        response = admin_client.get(_credential_url(service, field_name))

        assert response.status_code == 200
        assertNotContains(response, SECRET)
        assertNotContains(response, API_KEY)
        assertContains(response, mask(getattr(service, field_name)))
        assertContains(response, f'type="password" name="{field_name}"')
        assertContains(response, f'placeholder="{mask(getattr(service, field_name))}"')

    def test_change_secret(
        self, admin_client: Client, service, change_url_for_a_service
    ):
        response = admin_client.post(
            _credential_url(service, "secret"), {"secret": "brand-new-secret"}
        )

        assert response.status_code == 302
        assert response["Location"] == change_url_for_a_service
        service.refresh_from_db()
        assert service.secret == "brand-new-secret"
        assert service.header_key == "Authorization"
        assert service.header_value == API_KEY

    @pytest.mark.parametrize(
        "field_name,data,old_value",
        [
            ("secret", {"secret": "new-one"}, SECRET),
            (
                "header_value",
                {"header_key": "Authorization", "header_value": "new-one"},
                API_KEY,
            ),
        ],
    )
    def test_change_is_logged_without_value(
        self, admin_client: Client, service, field_name, data, old_value
    ):
        response = admin_client.post(_credential_url(service, field_name), data)

        assert response.status_code == 302
        log_entry = LogEntry.objects.get()
        assert log_entry.object_id == str(service.pk)
        assert "new-one" not in log_entry.change_message
        assert old_value not in log_entry.change_message

    def test_invalid_value_keeps_stored_value(self, admin_client: Client, service):
        # ZGW auth requires a secret
        response = admin_client.post(_credential_url(service, "secret"), {"secret": ""})

        assert response.status_code == 200
        assert response.context["form"].errors == {
            "secret": ["The field 'secret' is required for ZGW authentication"]
        }
        assertNotContains(response, SECRET)
        service.refresh_from_db()
        assert service.secret == SECRET

    def test_invalid_value_does_not_render_submitted_value(
        self, admin_client: Client, service
    ):
        too_long = "x" * 256

        response = admin_client.post(
            _credential_url(service, "secret"), {"secret": too_long}
        )

        assert response.status_code == 200
        assert list(response.context["form"].errors) == ["secret"]
        assertNotContains(response, too_long)
        assertNotContains(response, SECRET)
        service.refresh_from_db()
        assert service.secret == SECRET

    def test_error_on_field_outside_form(self, admin_client: Client):
        # Inconsistent stored data: OAuth2 without client ID / token URL. The model
        # validation errors are raised on fields that are not part of this form.
        service = ServiceFactory.create(
            api_root="https://example.com/",
            auth_type=AuthTypes.oauth2_client_credentials,
            client_id="",
            secret="old-secret",
            oauth2_token_url="",
        )

        response = admin_client.post(
            _credential_url(service, "secret"), {"secret": "new-secret"}
        )

        assert response.status_code == 200
        assert list(response.context["form"].errors) == ["__all__"]
        assertNotContains(response, "new-secret")
        service.refresh_from_db()
        assert service.secret == "old-secret"

    def test_unknown_service(self, admin_client: Client, db):
        response = admin_client.get(
            reverse("admin:zgw_consumers_service_change_secret", args=(9999,))
        )

        assert response.status_code == 404


class TestHeaderValueChangeForm:
    """
    The header key and value must both be set or both be empty, so they are edited
    together.
    """

    def _post(self, client: Client, service: Service, key: str, value: str):
        return client.post(
            _credential_url(service, "header_value"),
            {"header_key": key, "header_value": value},
        )

    def test_renders_header_key_but_not_value(self, admin_client: Client, service):
        response = admin_client.get(_credential_url(service, "header_value"))

        assertContains(response, 'name="header_key" value="Authorization"')
        assertContains(response, 'type="password" name="header_value"')
        assertContains(response, f'placeholder="{mask(API_KEY)}"')
        assertNotContains(response, API_KEY)

    def test_no_placeholder_without_value(self, admin_client: Client):
        service = ServiceFactory.create(
            api_root="https://example.com/", auth_type=AuthTypes.no_auth
        )

        response = admin_client.get(_credential_url(service, "header_value"))

        # (not a text check: the admin's sidebar filter has a placeholder too)
        widget = response.context["form"].fields["header_value"].widget
        assert "placeholder" not in widget.attrs

    def test_change_value(self, admin_client: Client, service):
        response = self._post(admin_client, service, "Authorization", "new-key")

        assert response.status_code == 302
        service.refresh_from_db()
        assert service.header_key == "Authorization"
        assert service.header_value == "new-key"
        assert service.secret == SECRET
        assert LogEntry.objects.get().get_change_message() == "Changed Header value."

    def test_change_key_and_value(self, admin_client: Client, service):
        response = self._post(admin_client, service, "X-Api-Key", "new-key")

        assert response.status_code == 302
        service.refresh_from_db()
        assert service.header_key == "X-Api-Key"
        assert service.header_value == "new-key"
        assert (
            LogEntry.objects.get().get_change_message()
            == "Changed Header key and Header value."
        )

    def test_change_key_requires_value(self, admin_client: Client, service):
        # the stored value is never shown, so it must be entered again
        response = self._post(admin_client, service, "X-Api-Key", "")

        assert response.status_code == 200
        assert list(response.context["form"].errors) == ["header_value"]
        service.refresh_from_db()
        assert service.header_key == "Authorization"
        assert service.header_value == API_KEY

    def test_clear_both(self, admin_client: Client, service):
        response = self._post(admin_client, service, "", "")

        assert response.status_code == 302
        service.refresh_from_db()
        assert service.header_key == ""
        assert service.header_value == ""

    def test_value_without_key(self, admin_client: Client, service):
        response = self._post(admin_client, service, "", "some-key")

        assert response.status_code == 200
        assert list(response.context["form"].errors) == ["header_key"]
        assertNotContains(response, "some-key")
        service.refresh_from_db()
        assert service.header_value == API_KEY


class TestAddPage:
    def test_credentials_are_password_inputs(self, admin_client: Client):
        response = admin_client.get(reverse("admin:zgw_consumers_service_add"))

        assertContains(response, 'type="password" name="secret"')
        assertContains(response, 'type="password" name="header_value"')

    def test_submitted_credentials_are_kept_on_validation_error(
        self, admin_client: Client
    ):
        response = admin_client.post(
            reverse("admin:zgw_consumers_service_add"),
            {
                "label": "",  # required -> validation error
                "auth_type": AuthTypes.zgw,
                "secret": "typed-secret",
                "header_key": "Authorization",
                "header_value": "typed-api-key",
            },
        )

        assert response.status_code == 200
        assert not Service.objects.exists()
        assertContains(response, 'value="typed-secret"')
        assertContains(response, 'value="typed-api-key"')
