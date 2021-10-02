import httpx

from utils_dayepao import get_content_in_website

if __name__ == "__main__":
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31",
        "origin": "https://hostloc.com",
        "referer": "https://hostloc.com/",
    }
    c = httpx.Client()
    c.headers.update(headers=headers)
    print(get_content_in_website("https://hostloc.com/forum.php", r'今日: <em>(.+?)</em>'))
    # print(get_method("https://hostloc.com/forum.php").text)
