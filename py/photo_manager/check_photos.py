import datetime
import os

import piexif

from utils_pm import get_date_time_from_exif, get_date_time_from_filename


def GPS_exif_is_empty(filename):
    """Check if GPS exif is empty"""
    exif_dict = piexif.load(filename)
    if (not exif_dict["GPS"]) or (piexif.GPSIFD.GPSLatitude not in exif_dict["GPS"]) or (piexif.GPSIFD.GPSLongitude not in exif_dict["GPS"]):
        return True
    if exif_dict["GPS"][piexif.GPSIFD.GPSLatitude] == ((0, 1), (0, 1), (0, 100)) and exif_dict["GPS"][piexif.GPSIFD.GPSLongitude] == ((0, 1), (0, 1), (0, 100)):
        return True
    return False


def date_time_in_filename_and_exif_is_different(filename):
    """Check if datetime in filename and exif is different"""
    if not (date_time := get_date_time_from_exif(filename)):
        print("No datetime in exif: {}".format(filename))
        return False
    date_time = datetime.datetime.strptime(date_time.decode("utf-8"), "%Y:%m:%d %H:%M:%S")
    date_time_from_filename = get_date_time_from_filename(filename)
    if date_time_from_filename:
        if date_time_from_filename + datetime.timedelta(hours=8) != date_time:
            return True
    return False


def date_time_in_exif_is_empty(filename):
    """Check if datetime in exif is empty"""
    if get_date_time_from_exif(filename):
        return False
    return True


def check_photos(directory, check_function):
    """Check photos in directory"""
    results = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith((".jpg", ".jpeg")):
                filename = os.path.join(root, file)
                if check_function(filename):
                    results.append(filename)
    return results


if __name__ == "__main__":
    for result in check_photos(r"Camera", date_time_in_exif_is_empty):
        print(result)
