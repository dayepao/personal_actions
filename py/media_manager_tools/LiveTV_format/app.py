import os
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, Response, jsonify, request
from utils_app import http_request

app = Flask(__name__)


# 初始化缓存文件
def load_cached_epg_xml():
    """加载缓存文件，如果不存在或过期，则重新下载"""
    if os.path.exists(CACHE_FILE_PATH):
        # 检查缓存文件是否过期
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(CACHE_FILE_PATH))
        if datetime.now() - file_mod_time > CACHE_EXPIRY_TIME:
            # 缓存过期，重新下载文件
            update_cached_epg_xml()
    else:
        # 文件不存在，下载
        update_cached_epg_xml()

    with open(CACHE_FILE_PATH, "r") as file:
        return file.read()


# 下载并更新缓存的 EPG XML 文件
def update_cached_epg_xml():
    """下载 EPG XML 文件并更新缓存"""
    try:
        response = http_request("get", EPG_XML_URL)
        if response.status_code == 200:
            with open(CACHE_FILE_PATH, "w") as file:
                file.write(response.text)
            print(f"EPG XML file updated at {datetime.now()}")
        else:
            print(f"Failed to fetch EPG XML file. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error updating EPG XML file: {e}")


# 定时任务更新缓存文件
def schedule_update_epg_xml():
    """定时任务，每24小时更新一次TXT文件"""
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_cached_epg_xml, "interval", hours=24)
    scheduler.start()


@app.route("/modify_m3u", methods=["POST"])
def modify_m3u():
    url = request.json.get("url")
    if not url:
        return jsonify({"error": "Missing URL parameter"}), 400

    try:
        # 获取并加载TXT文件缓存
        txt_content = load_cached_epg_xml()

        # 下载M3U文件
        response = http_request("get", url)
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch M3U file from URL"}), 500

        m3u_content = response.text

        # 修改M3U文件的内容
        modified_m3u_content = modify_m3u_file(m3u_content, txt_content)

        # 返回修改后的M3U文件内容
        return Response(modified_m3u_content, mimetype="application/vnd.apple.mpegurl")

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def modify_m3u_file(m3u_content, txt_content):
    """
    处理M3U文件内容的逻辑，可以根据需求自定义修改。
    这里可以使用txt_content作为参考，对M3U文件进行修改。
    """
    lines = m3u_content.splitlines()
    modified_lines = []
    for line in lines:
        if line.strip().startswith("#EXTINF"):
            line = "#EXTINF:-1, Modified with TXT " + line
        modified_lines.append(line)

    return "\n".join(modified_lines)


if __name__ == "__main__":
    # 配置EPG缓存文件路径和缓存过期时间
    CACHE_FILE_PATH = "e.xml"
    CACHE_EXPIRY_TIME = timedelta(days=1)  # 缓存过期时间为1天
    EPG_XML_URL = "http://epg.51zmt.top:8000/e.xml"  # EPG XML文件URL

    # 启动定时任务
    schedule_update_epg_xml()
    app.run(debug=True)
