from django.core.exceptions import ValidationError

import pytest

from zgw_consumers.models.validators import NonUrlValidator, validate_leading_slashes


def test_is_not_url_validator():
    validator = NonUrlValidator()

    try:
        validator("some random text")
    except ValidationError:
        pytest.fail("Expected validation to pass")

    with pytest.raises(
        ValidationError,
        match="Value cannot be a URL.",
    ):
        validator("http://www.example.com")


def test_validate_leading_slashes():
    try:
        validate_leading_slashes("foo")
    except ValidationError:
        pytest.fail("Expected validation to pass")

    with pytest.raises(
        ValidationError,
        match="The value must be a relative path.",
    ):
        validate_leading_slashes("/foo")
