import xml.etree.ElementTree as ET

from cache_config import CACHE_FILE_CONFIGS


def generate_tvg_map():
    """根据 EPG XML 文件, 生成节目单映射表"""
    # 读取 EPG XML 文件
    epg_xml_file = CACHE_FILE_CONFIGS["epg.xml"]["CACHE_PATH"].joinpath("epg.xml")
    tree = ET.parse(epg_xml_file)
    root = tree.getroot()
    tvg_map = {}
    for channel in root.findall("channel"):
        tvg_id = channel.attrib["id"]
        tvg_name = channel.find("display-name").text
        if tvg_name in tvg_map:
            print(f"重复的 tvg-name: {tvg_name}, 跳过")
            continue
        tvg_map[tvg_name.upper()] = tvg_id
    return tvg_map


if __name__ == "__main__":
    tvg_map = generate_tvg_map()
    print(tvg_map)
