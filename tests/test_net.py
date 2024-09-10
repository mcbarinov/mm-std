import os
from urllib.parse import urlencode, urlparse

from dotenv import load_dotenv
from pytest_httpserver import HTTPServer
from werkzeug import Request, Response

from mm_std import FIREFOX_USER_AGENT, check_port, hrequest, json_dumps
from mm_std.net import add_query_params_to_url, get_free_local_port, hr


def test_custom_user_agent(httpserver: HTTPServer):
    def handler(request: Request) -> Response:
        return Response(json_dumps({"user-agent": request.headers["user-agent"]}), content_type="application/json")

    httpserver.expect_request("/test").respond_with_handler(handler)
    user_agent = "moon cat"
    res = hrequest(httpserver.url_for("/test"), user_agent=user_agent)
    assert res.json["user-agent"] == user_agent


def test_json_parse_error():
    res = hrequest("https://httpbin.org")
    assert res.json_parse_error


def test_firefox_user_agent(httpserver: HTTPServer):
    data = {"user_agent": FIREFOX_USER_AGENT}
    httpserver.expect_request("/user-agent").respond_with_json(data)
    res = hrequest(httpserver.url_for("/user-agent"))
    assert res.json == data


def test_get_params(httpserver: HTTPServer):
    data = {"a": 123, "b": "bla bla"}
    httpserver.expect_request("/test", query_string="a=123&b=bla%20bla").respond_with_json(data)
    res = hrequest(httpserver.url_for("test"), params=data)
    assert res.json == data


def test_post_method(httpserver: HTTPServer):
    data = {"a": 1}
    httpserver.expect_request("/test", query_string=urlencode(data)).respond_with_json(data)
    res = hrequest(httpserver.url_for("test"), params=data)
    assert res.json == data


def test_timeout():
    res = hrequest("https://httpbin.org/delay/10", timeout=2)
    assert res.error == "timeout"
    assert res.is_timeout_error()


def test_proxy_error():
    res = hrequest("https://httpbin.org/ip", proxy="https://google.com")
    assert res.error == "proxy_error"
    assert res.is_proxy_error()


def test_connection_error():
    res = hrequest("https://httpbin222.org/ip", timeout=2)
    assert res.error.startswith("connection_error")


def test_to_ok_result(httpserver: HTTPServer):
    data = {"a": 1}
    httpserver.expect_request(
        "/test",
    ).respond_with_json(data)
    res = hrequest(httpserver.url_for("test"))
    assert res.to_ok_result(res.json).ok == data
    assert res.to_ok_result(res.json).is_ok()
    assert res.to_ok_result(res.json).data["code"] == 200


def test_to_error():
    res = hrequest("https://httpbin222.org/ip")
    assert res.to_err_result().data["code"] == res.code
    assert res.to_err_result().is_err()
    assert res.to_err_result().err.startswith("connection_error")
    assert res.is_connection_error()

    res = hrequest("https://httpbin222.org/ip")
    assert res.to_err_result("bla").err == "bla"


def test_proxy():
    load_dotenv()
    proxy_url = os.getenv("PROXY", "")
    proxy = urlparse(proxy_url)
    res = hr("https://httpbin.org/ip", proxy=proxy_url, timeout=5)
    assert proxy.hostname in res.json["origin"]


def test_check_port():
    assert check_port("8.8.8.8", 443)
    assert not check_port("8.8.8.8", 111)


def test_get_free_local_port():
    p1 = get_free_local_port()
    p2 = get_free_local_port()
    assert p1 != p2


def test_http_response_content_type(httpserver: HTTPServer):
    def handler(_request: Request) -> Response:
        return Response("aaa", content_type="custom/text")

    httpserver.expect_request("/test1").respond_with_json({"a": 1})
    httpserver.expect_request("/test2").respond_with_handler(handler)

    res = hrequest(httpserver.url_for("test1"))
    assert res.content_type == "application/json"

    res = hrequest(httpserver.url_for("test2"))
    assert res.content_type == "custom/text"


def test_add_query_params_to_url():
    res = add_query_params_to_url("url", {"a": 1, "b": "a  b  c"})
    assert res == "url?a=1&b=a++b++c"

    res = add_query_params_to_url("url", {"a": 1, "b": None})
    assert res == "url?a=1"
