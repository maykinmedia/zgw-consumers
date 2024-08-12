"""
Test using a local OAS
"""

# import os
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.files.base import File
from django.utils.text import slugify

import pytest

from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

pytestmark = pytest.mark.django_db()

OAS_PATH = Path(__file__).parent / "schemas/drc.yaml"


def test_use_local_oas_file(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    with open(OAS_PATH, "r") as oas_file:
        service = Service.objects.create(
            label="Test",
            api_type=APITypes.drc,
            api_root="http://foo.bar",
            oas_file=File(oas_file, name="schema.yaml"),
            slug=slugify("http://foo.bar"),
        )
        service.full_clean()

    client = service.build_client()

    # check we grabbed the relevant fields
    assert client.schema_url == ""
    assert client.schema_file != None

    # check we fetched the schema
    assert client.schema != None
    assert client.schema["openapi"] == "3.0.0"


def test_require_exclusively_oas_url_or_file(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    with open(OAS_PATH, "r") as oas_file:
        service = Service(
            label="Test",
            api_type=APITypes.drc,
            api_root="http://foo.bar",
            # oas and oas_file both defined
            oas="http://foo.bar/schema.yaml",
            oas_file=File(oas_file, name="schema.yaml"),
        )
        service.save()

    with pytest.raises(ValidationError) as excinfo:
        service.full_clean()

    # check both fields have a message
    error = excinfo.value.error_dict
    assert error["oas"][0].messages == ["Set either oas or oas_file, not both"]
    assert error["oas_file"][0].messages == ["Set either oas or oas_file, not both"]


def test_require_either_oas_url_or_file():
    with open(OAS_PATH, "r"):
        service = Service(
            label="Test",
            api_type=APITypes.drc,
            api_root="http://foo.bar",
            # oas and oas_file both empty
            oas="",
            oas_file=None,
        )
        service.save()

    with pytest.raises(ValidationError) as excinfo:
        service.full_clean()

    # check both fields have a message
    error = excinfo.value.error_dict
    assert error["oas"][0].messages == ["Set either oas or oas_file"]
    assert error["oas_file"][0].messages == ["Set either oas or oas_file"]
