import httpx

from utils_dayepao import get_method

if __name__ == "__main__":
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31",
        "origin": "https://hostloc.com",
        "referer": "https://hostloc.com/",
    }
    c = httpx.Client()
    c.headers.update(headers=headers)
    print(c.headers)
    get_method('http://httpbin.org/cookies/set/sessioncookie/a123456789', c=c)
    res = get_method("http://httpbin.org/cookies", c=c, headers={"a": "b"})
    print(res.request.headers)
    res = get_method("http://httpbin.org/cookies", c=c)
    print(res.request.headers)
    print(c.headers)
    c.headers.clear()
    print(c.headers)
