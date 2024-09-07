import pytest

from mm_std import get_dotenv


@pytest.fixture
def telegram_token() -> str:
    return get_dotenv("TELEGRAM_TOKEN")


@pytest.fixture
def telegram_chat_id() -> int:
    return int(get_dotenv("TELEGRAM_CHAT_ID"))
