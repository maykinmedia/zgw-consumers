from django.core.exceptions import ValidationError

import pytest

from zgw_consumers.models.validators import NonUrlValidator, PrefixValidator


def test_start_with_validator_starts_with_false():
    validator = PrefixValidator(prefix="/", starts_with=False)

    assert validator.__call__("no_leading_slash") is None

    with pytest.raises(ValidationError) as exc_context:
        validator.__call__("/with_leading_slash")

    assert "The given value cannot start with '/'" in exc_context.value


def test_start_with_validator_starts_with_true():
    validator = PrefixValidator(prefix="/")

    with pytest.raises(ValidationError) as exc_context:
        validator.__call__("no_leading_slash")

    assert "The given value must start with '/'" in exc_context.value

    assert validator.__call__("/with_leading_slash") is None


def test_is_not_url_validator():
    validator = NonUrlValidator()

    assert validator.__call__("some random text") is None

    with pytest.raises(ValidationError) as exc_context:
        assert validator.__call__("http://www.example.com")

    assert "Value cannot be a URL" in exc_context.value
