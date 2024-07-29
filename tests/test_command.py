from mm_std import run_command


def test_run_command():
    # stdout
    res = run_command("echo abc 123")
    assert res.stdout.strip() == "abc 123"

    # stderr
    res = run_command("cat /no/such/path")
    assert res.stderr.strip() == "cat: /no/such/path: No such file or directory"

    # out
    res = run_command("echo abc 123")
    assert res.out.strip() == "abc 123"


def test_timeout():
    res = run_command("sleep 2", timeout=1)
    assert res.out == "timeout"
