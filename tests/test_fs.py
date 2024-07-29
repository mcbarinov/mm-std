from mm_std import fs


def test_read_text():
    assert len(fs.read_text("pyproject.toml")) > 100


def test_get_filename_without_extension():
    assert fs.get_filename_without_extension("/mnt/Token.tar.gz") == "Token.tar"
    assert fs.get_filename_without_extension("/mnt/Token.abi") == "Token"
    assert fs.get_filename_without_extension("/Token") == "Token"
    assert fs.get_filename_without_extension("Token") == "Token"
