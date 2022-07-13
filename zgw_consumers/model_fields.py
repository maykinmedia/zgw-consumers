from urllib.parse import urljoin

from django.core import checks
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Field, ForeignKey, Model

from zgw_consumers.models import Service


class ServiceUrlField:
    """
    Composite field to store the base and relative parts of the url separately.

    This class is supposed to use with `zgw_consumers.Service` model
    """

    # field flags
    name = None
    is_relation = False
    many_to_many = False
    primary_key = False
    db_column = None

    def __init__(self, base_field: str, relative_field: str):
        """
        :param str base_field: name of ForeignKey field to the Service model
        used for the base part of the url

        :param str relative_field: name of CharField which consists of
        the relative part of the url
        """
        self.base_field = base_field
        self.relative_field = relative_field

        self.creation_counter = Field.creation_counter
        Field.creation_counter += 1

    def __lt__(self, other):
        # This is needed because bisect does not take a comparison function.
        if isinstance(other, Field):
            return self.creation_counter < other.creation_counter
        return NotImplemented

    def contribute_to_class(self, cls, name, private_only=False):
        self.name = name
        self.model = cls
        cls._meta.add_field(self, private=private_only)

        # todo can be changed to separate descriptor
        setattr(cls, name, self)

    def __str__(self):
        model = self.model
        return "%s.%s" % (model._meta.label, self.name)

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

    @property
    def attname(self) -> str:
        return self.name

    def get_attname_column(self):
        return self.attname, None

    def clone(self):
        """
        Uses deconstruct() to clone a new copy of this Field.
        Will not preserve any class attachments/attribute names.
        """
        name, path, args, kwargs = self.deconstruct()
        return self.__class__(*args, **kwargs)

    def deconstruct(self):
        path = "%s.%s" % (self.__class__.__module__, self.__class__.__qualname__)
        keywords = {
            "base_field": self.base_field,
            "relative_field": self.relative_field,
        }
        return self.name, path, [], keywords

    def get_base_url(self, base_val) -> str:
        return base_val.api_root

    def get_base_val(self, detail_url: str):
        return Service.get_service(detail_url)

    def __get__(self, instance: Model, cls=None):
        if instance is None:
            return self

        base_val = self.model._meta.get_field(self.base_field)
        base_url = self.get_base_url(base_val)
        relative_val = self.model._meta.get_field(self.relative_field)

        # todo cache value
        return urljoin(base_url, relative_val)

    def __set__(self, instance: Model, value: str):
        base_val = None
        relative_val = None

        #  todo value error if null and it's not allowed
        if value:
            if not isinstance(value, str):
                raise TypeError("Only string values are supported")

            # todo validate url

            base_val = self.get_base_val(value)
            relative_val = value[len(self.get_base_url(base_val)) :]

            # todo validate relative val against OAS?

        setattr(instance, self.base_field, base_val)
        setattr(instance, self.relative_field, relative_val)

        # todo cache value
