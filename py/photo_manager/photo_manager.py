import os
import sys
from pathlib import Path

import check_photos
from utils_pm import (convert_to_jpg, fix_date_time_in_exif,
                      set_date_time_in_Exif_exif)

if __name__ == "__main__":
    path = r""

    # 将所有png文件转换为jpg文件
    print("="*60, "将所有png文件转换为jpg文件", "="*60)
    for file in os.listdir(path):
        if file.lower().endswith("png"):
            if not convert_to_jpg(Path(path, file)):
                print("无法转换文件: {}".format(file))
                sys.exit(1)

    # 通过文件名修复文件的日期时间信息
    print("="*60, "通过文件名修复文件的日期时间信息", "="*60)
    empty_date_time_in_exif = []
    for result in check_photos.check_photos(path, check_photos.date_time_in_exif_is_empty):
        if not set_date_time_in_Exif_exif(result):
            empty_date_time_in_exif.append(result)
    if empty_date_time_in_exif:
        print("无法修复以下文件的日期时间信息: ")
        for result in empty_date_time_in_exif:
            print(result)
        sys.exit(1)

    # 检查所有文件的GPS信息
    print("="*60, "检查所有文件的GPS信息", "="*60)
    if empty_GPS_exif := check_photos.check_photos(path, check_photos.GPS_exif_is_empty):
        print("以下文件的GPS信息为空: ")
        for result in empty_GPS_exif:
            print(result)
        if input("是否继续? (y/N)") not in ("y", "Y"):
            sys.exit(1)

    # 修复所有文件的时区信息
    print("="*60, "修复所有文件的时区信息", "="*60)
    unalbe_to_fix_date_time_in_exif = []
    for root, _, files in os.walk(path):
        for file in files:
            filepath = str(Path(root, file))
            if file.lower().endswith((".jpg", ".jpeg")):
                if not fix_date_time_in_exif(filepath):
                    unalbe_to_fix_date_time_in_exif.append(filepath)
    if unalbe_to_fix_date_time_in_exif:
        print("以下文件的时区信息无法修复: ")
        for result in unalbe_to_fix_date_time_in_exif:
            print(result)
        sys.exit(1)

    # for result in check_photos.check_photos(path, check_photos.date_time_in_filename_and_exif_is_different):
    #     print(result)
