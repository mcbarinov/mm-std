import socket
import time
from typing import cast


def check_port(ip: str, port: int, attempts: int = 3, sleep_seconds: float = 1, timeout: float = 1) -> bool:
    for _ in range(attempts):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        res = sock.connect_ex((ip, port)) == 0
        if res:
            return True
        time.sleep(sleep_seconds)
    return False


def get_free_local_port() -> int:
    sock = socket.socket()
    sock.bind(("", 0))
    port = sock.getsockname()[1]
    sock.close()
    return cast(int, port)
