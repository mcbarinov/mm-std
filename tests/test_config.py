from decimal import Decimal
from pathlib import Path

from mm_std import BaseConfig


class Config(BaseConfig):
    name: str
    tags: list[str]
    value: Decimal


def test_read_toml_config(tmp_path: Path):
    data = """
    name = "config"
    tags = ["tag1", "tag2"]
    value = 123.456
    """

    config_path = tmp_path / "config.toml"
    config_path.write_text(data)

    res = Config.read_toml_config_or_exit(config_path)

    assert res == Config(name="config", tags=["tag1", "tag2"], value=Decimal("123.456"))
