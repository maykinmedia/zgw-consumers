from django.test import Client
from django.urls import reverse


def test_oas_fields_enabled(admin_client: Client, settings):
    settings.ZGW_CONSUMERS_IGNORE_OAS_FIELDS = False
    url = reverse("admin:zgw_consumers_service_add")

    response = admin_client.get(url)

    form = response.context["adminform"]

    # django 3.2
    if hasattr(form, "form"):
        form = form.form

    assert "oas" in form.fields
    assert "oas_file" in form.fields


def test_oas_fields_disabled(admin_client: Client, settings):
    settings.ZGW_CONSUMERS_IGNORE_OAS_FIELDS = True
    url = reverse("admin:zgw_consumers_service_add")

    response = admin_client.get(url)

    form = response.context["adminform"]

    # django 3.2
    if hasattr(form, "form"):
        form = form.form

    assert "oas" not in form.fields
    assert "oas_file" not in form.fields
