import enum
import json
from typing import Any

import pydash
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


@enum.unique
class HttpError(str, enum.Enum):
    TIMEOUT = "timeout"
    PROXY = "proxy"
    CONNECTION = "connection"
    ERROR = "error"


class HttpResponse:
    def __init__(
        self,
        status: int | None = None,
        error: HttpError | None = None,
        error_message: str | None = None,
        body: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status = status
        self.error = error
        self.error_message = error_message
        self.body = body
        self.headers = headers

        self._json_data: Any = None
        self._json_parsed = False
        self._json_parsed_error = False

    def _parse_json(self) -> None:
        if self.body is None:
            self._json_parsed_error = True
            return
        try:
            self._json_data = None
            self._json_data = json.loads(self.body)
            self._json_parsed_error = False
        except json.JSONDecodeError:
            self._json_parsed_error = True
        self._json_parsed = True

    def json(self, path: str | None = None) -> Any:  # noqa: ANN401
        if not self._json_parsed:
            self._parse_json()
        if path:
            return pydash.get(self._json_data, path, None)
        return self._json_data

    def dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "error": self.error,
            "error_message": self.error_message,
            "body": self.body,
            "headers": self.headers,
        }

    def is_json_parse_error(self) -> bool:
        if not self._json_parsed:
            self._parse_json()
        return self._json_parsed_error

    def __repr__(self) -> str:
        return f"HttpResponse(status={self.status}, error={self.error}, error_message={self.error_message}, body={self.body}, headers={self.headers})"  # noqa: E501

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: type[Any], handler: GetCoreSchemaHandler) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.any_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda x: x.dict()),
        )

    @classmethod
    def _validate(cls, v: object) -> "HttpResponse":
        if isinstance(v, cls):
            return v
        if isinstance(v, dict):
            return cls(
                status=v.get("status"),
                error=HttpError(v["error"]) if v.get("error") else None,
                error_message=v.get("error_message"),
                body=v.get("body"),
                headers=v.get("headers"),
            )
        raise TypeError(f"Cannot parse value as {cls.__name__}: {v}")
