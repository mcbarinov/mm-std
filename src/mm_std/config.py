import sys
import tomllib
from pathlib import Path
from typing import Any, NoReturn, Self, TypeVar

from pydantic import BaseModel, ConfigDict, ValidationError

from .print_ import print_json, print_plain
from .result import Result
from .zip import read_text_from_zip_archive

T = TypeVar("T", bound="BaseConfig")


class BaseConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    def print_and_exit(self, exclude: set[str] | None = None) -> NoReturn:
        print_json(self.model_dump(exclude=exclude))
        sys.exit(0)

    @classmethod
    def read_toml_config_or_exit(cls, config_path: Path, zip_password: str = "") -> Self:  # nosec
        res: Result[Self] = cls.read_toml_config(config_path, zip_password)
        if res.is_ok():
            return res.unwrap()
        cls._print_error_and_exit(res)

    @classmethod
    async def read_toml_config_or_exit_async(cls, config_path: Path, zip_password: str = "") -> Self:  # nosec
        res: Result[Self] = await cls.read_toml_config_async(config_path, zip_password)
        if res.is_ok():
            return res.unwrap()
        cls._print_error_and_exit(res)

    @classmethod
    def read_toml_config(cls, config_path: Path, zip_password: str = "") -> Result[Self]:  # nosec
        try:
            config_path = config_path.expanduser()
            if config_path.name.endswith(".zip"):
                data = tomllib.loads(read_text_from_zip_archive(config_path, password=zip_password))
            else:
                with config_path.open("rb") as f:
                    data = tomllib.load(f)
            return Result.success(cls(**data))
        except ValidationError as e:
            return Result.failure(("validator_error", e), extra={"errors": e.errors()})
        except Exception as e:
            return Result.failure(e)

    @classmethod
    async def read_toml_config_async(cls, config_path: Path, zip_password: str = "") -> Result[Self]:  # nosec
        try:
            config_path = config_path.expanduser()
            if config_path.name.endswith(".zip"):
                data = tomllib.loads(read_text_from_zip_archive(config_path, password=zip_password))
            else:
                with config_path.open("rb") as f:
                    data = tomllib.load(f)
            model = await cls.model_validate_async(data)  # type:ignore[attr-defined]
            return Result.success(model)
        except ValidationError as e:
            return Result.failure(("validator_error", e), extra={"errors": e.errors()})
        except Exception as e:
            return Result.failure(e)

    @classmethod
    def _print_error_and_exit(cls, res: Result[Any]) -> NoReturn:
        if res.error == "validator_error" and res.extra:
            print_plain("config validation errors")
            for e in res.extra["errors"]:
                loc = e["loc"]
                field = ".".join(str(lo) for lo in loc) if len(loc) > 0 else ""
                print_plain(f"{field} {e['msg']}")
        else:
            print_plain(f"can't parse config file: {res.error}")
        sys.exit(1)
