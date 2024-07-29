from mm_std import get_dotenv


def test_dotenv():
    assert get_dotenv("TEST_DOTENV") == "777"
