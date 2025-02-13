import json
from collections.abc import Callable
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from json import JSONEncoder
from pathlib import Path

from pydantic import BaseModel

from mm_std.result import Err, Ok


class CustomJSONEncoder(JSONEncoder):
    def default(self, o: object) -> object:
        if isinstance(o, Ok):
            return {"ok": o.ok}
        if isinstance(o, Err):
            return {"err": o.err}
        if isinstance(o, Decimal):
            return str(o)
        if isinstance(o, Path):
            return str(o)
        if isinstance(o, datetime | date):
            return o.isoformat()
        if is_dataclass(o) and not isinstance(o, type):
            return asdict(o)
        if isinstance(o, Enum):
            return o.value
        if isinstance(o, BaseModel):
            return o.model_dump()
        if isinstance(o, Exception):
            return str(o)

        return super().default(o)


def json_dumps(data: object, default_serializer: Callable[[object], str] | None = str) -> str:
    return json.dumps(data, cls=CustomJSONEncoder, default=default_serializer)
