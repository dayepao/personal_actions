import sys
from pathlib import Path

import check_photos
from utils_pm import convert_to_jpg, fix_date_time_in_exif, rotate_to_normal, set_date_time_in_Exif_exif

if __name__ == "__main__":
    target_path = Path(r"")

    # 删除所有Thumbs.db文件
    print("="*60, "删除所有Thumbs.db文件", "="*60)
    for file in target_path.rglob("Thumbs.db"):
        file.unlink()

    # 将所有png文件转换为jpg文件
    print("="*60, "将所有png文件转换为jpg文件", "="*60)
    for file in target_path.glob("*.png"):
        if not convert_to_jpg(file):
            print("无法转换文件: {}".format(file))
            sys.exit(1)

    # 将图片旋转为正确的方向
    print("="*60, "将图片旋转为正确的方向", "="*60)
    for file in target_path.iterdir():
        if file.suffix.lower() in (".jpg", ".jpeg"):
            if not rotate_to_normal(file):
                print("无法旋转文件: {}".format(file))
                sys.exit(1)

    # 通过文件名修复文件的日期时间信息
    print("="*60, "通过文件名修复文件的日期时间信息", "="*60)
    empty_date_time_in_exif = []
    for result in check_photos.check_photo(target_path, check_photos.date_time_in_exif_is_empty):
        if not set_date_time_in_Exif_exif(result):
            empty_date_time_in_exif.append(result)
    if empty_date_time_in_exif:
        print(f"无法修复以下 {len(empty_date_time_in_exif)} 个文件的日期时间信息: ")
        for result in empty_date_time_in_exif:
            print(result)
        sys.exit(1)

    # 修复所有文件的时区信息
    print("="*60, "修复所有文件的时区信息", "="*60)
    unable_to_fix_exif_date_time = []
    for file in target_path.rglob("*"):
        if file.suffix.lower() in (".jpg", ".jpeg"):
            if not fix_date_time_in_exif(file):
                unable_to_fix_exif_date_time.append(file)
    if unable_to_fix_exif_date_time:
        print(f"以下 {len(unable_to_fix_exif_date_time)} 个文件的时区信息无法修复: ")
        for result in unable_to_fix_exif_date_time:
            print(result)
        sys.exit(1)

    # 检查所有文件的GPS信息
    print("="*60, "检查所有文件的GPS信息", "="*60)
    if empty_GPS_exif := check_photos.check_photo(target_path, check_photos.GPS_exif_is_empty):
        print(f"以下 {len(empty_GPS_exif)} 个文件的GPS信息为空: ")
        for result in empty_GPS_exif:
            print(result)
        if input("是否继续? (y/N): ") not in ("y", "Y"):
            sys.exit(1)

    print("="*60, "检查完成", "="*60)

    # for result in check_photos.check_photos(path, check_photos.date_time_in_filename_and_exif_is_different):
    #     print(result)
