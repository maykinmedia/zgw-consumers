from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from zgw_consumers.api_models.base import Model, factory


def test_absent_keys_for_optional_fields() -> None:
    @dataclass
    class TestModel(Model):
        required_field: str
        optional_field: Optional[datetime] = None

    data = {"requiredField": "a value"}

    instance = factory(TestModel, data)

    assert instance.required_field == "a value"
    assert instance.optional_field is None
