from typing import Optional
from urllib.parse import urljoin

from django.core import checks
from django.core.exceptions import FieldDoesNotExist
from django.db.models import CharField, ForeignKey, Model, query_utils
from django.utils.functional import cached_property


class ServiceUrlField(query_utils.RegisterLookupMixin):
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
    remote_field = None
    concrete = False

    def __init__(
        self,
        base_field: str,
        relative_field: str,
        blank: bool = False,
        null: bool = False,
    ):
        """
        :param str base_field: name of ForeignKey field to the Service model
        used for the base part of the url

        :param str relative_field: name of CharField which consists of
        the relative part of the url
        """
        self.base_field = base_field
        self.relative_field = relative_field
        self.blank = blank
        self.null = null

    def contribute_to_class(self, cls, name, private_only=False):
        self.name = name
        self.model = cls
        cls._meta.add_field(self, private=True)

        # todo can be changed to separate descriptor
        setattr(cls, name, self)

    def __str__(self):
        model = self.model
        return "%s.%s" % (model._meta.label, self.name)

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

    @property
    def attname(self) -> str:
        return self.name

    def get_base_url(self, base_val) -> str:
        return getattr(base_val, "api_root", None)

    def get_base_val(self, detail_url: str):
        from zgw_consumers.models import Service

        return Service.get_service(detail_url)

    def __get__(self, instance: Model, cls=None) -> Optional[str]:
        if instance is None:
            return None

        base_val = getattr(instance, self.base_field)
        base_url = self.get_base_url(base_val)
        relative_val = getattr(instance, self.relative_field)

        # todo cache value
        return urljoin(base_url, relative_val)

    def __set__(self, instance: Model, value: Optional[str]):
        if value is None and not self.null:
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
                raise ValueError("The base part of url is not found in 'Service' data")

            relative_val = value[len(self.get_base_url(base_val)) :]

        setattr(instance, self.base_field, base_val)
        setattr(instance, self.relative_field, relative_val)

        # todo cache value

    def get_col(self, alias, output_field=None):
        if output_field is None:
            output_field = self
        if alias != self.model._meta.db_table or output_field != self:
            from django.db.models.expressions import Col

            return Col(alias, self, output_field)
        else:
            return self.cached_col

    @cached_property
    def cached_col(self):
        from django.db.models.expressions import Col

        return Col(self.model._meta.db_table, self)

    def get_internal_type(self):
        return self.__class__.__name__

    def db_type(self, connection):
        return None
