import sys
from collections.abc import Callable
from enum import Enum, unique
from typing import Any, NoReturn

import rich
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

from mm_std.json_ import json_dumps


@unique
class PrintFormat(str, Enum):
    PLAIN = "plain"
    TABLE = "table"
    JSON = "json"


def fatal(message: str, code: int = 1) -> NoReturn:
    print(message, file=sys.stderr)  # noqa: T201
    sys.exit(code)


def print_console(*messages: object, print_json: bool = False, default: Callable[[object], str] | None = str) -> None:
    if len(messages) == 1:
        message = messages[0]
        if isinstance(message, str):
            print(message)  # noqa: T201
        elif print_json:
            rich.print_json(json_dumps(message, default_serializer=default))
        else:
            rich.print(message)
    else:
        rich.print(messages)


def print_plain(messages: object) -> None:
    print(messages)  # noqa: T201


def print_json(data: object, default_serializer: Callable[[object], str] | None = None) -> None:
    rich.print_json(json_dumps(data, default_serializer=default_serializer))


def print_table(title: str, columns: list[str], rows: list[list[Any]]) -> None:
    table = Table(*columns, title=title)
    for row in rows:
        table.add_row(*(str(cell) for cell in row))
    console = Console()
    console.print(table)


def pretty_print_toml(data: str, line_numbers: bool = False, theme: str = "monokai") -> None:
    console = Console()
    syntax = Syntax(data, "toml", theme=theme, line_numbers=line_numbers)
    console.print(syntax)
