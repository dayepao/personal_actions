import datetime
import os
import re
import sys
from pathlib import Path

import piexif
from PIL import Image

from utils_dayepao import get_file_hash

# pip install piexif
# pip install Pillow


def print_exif(filepath, target_ifd: tuple | str = ("0th", "Exif", "GPS", "1st")):
    assert isinstance(target_ifd, (tuple, str))
    if isinstance(target_ifd, str):
        target_ifd = (target_ifd,)
    print("{} {} {}".format("="*60, filepath, "="*60))
    exif_dict = piexif.load(filepath)
    for ifd in target_ifd:
        print("{} {} {}".format("-"*60, ifd, "-"*60))
        print(exif_dict[ifd])
        for tag in exif_dict[ifd]:
            print(piexif.TAGS[ifd][tag]["name"], exif_dict[ifd][tag])


def insert_exif(exif_dict, filepath):
    if isinstance(filepath, Path):
        filepath = str(filepath)
    exif_dict["Exif"].pop(piexif.ExifIFD.SceneType) if piexif.ExifIFD.SceneType in exif_dict["Exif"] else None
    piexif.insert(piexif.dump(exif_dict), filepath)


def get_date_time_from_filename(filepath):
    re_str_list = [
        r".*?(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2}).*",  # MIUI 相机照片
        r".*?(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2}).*",  # MIUI 截图 & Google 相机照片
        r".*?_(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2})(\d{2})_.*",  # 原生 Android 截图
        r".*?(\d{4})-(\d{2})-(\d{2}) (\d{2})(\d{2})(\d{2}).*",  # Windows 电脑截图
    ]
    date_time_result = None
    for re_str in re_str_list:
        if date_time_result := re.match(re.compile(re_str), Path(filepath).name):
            break

    date_time_tuple = None
    if date_time_result:
        date_time_tuple = tuple(map(int, date_time_result.groups()))

    if date_time_tuple:
        try:
            date_time = datetime.datetime(*date_time_tuple)
        except Exception as e:
            print(sys._getframe().f_code.co_name + ": " + str(e))
            return None
        return date_time
    return None


def get_date_time_from_exif(filepath):
    """return date_time, offset_time"""
    exif_dict = piexif.load(str(filepath))
    if piexif.ExifIFD.DateTimeOriginal in exif_dict["Exif"]:
        date_time_str = exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal].decode("utf-8")
    elif piexif.ExifIFD.DateTimeDigitized in exif_dict["Exif"]:
        date_time_str = exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized].decode("utf-8")
    elif piexif.ImageIFD.DateTime in exif_dict["0th"]:
        date_time_str = exif_dict["0th"][piexif.ImageIFD.DateTime].decode("utf-8")
    else:
        return None, None
    assert isinstance(date_time_str, str)

    date_time = None
    offset_time = re.match(re.compile(r'.*?([\+\-]\d{2}:\d{2})'), date_time_str)
    if offset_time:
        offset_time = offset_time.group(1)
        date_time_str = date_time_str.replace(offset_time, "")

    try:
        date_time = datetime.datetime.strptime(date_time_str, "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass

    return date_time, offset_time


def copy_exif(src, dst, target_ifd: tuple | str = ("0th", "Exif", "GPS", "1st")):
    assert isinstance(target_ifd, (tuple, str))
    if isinstance(target_ifd, str):
        target_ifd = (target_ifd,)
    original_ifd = piexif.load(dst)
    for ifd in target_ifd:
        original_ifd[ifd] = piexif.load(src)[ifd]
    insert_exif(original_ifd, dst)


def get_lat_lon(filepath):
    exif_dict = piexif.load(filepath)
    if exif_dict["GPS"]:
        lat = exif_dict["GPS"][piexif.GPSIFD.GPSLatitude]
        lon = exif_dict["GPS"][piexif.GPSIFD.GPSLongitude]
        lat = dms2d(lat[0][0] / lat[0][1], lat[1][0] / lat[1][1], lat[2][0] / lat[2][1]) * (-1 if exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef] == b"S" else 1)
        lon = dms2d(lon[0][0] / lon[0][1], lon[1][0] / lon[1][1], lon[2][0] / lon[2][1]) * (-1 if exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef] == b"W" else 1)
        return lat, lon
    return None, None


def d2dms(d):
    mnt, sec = divmod(d * 3600, 60)
    deg, mnt = divmod(mnt, 60)
    return deg, mnt, sec


def dms2d(deg, mnt, sec):
    return deg + mnt / 60 + sec / 3600


def set_date_time_in_Exif_exif(filepath, date_time: datetime.datetime = None, offset_time: str = "+08:00", visible: bool = True):
    if date_time is None:
        date_time = get_date_time_from_filename(filepath)

    if date_time is None:
        print("date_time is None: {}".format(filepath))
        return False

    exif_ifd = {
        piexif.ExifIFD.OffsetTime: offset_time,
        piexif.ExifIFD.OffsetTimeOriginal: offset_time,
        piexif.ExifIFD.DateTimeOriginal: date_time.strftime("%Y:%m:%d %H:%M:%S{}".format(offset_time)),
        piexif.ExifIFD.DateTimeDigitized: date_time.strftime("%Y:%m:%d %H:%M:%S{}".format(offset_time)),
    }
    original_ifd = piexif.load(filepath)
    original_ifd["Exif"].update(exif_ifd)
    insert_exif(original_ifd, filepath)
    if visible:
        print_exif(filepath, "Exif")
    return True


def set_GPS_exif(filepath, latitude: float | int, longitude: float | int, date_time: datetime.datetime = None, offset_time: str = None, visible: bool = True):
    """
    r"IMG_20181029_225228.jpg", 30.60903033714247, 103.78470976163908, datetime.datetime(2018, 10, 29, 22, 52, 28)
    """
    assert isinstance(latitude, (float, int)) and isinstance(longitude, (float, int))
    assert -90 <= latitude <= 90 and -180 <= longitude <= 180

    latitude = ("S" if latitude < 0 else "N", d2dms(abs(latitude)))
    longitude = ("W" if longitude < 0 else "E", d2dms(abs(longitude)))

    exif_date_time, exif_offset_time = get_date_time_from_exif(filepath)

    date_time = date_time or exif_date_time
    offset_time = offset_time or exif_offset_time

    if not date_time:
        print("date_time is None: {}".format(filepath))
        return False

    if not offset_time:
        print("offset_time is None: {}".format(filepath))
        return False

    offset_time_int = int(re.match(re.compile(r'([\+\-]\d{2})'), offset_time).group(1))

    utc_date_time = date_time + datetime.timedelta(hours=-offset_time_int)

    gps_ifd = {
        piexif.GPSIFD.GPSLatitudeRef: latitude[0],
        piexif.GPSIFD.GPSLatitude: ((int(round(latitude[1][0])), 1), (int(round(latitude[1][1])), 1), (int(round(latitude[1][2] * 100)), 100)),
        piexif.GPSIFD.GPSLongitudeRef: longitude[0],
        piexif.GPSIFD.GPSLongitude: ((int(round(longitude[1][0])), 1), (int(round(longitude[1][1])), 1), (int(round(longitude[1][2] * 100)), 100)),
        piexif.GPSIFD.GPSAltitudeRef: 0,
        piexif.GPSIFD.GPSAltitude: (0, 1000),
        piexif.GPSIFD.GPSTimeStamp: ((utc_date_time.hour, 1), (utc_date_time.minute, 1), (utc_date_time.second, 1)),
        piexif.GPSIFD.GPSProcessingMethod: b'ASCII\x00\x00\x00CELLID\x00',
        piexif.GPSIFD.GPSDateStamp: '{}:{}:{}'.format(str(utc_date_time.year).zfill(4), str(utc_date_time.month).zfill(2), str(utc_date_time.day).zfill(2))
    }
    original_ifd = piexif.load(filepath)
    original_ifd["GPS"].update(gps_ifd)
    insert_exif(original_ifd, filepath)
    if visible:
        print_exif(filepath, "GPS")
    return True


def fix_date_time_in_exif(filepath, offset_time: str = "+08:00"):
    date_time, original_offset_time = get_date_time_from_exif(filepath)
    if date_time:
        if original_offset_time:
            return bool(original_offset_time == offset_time)
        return set_date_time_in_Exif_exif(filepath, date_time, offset_time=offset_time, visible=False)
    return False


def remove_duplicate_files(path):
    """文件夹去重"""
    files = os.listdir(path)
    files.sort()
    hash_list = []
    for file in files:
        if get_file_hash(Path(path, file)) in hash_list:
            print("重复文件：", Path(path, file))
            # os.remove(Path(path, file))
        else:
            hash_list.append(get_file_hash(Path(path, file)))


def convert_to_jpg(filepath):
    """将图片转为jpg格式"""
    filepath = Path(filepath)
    if filepath.suffix.lower() in [".png", ]:
        new_filepath = filepath.with_suffix(".jpg")
        print(f"转换文件：{filepath} -> {new_filepath}")
        with Image.open(filepath) as img:
            img.convert("RGB").save(new_filepath, "JPEG")
        if new_filepath.exists() and new_filepath.stat().st_size > 0:
            os.remove(filepath)
            return True
    return False


def rotate_to_normal(filepath):
    """将图片旋转为正确的方向"""
    filepath = Path(filepath)
    exif_dict = piexif.load(str(filepath))
    if filepath.suffix.lower() in [".jpg", ".jpeg"]:
        assert isinstance(exif_dict["0th"], dict)
        if (orientation := exif_dict["0th"].get(piexif.ImageIFD.Orientation)) and (orientation != 1):
            print(f"旋转文件：{filepath}")
            with Image.open(filepath) as img:
                if orientation == 3:
                    img = img.rotate(180, expand=True)
                elif orientation == 6:
                    img = img.rotate(270, expand=True)
                elif orientation == 8:
                    img = img.rotate(90, expand=True)
                else:
                    return False
                img.save(filepath, quality=95)
                exif_dict["0th"].update({piexif.ImageIFD.ImageWidth: img.width, piexif.ImageIFD.ImageLength: img.height, piexif.ImageIFD.Orientation: 1})
                exif_dict["Exif"].update({piexif.ExifIFD.PixelXDimension: img.width, piexif.ExifIFD.PixelYDimension: img.height})
                exif_dict["1st"].update({piexif.ImageIFD.Orientation: 1})
                insert_exif(exif_dict, filepath)
        return True
    return False


def rotate_to_angle(filepath, angle):
    """将图片逆时针旋转指定角度"""
    filepath = Path(filepath)
    exif_dict = piexif.load(str(filepath))
    if filepath.suffix.lower() in [".jpg", ".jpeg"]:
        print(f"旋转文件：{filepath}")
        with Image.open(filepath) as img:
            img = img.rotate(angle, expand=True)
            img.save(filepath, quality=95)
            exif_dict["0th"].update({piexif.ImageIFD.ImageWidth: img.width, piexif.ImageIFD.ImageLength: img.height, piexif.ImageIFD.Orientation: 1})
            exif_dict["Exif"].update({piexif.ExifIFD.PixelXDimension: img.width, piexif.ExifIFD.PixelYDimension: img.height})
            exif_dict["1st"].update({piexif.ImageIFD.Orientation: 1})
            insert_exif(exif_dict, filepath)
        return True
    return False


if __name__ == "__main__":
    # path = r"新建文件夹"
    # remove_duplicate_files(path)
    # for file in os.listdir(path):
    #     if file.endswith(".jpg"):
    #         set_date_time_in_Exif_exif(Path(path, file))
    #         convert_to_jpg(Path(path, file))
    # print(get_date_time_from_filename(r"20230206_094257_E0036B09.jpg"))
    # piexif.remove(r"2023-03-13-19-51-02-327.jpg")
    # print_exif(r"20230202_092530_8E369BFD.jpg")
    # print(get_lat_lon(r"2023-03-12-18-07-29-004.jpg"))
    # set_GPS_exif(r"\IMG_20220105_144149.jpg", *get_lat_lon(r"\IMG_20220105_144201.jpg"))
    # set_GPS_exif(r"IMG_20230209_190032.jpg", 30.550508617348928, 103.98844232553355)
    # print(get_date_time_from_exif(r"IMG_20180615_161812.jpg"))
    # set_date_time_in_Exif_exif(r"mmexport1674378903865.jpg", datetime.datetime(2023, 1, 21, 15, 33, 0))
    # rotate_to_normal(r"2023-03-18-18-33-21-708.jpg")
    # rotate_to_angle(r"20230318_103322_B5664745.jpg", 90)
    pass
