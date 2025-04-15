import enum
import json
from typing import Any

import pydash
from pydantic import BaseModel

from mm_std.data_result import DataResult


@enum.unique
class HttpError(str, enum.Enum):
    TIMEOUT = "timeout"
    PROXY = "proxy"
    CONNECTION = "connection"
    ERROR = "error"


class HttpResponse(BaseModel):
    status_code: int | None = None
    error: HttpError | None = None
    error_message: str | None = None
    body: str | None = None
    headers: dict[str, str] | None = None

    def parse_json_body(self, path: str | None = None, none_on_error: bool = False) -> Any:  # noqa: ANN401
        if self.body is None:
            if none_on_error:
                return None
            raise ValueError("Body is None")

        try:
            res = json.loads(self.body)
            return pydash.get(res, path, None) if path else res
        except json.JSONDecodeError:
            if none_on_error:
                return None
            raise

    def is_error(self) -> bool:
        return self.error is not None or (self.status_code is not None and self.status_code >= 400)

    def to_data_result_err[T](self, error: str | None = None) -> DataResult[T]:
        return DataResult.err(error or self.error or "error", self.model_dump())

    def to_data_result_ok[T](self, result: T) -> DataResult[T]:
        return DataResult.ok(result, self.model_dump())
