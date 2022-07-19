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

        rhs_sql, rhs_params = self.process_rhs(compiler, connection)
        params = base_lhs_params + relative_lhs_params

        params.extend(rhs_params)

        rhs_sql = self.get_rhs_op(connection, rhs_sql)
        sql = f"{base_lhs_sql} {rhs_sql} AND {relative_lhs_sql} {rhs_sql}"

        return sql, params
