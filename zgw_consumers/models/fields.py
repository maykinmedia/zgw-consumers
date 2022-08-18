from typing import Optional
from urllib.parse import urljoin

from django.core import checks
from django.core.exceptions import FieldDoesNotExist
from django.db.models import CharField, Field, ForeignKey, Model


class ServiceUrlDescriptor:
    def __init__(self, field):
        self.field = field

    def get_base_url(self, base_val) -> str:
        return getattr(base_val, "api_root", None)

    def get_base_val(self, detail_url: str):
        from zgw_consumers.models import Service

        return Service.get_service(detail_url)

    def __get__(self, instance: Model, cls=None) -> Optional[str]:
        if instance is None:
            return None

        base_val = getattr(instance, self.field.base_field)
        base_url = self.get_base_url(base_val)
        relative_val = getattr(instance, self.field.relative_field)

        # todo cache value
        return urljoin(base_url, relative_val)

    def __set__(self, instance: Model, value: Optional[str]):
        if value is None and not self.field.null:
            raise ValueError(
                "A 'None'-value is not allowed. Make the field "
                "nullable if empty values should be supported."
            )

        base_val = None
        relative_val = None
        if value:
            if not isinstance(value, str):
                raise TypeError("Only string values are supported")

            base_val = self.get_base_val(value)
            if not base_val:
                raise ValueError(
                    "The base part of url %s is not found in 'Service' data" % value
                )

            relative_val = value[len(self.get_base_url(base_val)) :]

        setattr(instance, self.field.base_field, base_val)
        setattr(instance, self.field.relative_field, relative_val)
        # todo cache value


class ServiceUrlField(Field):
    """
    Composite field to store the base and relative parts of the url separately.

    This class is supposed to use with `zgw_consumers.Service` model
    """

    # field flags
    name = None
    concrete = False
    column = None
    db_column = None

    descriptor_class = ServiceUrlDescriptor

    def __init__(self, base_field: str, relative_field: str, **kwargs):
        """
        :param str base_field: name of ForeignKey field to the Service model
        used for the base part of the url

        :param str relative_field: name of CharField which consists of
        the relative part of the url
        """
        self.base_field = base_field
        self.relative_field = relative_field

        super().__init__(**kwargs)

    def contribute_to_class(self, cls, name, private_only=False):
        self.name = name
        self.model = cls
        cls._meta.add_field(self, private=private_only)

        setattr(cls, name, self.descriptor_class(self))

    @property
    def attname(self) -> str:
        return self.name

    def get_attname_column(self):
        return self.attname, None

    def deconstruct(self):
        path = "%s.%s" % (self.__class__.__module__, self.__class__.__qualname__)
        keywords = {
            "base_field": self.base_field,
            "relative_field": self.relative_field,
            "blank": self.blank,
            "null": self.null,
        }
        return self.name, path, [], keywords

    @property
    def _base_field(self) -> ForeignKey:
        return self.model._meta.get_field(self.base_field)

    @property
    def _relative_field(self) -> CharField:
        return self.model._meta.get_field(self.relative_field)

    def check(self, **kwargs):
        return [
            *self._check_field_name(),
            *self._check_base_field(),
            *self._check_relative_field(),
        ]

    def _check_field_name(self):
        if self.name.endswith("_"):
            return [
                checks.Error(
                    "Field names must not end with an underscore.",
                    obj=self,
                    id="fields.E001",
                )
            ]
        else:
            return []

    def _check_base_field(self):
        """
        Check if 'base_field' exists and if it is a FK to Service model
        """
        try:
            field = self.model._meta.get_field(self.base_field)
        except FieldDoesNotExist:
            return [
                checks.Error(
                    "The ServiceUrlField base_field references the nonexistent field '%s'."
                    % self.base_field,
                    obj=self,
                    id="zgw_consumers.E001",
                )
            ]
        else:
            from zgw_consumers.models import Service

            if not isinstance(field, ForeignKey):
                return [
                    checks.Error(
                        "'%s.%s' is not a ForeignKey."
                        % (self.model._meta.object_name, self.base_field),
                        obj=self,
                        id="zgw_consumers.E002",
                    )
                ]
            elif field.remote_field.model != Service:
                return [
                    checks.Error(
                        "'%s.%s' is not a ForeignKey to 'zgw_consumers.Service'."
                        % (self.model._meta.object_name, self.base_field),
                        obj=self,
                        id="zgw_consumers.E003",
                    )
                ]
            else:
                return []

    def _check_relative_field(self):
        """
        Check if 'relative_field' exists
        """
        try:
            self.model._meta.get_field(self.relative_field)
        except FieldDoesNotExist:
            return [
                checks.Error(
                    "The ServiceUrlField relative_field references the nonexistent field '%s'."
                    % self.relative_field,
                    obj=self,
                    id="zgw_consumers.E004",
                )
            ]
        else:
            return []
