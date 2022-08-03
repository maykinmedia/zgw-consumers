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


@ServiceUrlField.register_lookup
class Exact(_Exact):
    def get_db_prep_lookup(self, value, connection):
        target = self.lhs.target
        base_field = target.model._meta.get_field(target.base_field)
        relative_field = target.model._meta.get_field(target.relative_field)

        sql = "%s"
        params = [
            base_field.get_db_prep_value(value[0], connection, prepared=True),
            relative_field.get_db_prep_value(value[1], connection, prepared=True),
        ]

        return sql, params

    def get_prep_lookup(self) -> list:
        if self.rhs_is_direct_value():
            target = self.lhs.target
            alias = target.model._meta.db_table
            decomposed_values = decompose_value(self.rhs)
            prepared_values = []
            for i, field_name in enumerate([target.base_field, target.relative_field]):
                field = target.model._meta.get_field(field_name)
                lhs = field.get_col(alias, output_field=field)
                # convert model instances to int for FK fields
                normalized_value = get_normalized_value(decomposed_values[i], lhs)[0]
                prep_value = field.get_prep_value(normalized_value)
                prepared_values.append(prep_value)

            return prepared_values

        return super().get_prep_lookup()

    def as_sql(self, compiler, connection):
        # process lhs for both fields
        target = self.lhs.target
        alias = target.model._meta.db_table
        base_lhs = target.model._meta.get_field(target.base_field).get_col(alias)
        relative_lhs = target.model._meta.get_field(target.relative_field).get_col(
            alias
        )
        base_lhs_sql, base_lhs_params = self.process_lhs(
            compiler, connection, lhs=base_lhs
        )
        relative_lhs_sql, relative_lhs_params = self.process_lhs(
            compiler, connection, lhs=relative_lhs
        )

        # process rhs
        rhs_sql, rhs_params = self.process_rhs(compiler, connection)
        rhs_sql = self.get_rhs_op(connection, rhs_sql)

        # combine
        params = rhs_params
        sql = f"{base_lhs_sql} {rhs_sql} AND {relative_lhs_sql} {rhs_sql}"

        return sql, params


@ServiceUrlField.register_lookup
class In(_In):
    # TODO This realization will add additional DB query for every item in rhs list
    # Possible optimization is to cache Service.get_service(value)
    # Other solution would be not to decompose rhs value, but to combine lhs fields
    # But it will require additional join, which will complicate the implementation
    # The concatenation can slow down the DB query even more since the indexes are
    # usually not used with it

    def get_db_prep_lookup(self, value, connection):
        # For relational fields, use the 'target_field' attribute of the
        # output_field.
        target = self.lhs.target
        base_field = target.model._meta.get_field(target.base_field)
        relative_field = target.model._meta.get_field(target.relative_field)

        sql = "%s"

        params = (
            [
                [
                    base_field.get_db_prep_value(v[0], connection, prepared=True),
                    relative_field.get_db_prep_value(v[1], connection, prepared=True),
                ]
                for v in value
            ]
            if self.get_db_prep_lookup_value_is_iterable
            else [
                base_field.get_db_prep_value(value[0], connection, prepared=True),
                relative_field.get_db_prep_value(value[1], connection, prepared=True),
            ]
        )

        return sql, params

    def get_prep_lookup(self) -> list:
        if self.rhs_is_direct_value():
            target = self.lhs.target
            alias = target.model._meta.db_table

            base_field = target.model._meta.get_field(target.base_field)
            relative_field = target.model._meta.get_field(target.relative_field)

            base_lhs = base_field.get_col(alias, output_field=base_field)
            relative_lhs = relative_field.get_col(alias, output_field=relative_field)

            prepared_values = []

            for rhs in self.rhs:
                decomposed_values = decompose_value(rhs)

                # convert model instances to int for FK fields
                base_normalized_value = get_normalized_value(
                    decomposed_values[0], base_lhs
                )[0]
                relative__normalized_value = get_normalized_value(
                    decomposed_values[1], relative_lhs
                )[0]
                prepared_values.append(
                    (
                        base_field.get_prep_value(base_normalized_value),
                        relative_field.get_prep_value(relative__normalized_value),
                    )
                )

            return prepared_values

        return super().get_prep_lookup()

    def as_sql(self, compiler, connection):
        # TODO: support connection.ops.max_in_list_size()
        # process lhs
        target = self.lhs.target
        alias = target.model._meta.db_table
        base_lhs = target.model._meta.get_field(target.base_field).get_col(alias)
        relative_lhs = target.model._meta.get_field(target.relative_field).get_col(
            alias
        )
        base_lhs_sql, base_lhs_params = self.process_lhs(
            compiler, connection, lhs=base_lhs
        )
        relative_lhs_sql, relative_lhs_params = self.process_lhs(
            compiler, connection, lhs=relative_lhs
        )

        # process rhs
        _, rhs_params = self.process_rhs(compiler, connection)
        rhs_sql = "IN (" + ", ".join(["(%s, %s)"] * len(rhs_params)) + ")"

        # combine
        params = sum(rhs_params, [])
        sql = f"({base_lhs_sql}, {relative_lhs_sql}) {rhs_sql}"

        return sql, params
