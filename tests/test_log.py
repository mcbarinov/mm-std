from mm_std import init_logger


def test_init_logger():
    logger = init_logger(name="log1")
    assert logger.name == "log1"
