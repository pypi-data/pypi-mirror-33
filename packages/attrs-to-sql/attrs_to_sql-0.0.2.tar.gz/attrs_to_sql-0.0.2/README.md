# attrs to sql

Convert [attrs](https://github.com/python-attrs/attrs) class to sql `CREATE TABLE` command.

# Usage 

Define class decorated with `attr.s`:

```python
@attr.s(auto_attribs=True)
class Model:
    id: int = attr.ib(metadata={"primary_key": True})
    name: str = attr.ib(metadata={"not_null": True, "length": 30})
    floats: List[float] = attr.ib(factory=list)
```

Run `attrs_to_table` with defined class:

```python
from attrs_to_sql import attrs_to_table

attrs_to_table(Model)
```

Output:

```sql
CREATE TABLE public.model
(
    id int PRIMARY KEY,
    name varchar(30) NOT NULL,
    floats float[]
);
```
