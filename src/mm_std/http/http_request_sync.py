from typing import Any

import requests

from mm_std.http.response import HttpError, HttpResponse


def http_request_sync(
    url: str,
    *,
    method: str = "GET",
    params: dict[str, Any] | None = None,
    data: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    cookies: dict[str, Any] | None = None,
    user_agent: str | None = None,
    proxy: str | None = None,
    timeout: float | None = 10.0,
) -> HttpResponse:
    """
    Send a synchronous HTTP request and return the response.
    """
    if user_agent:
        if headers is None:
            headers = {}
        headers["User-Agent"] = user_agent

    proxies: dict[str, str] | None = None
    if proxy:
        proxies = {
            "http": proxy,
            "https": proxy,
        }

    try:
        res = requests.request(
            method=method,
            url=url,
            params=params,
            data=data,
            json=json,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            proxies=proxies,
        )
        return HttpResponse(
            status_code=res.status_code,
            error=None,
            error_message=None,
            body=res.text,
            headers=dict(res.headers),
        )
    except requests.Timeout as err:
        return HttpResponse(error=HttpError.TIMEOUT, error_message=str(err))
    except Exception as err:
        return HttpResponse(error=HttpError.ERROR, error_message=str(err))
