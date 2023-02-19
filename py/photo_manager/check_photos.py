import datetime
import os

import piexif

from utils_pm import get_date_time_from_exif, get_date_time_from_filename


def GPS_exif_is_empty(filepath):
    """Check if GPS exif is empty"""
    exif_dict = piexif.load(filepath)
    if (not exif_dict["GPS"]) or (piexif.GPSIFD.GPSLatitude not in exif_dict["GPS"]) or (piexif.GPSIFD.GPSLongitude not in exif_dict["GPS"]):
        return True
    if exif_dict["GPS"][piexif.GPSIFD.GPSLatitude] == ((0, 1), (0, 1), (0, 100)) and exif_dict["GPS"][piexif.GPSIFD.GPSLongitude] == ((0, 1), (0, 1), (0, 100)):
        return True
    return False


def date_time_in_filename_and_exif_is_different(filepath):
    """Check if datetime in filename and exif is different"""
    if not (date_time := get_date_time_from_exif(filepath)):
        print("No datetime in exif: {}".format(filepath))
        return True
    date_time_from_filename = get_date_time_from_filename(filepath)
    if date_time_from_filename:
        if date_time_from_filename not in (date_time, date_time + datetime.timedelta(hours=-8)):
            return True
    return False


def date_time_in_exif_is_empty(filepath):
    """Check if datetime in exif is empty"""
    if get_date_time_from_exif(filepath):
        return False
    return True


def check_photos(directory, check_function):
    """Check photos in directory"""
    results = []
    for root, _, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            if file.lower().endswith((".jpg", ".jpeg")):
                if check_function(filepath):
                    results.append(filepath)
            elif file.lower().endswith((".mp4", ".mov")):
                pass
            else:
                print("Not a jpeg photo: {}".format(filepath))
    return results


if __name__ == "__main__":
    for result in check_photos(r"photos", date_time_in_filename_and_exif_is_different):
        print(result)
