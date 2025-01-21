import io
import sys
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, ValidationError

from .print_ import print_plain
from .result import Err, Ok, Result
from .str import str_to_list
from .zip import read_text_from_zip_archive


class BaseConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @classmethod
    def to_list_str_validator(
        cls,
        v: str | list[str] | None,
        *,
        lower: bool = False,
        unique: bool = False,
        remove_comments: bool = False,
        split_line: bool = False,
    ) -> list[str]:
        if v is None:
            return []
        if isinstance(v, str):
            return str_to_list(v, unique=unique, remove_comments=remove_comments, split_line=split_line, lower=lower)
        return v

    @classmethod
    def read_config[T](cls: type[T], config_path: io.TextIOWrapper | str | Path, zip_password: str = "") -> Result[T]:  # nosec
        try:
            # is it zip archive?
            if isinstance(config_path, str) and config_path.endswith(".zip"):
                config_path = str(Path(config_path).expanduser())
                return Ok(cls(**yaml.full_load(read_text_from_zip_archive(config_path, password=zip_password))))
            if isinstance(config_path, io.TextIOWrapper) and config_path.name.endswith(".zip"):
                config_path = str(Path(config_path.name).expanduser())
                return Ok(cls(**yaml.full_load(read_text_from_zip_archive(config_path, password=zip_password))))
            if isinstance(config_path, Path) and config_path.name.endswith(".zip"):
                config_path = str(config_path.expanduser())
                return Ok(cls(**yaml.full_load(read_text_from_zip_archive(config_path, password=zip_password))))

            # plain yml file
            if isinstance(config_path, str):
                return Ok(cls(**yaml.full_load(Path(config_path).expanduser().read_text())))
            if isinstance(config_path, Path):
                return Ok(cls(**yaml.full_load(config_path.expanduser().read_text())))

            return Ok(cls(**yaml.full_load(config_path)))
        except ValidationError as err:
            return Err("validator_error", data={"errors": err.errors()})
        except Exception as err:
            return Err(err)

    @classmethod
    def read_config_or_exit[T](cls: type[T], config_path: io.TextIOWrapper | str | Path, zip_password: str = "") -> T:  # noqa: PYI019 # nosec
        res = cls.read_config(config_path, zip_password)  # type: ignore[attr-defined]
        if isinstance(res, Ok):
            return res.unwrap()  # type: ignore[no-any-return]

        if res.err == "validator_error":
            print_plain("config validation errors")
            for e in res.data["errors"]:
                loc = e["loc"]
                field = ".".join(str(lo) for lo in loc) if len(loc) > 0 else ""
                print_plain(f"{field} {e['msg']}")
        else:
            print_plain(f"can't parse config file: {res.err}")

        sys.exit(1)
