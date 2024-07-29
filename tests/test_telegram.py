import pytest
from mm_std.telegram import send_telegram_message

pytestmark = pytest.mark.telegram


def test_send_telegram_message_short_message(telegram_token, telegram_chat_id):
    res = send_telegram_message(telegram_token, telegram_chat_id, "bla")
    assert len(res.unwrap()) == 1


def test_send_telegram_message_long_message(telegram_token, telegram_chat_id):
    message = ""
    for i in range(1800):
        message += f"{i} "
    res = send_telegram_message(telegram_token, telegram_chat_id, message)
    assert len(res.unwrap()) == 2
