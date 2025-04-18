import asyncio
from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import model_validator

from mm_std import BaseConfig


class Config1(BaseConfig):
    name: str
    tags: list[str]
    value: Decimal


class Config2(BaseConfig):
    name: str
    tags: list[str]
    value: Decimal

    @model_validator(mode="after")
    async def final_validator(self) -> "Config2":
        await asyncio.sleep(0.1)
        self.name += "_async"
        return self


def test_read_toml_config(tmp_path: Path):
    data = """
    name = "config"
    tags = ["tag1", "tag2"]
    value = 123.456
    """

    config_path = tmp_path / "config.toml"
    config_path.write_text(data)

    res = Config1.read_toml_config_or_exit(config_path)

    assert res == Config1(name="config", tags=["tag1", "tag2"], value=Decimal("123.456"))


@pytest.mark.asyncio
async def test_read_toml_config_async(tmp_path: Path):
    data = """
    name = "config"
    tags = ["tag1", "tag2"]
    value = 123.456
    """

    config_path = tmp_path / "config.toml"
    config_path.write_text(data)

    res = await Config2.read_toml_config_or_exit_async(config_path)

    res2 = await Config2.model_validate({"name": "config", "tags": ["tag1", "tag2"], "value": Decimal("123.456")})

    assert res == res2
    assert res.name == "config_async"
