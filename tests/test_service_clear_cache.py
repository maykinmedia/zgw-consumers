from pathlib import Path

from django.core.files.base import File
from unittest.mock import patch

import pytest

from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

API_ROOT = "https://example.com/api/v1/"
OAS_PATH = Path(__file__).parent / "schemas" / "ztc.yaml"


@pytest.mark.django_db
def test_save_service_with_type_ztc(settings):
    with patch(
        "zgw_consumers.admin_fields.get_zaaktypen.cache_clear"
    ) as mock_clear_cache:
        # set up service
        with open(OAS_PATH, "r") as oas_file:
            service = Service.objects.create(
                label="Test",
                api_type=APITypes.ztc,
                api_root=API_ROOT,
                oas_file=File(oas_file, name="schema.yaml"),
            )
            service.full_clean()

        mock_clear_cache.assert_called_once()


@pytest.mark.django_db
def test_save_service_with_type_ac(settings):
    with patch(
        "zgw_consumers.admin_fields.get_zaaktypen.cache_clear"
    ) as mock_clear_cache:
        # set up service
        with open(OAS_PATH, "r") as oas_file:
            service = Service.objects.create(
                label="Test",
                api_type=APITypes.ac,
                api_root=API_ROOT,
                oas_file=File(oas_file, name="schema.yaml"),
            )
            service.full_clean()

        mock_clear_cache.assert_not_called()


@pytest.mark.django_db
def test_save_service_with_type_nrc(settings):
    with patch(
        "zgw_consumers.admin_fields.get_zaaktypen.cache_clear"
    ) as mock_clear_cache:
        # set up service
        with open(OAS_PATH, "r") as oas_file:
            service = Service.objects.create(
                label="Test",
                api_type=APITypes.nrc,
                api_root=API_ROOT,
                oas_file=File(oas_file, name="schema.yaml"),
            )
            service.full_clean()

        mock_clear_cache.assert_not_called()


@pytest.mark.django_db
def test_save_service_with_type_zrc(settings):
    with patch(
        "zgw_consumers.admin_fields.get_zaaktypen.cache_clear"
    ) as mock_clear_cache:
        # set up service
        with open(OAS_PATH, "r") as oas_file:
            service = Service.objects.create(
                label="Test",
                api_type=APITypes.zrc,
                api_root=API_ROOT,
                oas_file=File(oas_file, name="schema.yaml"),
            )
            service.full_clean()

        mock_clear_cache.assert_not_called()


@pytest.mark.django_db
def test_save_service_with_type_drc(settings):
    with patch(
        "zgw_consumers.admin_fields.get_zaaktypen.cache_clear"
    ) as mock_clear_cache:
        # set up service
        with open(OAS_PATH, "r") as oas_file:
            service = Service.objects.create(
                label="Test",
                api_type=APITypes.drc,
                api_root=API_ROOT,
                oas_file=File(oas_file, name="schema.yaml"),
            )
            service.full_clean()

        mock_clear_cache.assert_not_called()


@pytest.mark.django_db
def test_save_service_with_type_brc(settings):
    with patch(
        "zgw_consumers.admin_fields.get_zaaktypen.cache_clear"
    ) as mock_clear_cache:
        # set up service
        with open(OAS_PATH, "r") as oas_file:
            service = Service.objects.create(
                label="Test",
                api_type=APITypes.brc,
                api_root=API_ROOT,
                oas_file=File(oas_file, name="schema.yaml"),
            )
            service.full_clean()

        mock_clear_cache.assert_not_called()


@pytest.mark.django_db
def test_save_service_with_type_cmc(settings):
    with patch(
        "zgw_consumers.admin_fields.get_zaaktypen.cache_clear"
    ) as mock_clear_cache:
        # set up service
        with open(OAS_PATH, "r") as oas_file:
            service = Service.objects.create(
                label="Test",
                api_type=APITypes.cmc,
                api_root=API_ROOT,
                oas_file=File(oas_file, name="schema.yaml"),
            )
            service.full_clean()

        mock_clear_cache.assert_not_called()


@pytest.mark.django_db
def test_save_service_with_type_kc(settings):
    with patch(
        "zgw_consumers.admin_fields.get_zaaktypen.cache_clear"
    ) as mock_clear_cache:
        # set up service
        with open(OAS_PATH, "r") as oas_file:
            service = Service.objects.create(
                label="Test",
                api_type=APITypes.kc,
                api_root=API_ROOT,
                oas_file=File(oas_file, name="schema.yaml"),
            )
            service.full_clean()

        mock_clear_cache.assert_not_called()


@pytest.mark.django_db
def test_save_service_with_type_vrc(settings):
    with patch(
        "zgw_consumers.admin_fields.get_zaaktypen.cache_clear"
    ) as mock_clear_cache:
        # set up service
        with open(OAS_PATH, "r") as oas_file:
            service = Service.objects.create(
                label="Test",
                api_type=APITypes.vrc,
                api_root=API_ROOT,
                oas_file=File(oas_file, name="schema.yaml"),
            )
            service.full_clean()

        mock_clear_cache.assert_not_called()


@pytest.mark.django_db
def test_save_service_with_type_orc(settings):
    with patch(
        "zgw_consumers.admin_fields.get_zaaktypen.cache_clear"
    ) as mock_clear_cache:
        # set up service
        with open(OAS_PATH, "r") as oas_file:
            service = Service.objects.create(
                label="Test",
                api_type=APITypes.orc,
                api_root=API_ROOT,
                oas_file=File(oas_file, name="schema.yaml"),
            )
            service.full_clean()

        mock_clear_cache.assert_not_called()
