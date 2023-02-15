import os

import piexif
import datetime
from utils_pm import get_date_time_from_filename


def GPS_exif_is_empty(filename):
    """Check if GPS exif is empty"""
    exif_dict = piexif.load(filename)
    if (not exif_dict["GPS"]) or (not exif_dict["GPS"][piexif.GPSIFD.GPSLatitude]) or (not exif_dict["GPS"][piexif.GPSIFD.GPSLongitude]):
        return True
    if exif_dict["GPS"][piexif.GPSIFD.GPSLatitude] == (0, 0, 0) and exif_dict["GPS"][piexif.GPSIFD.GPSLongitude] == (0, 0, 0):
        return True
    return False


def datetime_in_filename_and_exif_is_different(filename):
    """Check if datetime in filename and exif is different"""
    exif_dict = piexif.load(filename)
    if piexif.ExifIFD.DateTimeOriginal in exif_dict["Exif"]:
        date_time = exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal]
    elif piexif.ImageIFD.DateTime in exif_dict["0th"]:
        date_time = exif_dict["0th"][piexif.ImageIFD.DateTime]
    else:
        print("No datetime in exif: {}".format(filename))
        return False
    date_time = datetime.datetime.strptime(date_time.decode("utf-8"), "%Y:%m:%d %H:%M:%S")
    date_time_from_filename = get_date_time_from_filename(filename)
    if date_time_from_filename:
        if date_time_from_filename + datetime.timedelta(hours=8) != date_time:
            return True
    return False


def check_photos(directory, check_function):
    """Check photos in directory"""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith((".jpg", ".jpeg")):
                filename = os.path.join(root, file)
                if check_function(filename):
                    print(filename)


if __name__ == "__main__":
    check_photos(r"photos", datetime_in_filename_and_exif_is_different)
