import os

from flask import Flask, Response, jsonify, request

from handle_cache import schedule_update_cached_file
import re
from handle_epg_xml import generate_tvg_map
from utils_app import http_request

app = Flask(__name__)


@app.route("/tv.m3u", methods=["GET"])
def modify_m3u():
    tv_m3u_url = os.getenv("TV_M3U_URL", request.args.get("url"))
    if not tv_m3u_url:
        return jsonify({"error": "Missing URL parameter"}), 400

    try:
        tvg_map = generate_tvg_map()

        # 下载M3U文件
        response = http_request("get", tv_m3u_url)
        if response.status_code != 200:
            return jsonify({"error": f"Failed to fetch M3U file from {tv_m3u_url}"}), 500

        m3u_content = response.text

        # 修改M3U文件的内容
        modified_m3u_content = format_m3u_file(m3u_content, tvg_map)

        # 返回修改后的M3U文件内容
        return Response(modified_m3u_content, mimetype="application/vnd.apple.mpegurl")

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def format_m3u_file(m3u_content, tvg_map):
    """
    处理M3U文件内容的逻辑，可以根据需求自定义修改。
    这里可以使用EPG XML 文件作为参考，对M3U文件进行修改。
    """
    pattern = re.compile(r'#EXTINF:(.+?)[,\s]+tvg-id="([^"]+)"\s+tvg-name="([^"]+)"\s+tvg-logo="([^"]+)"\s+group-title="([^"]+)",(.*)[\r\n]+((https?|rtmp):\/\/.*)[\r\n]+')

    name_replacements = {
        # tv.m3u 替换
        "CCTV5P": "CCTV5+",
        "CGTNEN": "CGTN",
        "CGTN-记录": "CGTN纪录",
        "CGTNDOC": "CGTN纪录",
        "CGTNRU": "CGTN俄语",
        "CGTNFR": "CGTN法语",
        "CGTNSP": "CGTN西语",
        "CGTNAR": "CGTN阿语",
        "上海东方卫视": "东方卫视",
        "凤凰卫视中文": "凤凰卫视中文台",
        "凤凰卫视资讯": "凤凰卫视资讯台",
        "凤凰卫视香港": "凤凰卫视香港台",
        "NEWTV炫舞未来": "NewTV炫舞未来",
        "咪咕视频_8M1080_": "",
        # tptv.m3u 替换
        "CCTV5PLUS": "CCTV5+",
        # migu.m3u 替换
        "CCTV9DOCUMENTARY": "CGTN纪录",
        "CCTV俄语": "CGTN俄语",
        "CCTV法语": "CGTN法语",
        "CCTV西班牙语": "CGTN西语",
        "CCTV阿拉伯语": "CGTN阿语",

        # 自定义
        "北京纪实": "BTV",
        "北京卡酷少儿": "卡酷动画",
        "海南卫视": "旅游卫视",

        # 其他
        "_": "-",
    }
    # 解析M3U文件内容
    search_results = pattern.findall(m3u_content)
    if not search_results:
        print("未找到任何匹配的内容")
        return m3u_content

    # 生成新的M3U文件内容
    formated_m3u_entries = []
    for search_result in search_results:
        inf, tvg_id, tvg_name, tvg_logo, group_title, desc, tvg_url, protocol = search_result
        tvg_name = tvg_name.upper()
        desc = desc.upper()
        for old_name, new_name in name_replacements.items():
            tvg_name = tvg_name.replace(old_name, new_name)
            desc = desc.replace(old_name, new_name)
        if tvg_name in tvg_map:
            tvg_id = tvg_map[tvg_name]
        elif desc in tvg_map:
            tvg_id = tvg_map[desc]
        else:
            tvg_id = tvg_map.get("noepg", "9999")
            # print(f"找不到对应的 tvg-name: {tvg_name}, desc: {desc}, 使用默认 tvg-id: {tvg_id}")

        # for formated_m3u_entry in formated_m3u_entries:
        #     if f'tvg-name="{desc}"' in formated_m3u_entry:
        #         print(f"重复的 tvg-name: {desc}, 跳过")

        formated_m3u_entries.append(f'#EXTINF:{inf},tvg-id="{tvg_id}" tvg-name="{desc}" tvg-logo="{tvg_logo}" group-title="{group_title}","{desc}"\n{tvg_url}\n')

    return "".join(formated_m3u_entries)


if __name__ == "__main__":
    # 启动定时任务
    schedule_update_cached_file()
    app.run(port=35456)
    # app.run(debug=True)
