from __future__ import annotations

import enum
import json
from typing import Any

import pydash
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

from mm_std.result import Result


@enum.unique
class HttpError(str, enum.Enum):
    TIMEOUT = "timeout"
    PROXY = "proxy"
    CONNECTION = "connection"
    ERROR = "error"


class HttpResponse:
    status_code: int | None
    error: HttpError | None
    error_message: str | None
    body: str | None
    headers: dict[str, str] | None

    def __init__(
        self,
        status_code: int | None = None,
        error: HttpError | None = None,
        error_message: str | None = None,
        body: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status_code = status_code
        self.error = error
        self.error_message = error_message
        self.body = body
        self.headers = headers

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

    def to_result_failure[T](self, error: str | Exception | tuple[str, Exception] | None = None) -> Result[T]:
        return Result.failure(error or self.error or "error", extra=self.to_dict())

    def to_result_success[T](self, result: T) -> Result[T]:
        return Result.success(result, extra=self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        return {
            "status_code": self.status_code,
            "error": self.error.value if self.error else None,
            "error_message": self.error_message,
            "body": self.body,
            "headers": self.headers,
        }

    @property
    def content_type(self) -> str | None:
        if self.headers is None:
            return None
        for key in self.headers:
            if key.lower() == "content-type":
                return self.headers[key]
        return None

    def __repr__(self) -> str:
        parts: list[str] = []
        if self.status_code is not None:
            parts.append(f"status_code={self.status_code!r}")
        if self.error is not None:
            parts.append(f"error={self.error!r}")
        if self.error_message is not None:
            parts.append(f"error_message={self.error_message!r}")
        if self.body is not None:
            parts.append(f"body={self.body!r}")
        if self.headers is not None:
            parts.append(f"headers={self.headers!r}")
        return f"HttpResponse({', '.join(parts)})"

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: type[Any], _handler: GetCoreSchemaHandler) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.any_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda x: x.to_dict()),
        )

    @classmethod
    def _validate(cls, value: object) -> HttpResponse:
        if isinstance(value, cls):
            return value
        if isinstance(value, dict):
            return cls(
                status_code=value.get("status_code"),
                error=HttpError(value["error"]) if value.get("error") else None,
                error_message=value.get("error_message"),
                body=value.get("body"),
                headers=value.get("headers"),
            )
        raise TypeError(f"Invalid value for HttpResponse: {value}")
