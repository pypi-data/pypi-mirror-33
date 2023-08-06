from datetime import datetime
from typing import cast, Optional

import attr
from jinja2 import Environment, FileSystemLoader, Template

from .utils import camelcase_to_underscore

env = Environment(loader=FileSystemLoader("templates"), lstrip_blocks=True, trim_blocks=True)

PY_SQL_TYPES = {int: "int", datetime: "timestamp", str: "varchar", float: "float"}


def attrs_to_table(attrs: type) -> str:
    table = camelcase_to_underscore(attrs.__name__)

    fields = attr.fields(attrs)
    columns = map(_field_to_column, fields)

    template: Template = env.get_template("create_table.sql")
    return template.render(table=table, columns=columns)


def _field_to_column(field: attr.Attribute) -> str:
    column_name = field.name
    column_type = _build_column_type(field)

    column_str = f"{column_name} {column_type}"

    column_extra = _build_column_extra(field)
    if column_extra:
        column_str = f"{column_str} {column_extra}"

    return column_str


def _build_column_type(field: attr.Attribute) -> str:
    column_type = (
        cast(str, field.metadata.get("type"))
        or PY_SQL_TYPES.get(cast(type, field.type))
        or _try_set_array_type(field)
    )
    if not column_type:
        raise ValueError(f"Unsupported type: {field.type}")

    if field.metadata.get("length"):
        return _append_length(column_type, cast(int, field.metadata.get("length")))

    if field.metadata.get("auto_inc"):
        return _map_auto_inc(column_type)

    return column_type


def _try_set_array_type(field: attr.Attribute) -> Optional[str]:
    if not issubclass(cast(type, field.type), list):
        return None

    try:
        list_type = field.type.__args__[0]  # type: ignore
    except IndexError:
        raise ValueError("No array type provided.")

    list_type = PY_SQL_TYPES.get(list_type)
    if not list_type:
        return None

    return f"{list_type}[]"


def _append_length(column_type: str, length: int) -> str:
    if column_type == "varchar":
        return f"varchar({length})"

    raise ValueError("Only varchar supported.")


def _map_auto_inc(column_type: str) -> str:
    if column_type == "int":
        return "serial"

    if column_type == "bigint":
        return "bigserial"

    raise ValueError("Only integer type can be autoincremented.")


def _build_column_extra(field: attr.Attribute) -> str:
    column_extra = []

    if field.metadata.get("primary_key"):
        column_extra.append("PRIMARY KEY")

    has_default = field.default != attr.NOTHING
    immutable_default = not isinstance(field.default, cast(type, attr.Factory))
    if has_default and immutable_default:
        column_extra.append(f"DEFAULT {field.default}")

    if field.metadata.get("not_null"):
        column_extra.append("NOT NULL")

    column_extra_str = " ".join(column_extra)
    return column_extra_str
