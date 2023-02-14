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
        print("=============================================================={}==============================================================".format(ifd))
        print(exif_dict[ifd])
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


def copy_exif(src, dst, ifd_tuple: tuple = ("0th", "Exif", "GPS", "1st")):
    original_ifd = piexif.load(dst)
    for ifd in ifd_tuple:
        original_ifd[ifd] = piexif.load(src)[ifd]
    original_ifd["Exif"].pop(piexif.ExifIFD.SceneType) if piexif.ExifIFD.SceneType in original_ifd["Exif"] else None
    piexif.insert(piexif.dump(original_ifd), dst)


def get_lat_lon(filename):
    exif_dict = piexif.load(filename)
    if exif_dict["GPS"]:
        latref = exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef].decode("utf-8")
        lat = exif_dict["GPS"][piexif.GPSIFD.GPSLatitude]
        lonref = exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef].decode("utf-8")
        lon = exif_dict["GPS"][piexif.GPSIFD.GPSLongitude]
        lat = dms2d(lat[0][0] / lat[0][1], lat[1][0] / lat[1][1], lat[2][0] / lat[2][1])
        lon = dms2d(lon[0][0] / lon[0][1], lon[1][0] / lon[1][1], lon[2][0] / lon[2][1])
    return (latref, lat), (lonref, lon)


def d2dms(d):
    mnt, sec = divmod(d * 3600, 60)
    deg, mnt = divmod(mnt, 60)
    return deg, mnt, sec


def dms2d(deg, mnt, sec):
    return deg + mnt / 60 + sec / 3600


def set_Exif_exif(filename, date_time: datetime.datetime = None):
    if date_time is None:
        date_time = get_date_time_from_filename(filename)[0]
    exif_ifd = {
        piexif.ExifIFD.OffsetTime: b"+08:00",
        piexif.ExifIFD.OffsetTimeOriginal: b"+08:00",
        piexif.ExifIFD.DateTimeOriginal: date_time.strftime("%Y:%m:%d %H:%M:%S"),
        piexif.ExifIFD.DateTimeDigitized: date_time.strftime("%Y:%m:%d %H:%M:%S"),
    }
    original_ifd = piexif.load(filename)
    original_ifd["Exif"].update(exif_ifd)
    piexif.insert(piexif.dump(original_ifd), filename)
    get_exif(filename, ("Exif",))


def set_GPS_exif(filename, latitude: tuple, longitude: tuple, date_time: datetime.datetime = None):
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
    original_ifd["GPS"].update(gps_ifd)
    piexif.insert(piexif.dump(original_ifd), filename)
    get_exif(filename, ("GPS",))


if __name__ == "__main__":
    # set_GPS_exif(r"-57f688eeb9b6b912.jpg", get_lat_lon(r"IMG_20180613_121423.jpg")[0], get_lat_lon(r"IMG_20180613_121423.jpg")[1], date_time=datetime.datetime(2018, 6, 13, 11, 14, 35))
    # set_Exif_exif(r"-1e7efef544fdd5b4.jpg", datetime.datetime(2018, 6, 13, 11, 14, 35))
    get_exif(r"-57f688eeb9b6b912.jpg")
    # print(get_date_time_from_filename(r"IMG_20181029_225228.jpg"))
