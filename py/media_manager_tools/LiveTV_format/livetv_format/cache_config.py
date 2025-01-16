from datetime import timedelta
from pathlib import Path

CACHE_FILE_CONFIGS = {
    "epg.xml": {
        "CACHE_PATH": Path(__file__).parent.joinpath("tmp"),
        "CACHE_EXPIRY_TIME": timedelta(days=1),  # 缓存过期时间为1天
        "FILE_URL": "http://epg.51zmt.top:8000/e.xml"
    },
}
