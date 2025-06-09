# mm-std

A collection of Python utilities for common data manipulation tasks with strict type safety and modern Python support.

## Features

- **JSON Utilities**: Extended JSON encoder with support for datetime, UUID, Decimal, dataclasses, enums, and Pydantic models
- **Dictionary Utilities**: Advanced dictionary manipulation with type preservation
- **Date Utilities**: UTC-focused datetime operations and flexible date parsing
- **Random Utilities**: Type-safe random generation for decimals and datetimes
- **Full Type Safety**: Strict mypy compliance with comprehensive type annotations

## Quick Start

### JSON Utilities

Extended JSON serialization with automatic handling of Python types:

```python
from mm_std import json_dumps, ExtendedJSONEncoder
from datetime import datetime
from decimal import Decimal
from uuid import UUID

data = {
    "timestamp": datetime.now(),
    "price": Decimal("19.99"),
    "user_id": UUID("12345678-1234-5678-1234-567812345678"),
    "tags": {"python", "json"}  # set will be converted to list
}

# Simple serialization
json_str = json_dumps(data)

# Custom type handlers for specific use cases
json_str = json_dumps(data, type_handlers={
    Decimal: lambda d: float(d)  # Convert Decimal to float instead of string
})
```

### Dictionary Utilities

Clean up dictionaries by replacing or removing empty values:

```python
from mm_std import replace_empty_dict_entries

data = {
    "name": "John",
    "age": None,
    "email": "",
    "score": 0,
    "active": False
}

# Remove empty entries entirely
cleaned = replace_empty_dict_entries(data)
# Result: {"name": "John"}

# Replace with defaults
defaults = {"age": 25, "email": "unknown@example.com"}
cleaned = replace_empty_dict_entries(data, defaults=defaults)
# Result: {"name": "John", "age": 25, "email": "unknown@example.com"}

# Treat zero and false as empty too
cleaned = replace_empty_dict_entries(
    data,
    defaults=defaults,
    treat_zero_as_empty=True,
    treat_false_as_empty=True
)
```

### Date Utilities

UTC-focused datetime operations:

```python
from mm_std import utc_now, utc_delta, parse_date

# Current UTC time
now = utc_now()

# Time calculations
past = utc_delta(hours=-2, minutes=-30)
future = utc_delta(days=7)

# Flexible date parsing
dates = [
    "2023-12-25",
    "2023-12-25T10:30:00Z",
    "2023-12-25 10:30:00.123456+00:00",
    "2023/12/25"
]

parsed_dates = [parse_date(d) for d in dates]

# Parse and ignore timezone info
local_time = parse_date("2023-12-25T10:30:00+02:00", ignore_tz=True)
```

### Random Utilities

Generate random values with precision:

```python
from mm_std import random_decimal, random_datetime
from decimal import Decimal
from datetime import datetime

# Random decimal with preserved precision
price = random_decimal(Decimal("10.00"), Decimal("99.99"))

# Random datetime within a range
base_time = datetime.now()
random_time = random_datetime(
    base_time,
    hours=24,      # Up to 24 hours later
    minutes=30,    # Plus up to 30 minutes
    seconds=45     # Plus up to 45 seconds
)
```
