import os
import time
from urllib.parse import urlencode, urlparse

import pytest
from dotenv import load_dotenv
from pytest_httpserver import HTTPServer
from werkzeug import Request, Response

from mm_std import http_request, json_dumps

pytestmark = pytest.mark.anyio


async def test_json_path(httpserver: HTTPServer):
    httpserver.expect_request("/test").respond_with_json({"a": {"b": {"c": 123}}})
    res = await http_request(httpserver.url_for("/test"))
    assert res.json("a.b.c") == 123


async def test_json_path_not_exists(httpserver: HTTPServer):
    def handler(_request: Request) -> Response:
        raise RuntimeError

    httpserver.expect_request("/test").respond_with_handler(handler)
    res = await http_request(httpserver.url_for("/test"))
    assert res.json("a.b.c") is None


async def test_custom_user_agent(httpserver: HTTPServer):
    def handler(request: Request) -> Response:
        return Response(json_dumps({"user-agent": request.headers["user-agent"]}), content_type="application/json")

    httpserver.expect_request("/test").respond_with_handler(handler)
    user_agent = "moon cat"
    res = await http_request(httpserver.url_for("/test"), user_agent=user_agent)
    assert res.json()["user-agent"] == user_agent


async def test_json_parse_error():
    res = await http_request("https://httpbin.org")
    assert res.is_json_parse_error()


async def test_params(httpserver: HTTPServer):
    data = {"a": 123, "b": "bla bla"}
    httpserver.expect_request("/test", query_string="a=123&b=bla+bla").respond_with_json(data)
    res = await http_request(httpserver.url_for("/test"), params=data)
    assert res.json() == data


async def test_post_with_params(httpserver: HTTPServer):
    data = {"a": 1}
    httpserver.expect_request("/test", query_string=urlencode(data)).respond_with_json(data)
    res = await http_request(httpserver.url_for("/test"), params=data)
    assert res.json() == data


async def test_timeout(httpserver: HTTPServer):
    def handler(_request: Request) -> Response:
        time.sleep(2)
        return Response("ok")

    httpserver.expect_request("/test").respond_with_handler(handler)
    res = await http_request(httpserver.url_for("/test"), timeout=1)
    assert res.error == "timeout"


async def test_proxy_http():
    load_dotenv()
    proxy_url = os.getenv("PROXY_HTTP", "")
    proxy = urlparse(proxy_url)
    res = await http_request("https://api.ipify.org?format=json", proxy=proxy_url, timeout=5)
    assert proxy.hostname in res.json()["ip"]


async def test_proxy_socks5():
    load_dotenv()
    proxy_url = os.getenv("PROXY_SOCKS5", "")
    proxy = urlparse(proxy_url)
    res = await http_request("https://api.ipify.org?format=json", proxy=proxy_url, timeout=5)
    assert proxy.hostname in res.json()["ip"]
