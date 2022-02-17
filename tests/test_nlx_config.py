from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

import pytest

from zgw_consumers.models import NLXConfig


@pytest.mark.django_db
def test_clean_created_from_defaults():
    config = NLXConfig.get_solo()

    assert config.clean() is None


def test_validate_outway_conn_test():
    config = NLXConfig(outway="http://invalid-host:1337")

    err = _("Connection refused. Please provide a correct address.")
    with pytest.raises(ValidationError, match=err):
        config.clean()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "outway,fixed_outway",
    [
        ("", ""),
        ("http://localhost:8080", "http://localhost:8080/"),
        ("http://localhost:8080/", "http://localhost:8080/"),
    ],
)
def test_append_trailing_slash(outway, fixed_outway):
    config = NLXConfig.get_solo()
    config.outway = outway
    config.save()

    assert config.outway == fixed_outway
