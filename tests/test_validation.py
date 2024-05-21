from django.core.exceptions import ValidationError

import pytest

from zgw_consumers.models.validators import IsNotUrlValidator, StartWithValidator


def test_start_with_validator_return_value_false():
    validator = StartWithValidator(prefix="/", return_value=False)

    assert validator.__call__("no_leading_slash") is None

    with pytest.raises(ValidationError) as exc_context:
        validator.__call__("/with_leading_slash")

    assert "The given value cannot start with '/'" in exc_context.value


def test_start_with_validator_return_value_true():
    validator = StartWithValidator(prefix="/")

    with pytest.raises(ValidationError) as exc_context:
        validator.__call__("no_leading_slash")

    assert "The given value must start with '/'" in exc_context.value

    assert validator.__call__("/with_leading_slash") is None


def test_is_not_url_validator():
    validator = IsNotUrlValidator()

    assert validator.__call__("some random text") is None

    with pytest.raises(ValidationError) as exc_context:
        assert validator.__call__("http://www.example.com")

    assert "String cannot be a URL" in exc_context.value
