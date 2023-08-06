from datetime import datetime
from typing import List
import attr
from attrs_to_sql.table import attrs_to_table


@attr.s(auto_attribs=True)
class SampleModel:
    id: int = attr.ib(metadata={"primary_key": True, "type": "bigint", "auto_inc": True})
    title: str = attr.ib(metadata={"not_null": True, "length": 30})
    ids: list = attr.ib(metadata={"type": "bigint[]"})
    default_int: int = 1
    created_datetime: datetime = attr.ib(factory=datetime.now)
    ints: List[int] = attr.ib(factory=list)
    default_float: float = 2.5


def test_attrs_to_table():
    with open("tests/data/model.sql", encoding="utf-8") as f:
        expected_sql = f.read()

    actual_sql = attrs_to_table(SampleModel)

    assert actual_sql == expected_sql
