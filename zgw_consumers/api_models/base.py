"""
Datamodels for ZGW resources.

These are NOT django models.
"""
import uuid
from datetime import datetime
from typing import List, Union

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from relativedeltafield import parse_relativedelta

from ._camel_case import underscoreize
from .types import JSONObject

__all__ = ["CONVERTERS", "factory", "Model", "ZGWModel"]

CONVERTERS = {
    type(None): lambda x: None,
    datetime: parse,
    relativedelta: parse_relativedelta,
    uuid.UUID: lambda value: uuid.UUID(value),
    int: lambda number: number,
    float: lambda number: number,
}


class Model:
    def __post_init__(self):
        self._type_cast()

    def _type_cast(self):
        for attr, typehint in self.__annotations__.items():
            value = getattr(self, attr)

            if typehint is None:
                typehint = type(None)

            # support for Optional
            if hasattr(typehint, "__origin__") and typehint.__origin__ is Union:
                typehint = typehint.__args__

                if value is None:
                    continue

                # Optional is ONE type combined with None
                typehint = next(t for t in typehint.__args__ if t is not None)

            if isinstance(value, typehint):
                continue

            converter = CONVERTERS[typehint]
            setattr(self, attr, converter(value))


class ZGWModel(Model):
    @property
    def uuid(self) -> uuid.UUID:
        """
        Because of the usage of UUID4, we can rely on the UUID as identifier.
        """
        _uuid = self.url.split("/")[-1]
        return uuid.UUID(_uuid)


def factory(
    model: type, data: Union[JSONObject, List[JSONObject]]
) -> Union[type, List[type]]:
    _is_collection = isinstance(data, list)

    known_kwargs = list(model.__annotations__.keys())

    def _normalize(kwargs: dict):
        # TODO: this should be an explicit mapping, but *most* of the time with ZGW
        # API's this is fine.
        kwargs = underscoreize(kwargs)
        to_keep = {key: value for key, value in kwargs.items() if key in known_kwargs}
        return to_keep

    if not _is_collection:
        data = [data]

    instances = [model(**_normalize(_raw)) for _raw in data]

    if not _is_collection:
        instances = instances[0]
    return instances
