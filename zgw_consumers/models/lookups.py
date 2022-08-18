from typing import Optional, Tuple

from django.db.models.fields.related_lookups import get_normalized_value
from django.db.models.lookups import Exact as _Exact, In as _In

from zgw_consumers.models import Service

from .fields import ServiceUrlField


def decompose_value(value: str) -> Tuple[Optional[Service], Optional[str]]:
    service = Service.get_service(value)
    if not service:
        return None, None

    relative_val = value[len(service.api_root) :]
    return service, relative_val


class ServiceUrlFieldMixin:
    def split_lhs(self, compiler, connection) -> Tuple[str, tuple, str, tuple]:
        target = self.lhs.target
        alias = target.model._meta.db_table

        base_lhs = target._base_field.get_col(alias)
        relative_lhs = target._relative_field.get_col(alias)

        base_lhs_sql, base_lhs_params = self.process_lhs(
            compiler, connection, lhs=base_lhs
        )
        relative_lhs_sql, relative_lhs_params = self.process_lhs(
            compiler, connection, lhs=relative_lhs
        )

        return base_lhs_sql, base_lhs_params, relative_lhs_sql, relative_lhs_params

    def get_prep_lookup(self) -> list:
        if not self.rhs_is_direct_value():
            return super().get_prep_lookup()

        target = self.lhs.target
        alias = target.model._meta.db_table
        base_lhs, relative_lhs = [
            field.get_col(alias, output_field=field)
            for field in [target._base_field, target._relative_field]
        ]
        value = self.rhs if self.get_db_prep_lookup_value_is_iterable else [self.rhs]

        prepared_values = []
        for rhs in value:
            base_value, relative_value = decompose_value(rhs)

            # convert model instances to int for FK fields
            base_normalized_value = get_normalized_value(base_value, base_lhs)[0]
            relative_normalized_value = get_normalized_value(
                relative_value, relative_lhs
            )[0]
            prepared_values.append(
                [
                    target._base_field.get_prep_value(base_normalized_value),
                    target._relative_field.get_prep_value(relative_normalized_value),
                ]
            )

        return (
            prepared_values[0]
            if not self.get_db_prep_lookup_value_is_iterable
            else prepared_values
        )

    def get_db_prep_lookup(self, value, connection):
        # For relational fields, use the 'target_field' attribute of the
        # output_field.
        target = self.lhs.target

        sql = "%s"

        params = (
            [
                [
                    target._base_field.get_db_prep_value(
                        v[0], connection, prepared=True
                    ),
                    target._relative_field.get_db_prep_value(
                        v[1], connection, prepared=True
                    ),
                ]
                for v in value
            ]
            if self.get_db_prep_lookup_value_is_iterable
            else [
                target._base_field.get_db_prep_value(
                    value[0], connection, prepared=True
                ),
                target._relative_field.get_db_prep_value(
                    value[1], connection, prepared=True
                ),
            ]
        )

        return sql, params


@ServiceUrlField.register_lookup
class Exact(ServiceUrlFieldMixin, _Exact):
    def as_sql(self, compiler, connection):
        # process lhs
        (
            base_lhs_sql,
            base_lhs_params,
            relative_lhs_sql,
            relative_lhs_params,
        ) = self.split_lhs(compiler, connection)

        # process rhs
        rhs_sql, rhs_params = self.process_rhs(compiler, connection)
        rhs_sql = self.get_rhs_op(connection, rhs_sql)

        # combine
        params = rhs_params
        sql = f"{base_lhs_sql} {rhs_sql} AND {relative_lhs_sql} {rhs_sql}"

        return sql, params


@ServiceUrlField.register_lookup
class In(ServiceUrlFieldMixin, _In):
    """
    This realization will add additional DB query for every item in rhs list
    Possible optimization is to cache Service.get_service(value)
    Other solution would be not to decompose rhs value, but to combine lhs fields
    But it will require additional join, which will complicate the implementation
    The concatenation can slow down the DB query even more since the indexes are
    usually not used with it
    """

    def as_sql(self, compiler, connection):
        # TODO: support connection.ops.max_in_list_size()
        # process lhs
        (
            base_lhs_sql,
            base_lhs_params,
            relative_lhs_sql,
            relative_lhs_params,
        ) = self.split_lhs(compiler, connection)

        # process rhs
        _, rhs_params = self.process_rhs(compiler, connection)
        rhs_sql = "IN (" + ", ".join(["(%s, %s)"] * len(rhs_params)) + ")"

        # combine
        params = sum(rhs_params, [])
        sql = f"({base_lhs_sql}, {relative_lhs_sql}) {rhs_sql}"

        return sql, params
