import datetime
import os
import re
import sys

import piexif

# pip install piexif


def get_exif(filename, ifd_tuple: tuple = ("0th", "Exif", "GPS", "1st")):
    assert isinstance(ifd_tuple, tuple)
    exif_dict = piexif.load(filename)
    for ifd in ifd_tuple:
        for tag in exif_dict[ifd]:
            print(piexif.TAGS[ifd][tag]["name"], exif_dict[ifd][tag])


def get_date_time_from_filename(filename):
    date = re.match(re.compile(r'.*?_(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2}).*'), os.path.basename(filename))
    if date and (len(date.groups()) == 6):
        try:
            date_time = datetime.datetime(int(date.group(1)), int(date.group(2)), int(date.group(3)), int(date.group(4)), int(date.group(5)), int(date.group(6)))
        except Exception as e:
            print(sys._getframe().f_code.co_name + ": " + str(e))
            return None
        utc_date_time = date_time + datetime.timedelta(hours=-8)
        return (date_time, utc_date_time)
    return None


def get_gps_ifd(filename):
    exif_dict = piexif.load(filename)
    return exif_dict["GPS"]


def copy_gps_exif(src, dst):
    original_ifd = piexif.load(dst)
    original_ifd["GPS"] = get_gps_ifd(src)
    original_ifd["Exif"].pop(piexif.ExifIFD.SceneType) if piexif.ExifIFD.SceneType in original_ifd["Exif"] else None
    piexif.insert(piexif.dump(original_ifd), dst)


def d2dms(d):
    mnt, sec = divmod(d * 3600, 60)
    deg, mnt = divmod(mnt, 60)
    return deg, mnt, sec


def set_gps_exif(filename, latitude: tuple, longitude: tuple, date_time: datetime.datetime = None):
    """
    r"IMG_20181029_225228.jpg", ("N", 30.60903033714247), ("E", 103.78470976163908), datetime.datetime(2018, 10, 29, 22, 52, 28)
    """
    assert isinstance(latitude, tuple) and isinstance(longitude, tuple)
    assert latitude[0] in ("N", "S")
    assert longitude[0] in ("E", "W")
    assert 0 <= latitude[1] <= 90
    assert 0 <= longitude[1] <= 180

    latitude = (latitude[0], d2dms(latitude[1]))
    longitude = (longitude[0], d2dms(longitude[1]))

    if date_time is None:
        date_time = get_date_time_from_filename(filename)[0]

    utc_date_time = date_time + datetime.timedelta(hours=-8)

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
    original_ifd = piexif.load(filename)
    original_ifd["GPS"] = gps_ifd
    piexif.insert(piexif.dump(original_ifd), filename)
    get_exif(filename, ("GPS",))


if __name__ == "__main__":
    set_gps_exif(r"IMG_20181029_225228.jpg", ("N", 30.60903033714247), ("E", 103.78470976163908), datetime.datetime(2018, 10, 29, 22, 52, 28))
    # get_exif(r"IMG_20181029_225228.jpg")
    # print(get_date_time_from_filename(r"IMG_20181029_225228.jpg"))
