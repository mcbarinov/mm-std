from mm_std import replace_empty_values


def test_replace_empty_values():
    data = {"a": None, "b": 0, "c": [], "d": 111}
    defaults = {"a": "bla", "b": 1, "c": [1, 2, 3]}
    replace_empty_values(data, defaults)
    assert data == {"a": "bla", "b": 1, "c": [1, 2, 3], "d": 111}
