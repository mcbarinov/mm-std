from mm_std import check_port, get_free_local_port


def test_check_port():
    assert check_port("8.8.8.8", 443)
    assert not check_port("8.8.8.8", 111)


def test_get_free_local_port():
    p1 = get_free_local_port()
    p2 = get_free_local_port()
    assert p1 != p2
