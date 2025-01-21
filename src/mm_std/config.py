import io
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, ValidationError

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
            return Err("validator error", data={"validaton_errors": err})
        except Exception as err:
            return Err(err)
