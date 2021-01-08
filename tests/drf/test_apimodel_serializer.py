from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID

import pytest
from rest_framework import fields

from zgw_consumers.drf.serializers import APIModelSerializer


@dataclass
class SimpleModel:
    some_str: str
    some_date: date
    some_datetime: datetime
    some_time: time
    some_int: int
    some_float: float
    some_decimal: Decimal
    some_bool: bool
    some_uuid: UUID

@pytest.mark.parametrize(
    "field,expected_type",
    [
        ("some_str", fields.CharField),
        ("some_date", fields.DateField),
        ("some_datetime", fields.DateTimeField),
        ("some_time", fields.TimeField),
        ("some_int", fields.IntegerField),
        ("some_float", fields.FloatField),
        # ("some_decimal", fields.DecimalField),
        ("some_bool", fields.BooleanField),
        ("some_uuid", fields.UUIDField),
    ],
)
def test_simple_model_serializer_fields(field: str, expected_type):
    class Serializer(APIModelSerializer):
        class Meta:
            model = SimpleModel
            fields = (field,)

    serializer = Serializer()

    assert field in serializer.fields
    assert isinstance(serializer.fields[field], expected_type)
