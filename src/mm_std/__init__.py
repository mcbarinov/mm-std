"""mm-std: Python utilities for common data manipulation tasks."""

from .date_utils import parse_datetime as parse_datetime
from .date_utils import utc_from_timestamp as utc_from_timestamp
from .date_utils import utc_now as utc_now
from .date_utils import utc_now_offset as utc_now_offset
from .dict_utils import compact_dict as compact_dict
from .json_utils import ExtendedJSONEncoder as ExtendedJSONEncoder
from .json_utils import json_dumps as json_dumps
from .random_utils import random_datetime as random_datetime
from .random_utils import random_datetime_offset as random_datetime_offset
from .random_utils import random_decimal as random_decimal
from .str_utils import parse_lines as parse_lines
from .str_utils import str_contains_any as str_contains_any
from .str_utils import str_ends_with_any as str_ends_with_any
from .str_utils import str_starts_with_any as str_starts_with_any

# B404: re-exporting subprocess utilities with documented security considerations
from .subprocess_utils import CmdResult as CmdResult  # nosec
from .subprocess_utils import run_cmd as run_cmd  # nosec
from .subprocess_utils import run_ssh_cmd as run_ssh_cmd  # nosec
