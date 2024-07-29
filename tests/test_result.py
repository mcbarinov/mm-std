from mm_std import Err, Ok


def test_basics() -> None:
    v1 = Ok(1, data=2)
    assert v1.ok == 1 and v1.data == 2 and v1.err is None

    v2 = Err("a", data=2)
    assert v2.err == "a" and v2.data == 2 and v2.ok is None

    v3 = Err(ValueError("zzz"))
    assert v3.err == "exception: zzz"


def test_ok_map() -> None:
    assert Ok(1, data=[1, 2, 3]).map(lambda o: f"a{o}") == Ok("a1", data=[1, 2, 3])


def testand_then():
    assert Ok(1, data=2).and_then(lambda o: Ok(f"a{o}")) == Ok("a1", data=2)
    assert Ok(1, data=2).and_then(lambda o: f"a{o}") == Ok("a1", data=2)
    assert Err("a", data=2).and_then(lambda o: Ok(f"a{o}")) == Err("a", data=2)


def test_and_then_with_exception():
    assert Ok(1, data=[1, 2, 3]).and_then(lambda o: 2 / 0) == Err("exception: division by zero", data=[1, 2, 3])


def test_ok_or_err():
    assert Ok(1, data=2).ok_or_err() == 1
    assert Err("a", data=2).ok_or_err() == "a"


def test_map_or_else():
    assert Ok(1).map_or_else(lambda err: int(err) + 1, lambda ok: ok + 1) == 2
    assert Err("1").map_or_else(lambda err: int(err) + 1, lambda ok: ok + 1) == 2


def test_ok_or_none():
    assert Ok(1).ok_or_none() == 1
    assert Err("bla").ok_or_none() is None


# def test_pydandic_with_result():
#     class A(BaseModel):
#         name: str
#         value: Result[int]
#
#     a = A(value=Ok(1), name="s1")
#     print(a)
#
#     assert a.value == Ok(1)
