import sys
import time

import httpx


def http_request(method_name: str, url: str, timeout=5, max_retries=5, c: httpx.Client = None, **kwargs) -> httpx.Response:
    """
    发送 HTTP 请求

    method: 请求方法，如 'get', 'post', 'put', 'delete'等

    url: 请求的URL

    timeout: 超时时间, 单位秒(s), 默认为 5 秒, 为 `None` 时禁用

    max_retries: 最大尝试次数, 默认为 5 次, 为 0 时禁用

    c: httpx.Client 对象

    **kwargs: 其他传递给 httpx 请求方法的参数, 如 headers, data, json, verify 等
    """
    method_name = method_name.lower()  # 先转换为小写

    if not method_name:
        raise ValueError("请求方法不能为空")

    try:
        if c is not None:
            request_method = getattr(c, method_name)
        else:
            request_method = getattr(httpx, method_name)
    except AttributeError:
        raise ValueError(f"不支持的请求方法: '{method_name}'")

    attempt_count = 1
    while (attempt_count <= max_retries) or (max_retries == 0):
        try:
            res = request_method(url=url, timeout=timeout, **kwargs)
        except Exception as e:
            attempt_count = attempt_count + 1
            print(f"{sys._getframe().f_code.co_name} 出错: {str(e)}")
            time.sleep(1)
            continue
        else:
            break
    try:
        return res
    except Exception:
        raise RuntimeError(f"{sys._getframe().f_code.co_name} 出错: 已达到最大重试次数")
