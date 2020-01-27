"""
Datamodels for ZGW resources.

These are NOT django models.
"""
import uuid

from dateutil.relativedelta import relativedelta
from relativedeltafield import parse_relativedelta

from ._camel_case import underscoreize

TYPE_MAPPERS = {
    relativedelta: parse_relativedelta,
}


class BaseModel:
    @classmethod
    def from_raw(cls, raw_data: dict, strict=False):
        kwargs = underscoreize(raw_data)

        annotations = cls.__annotations__
        init_kwargs = {}

        for field, value in kwargs.items():
            if strict and field not in annotations:
                raise TypeError(f"Field {field} does not exists on {cls}")
            elif not strict and field not in annotations:
                continue

            output_type = annotations[field]

            # not type conversion required if it's already the right type
            if type(value) == output_type:
                init_kwargs[field] = value

            # check for type casts
            else:
                type_cast = TYPE_MAPPERS.get(output_type)
                if value and type_cast is not None:
                    value = type_cast(value)
                init_kwargs[field] = value

        return cls(**init_kwargs)


class Model(BaseModel):
    @property
    def uuid(self) -> uuid.UUID:
        """
        Because of the usage of UUID4, we can rely on the UUID as identifier.
        """
        _uuid = self.url.split("/")[-1]
        return uuid.UUID(_uuid)
