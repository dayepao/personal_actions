import datetime
from pathlib import Path

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
    if get_date_time_from_exif(filepath)[0]:
        return False
    return True


def is_screenshot(filepath):
    """Check if it is a screenshot"""
    exif_dict = piexif.load(filepath)
    keys_0th = [piexif.ImageIFD.Make, piexif.ImageIFD.Model]
    keys_exif = [piexif.ExifIFD.Flash, piexif.ExifIFD.FlashpixVersion, piexif.ExifIFD.ColorSpace]
    if (not exif_dict["0th"]) or (all(key not in exif_dict["0th"] for key in keys_0th) and all(key not in exif_dict["Exif"] for key in keys_exif) and GPS_exif_is_empty(filepath)):
        return True
    return False


def check_photo(directory, check_function):
    """Check photos in directory"""
    if isinstance(directory, str):
        directory = Path(directory)
    results = []
    for file in directory.rglob("*"):
        if file.is_file():
            if file.suffix.lower() in (".jpg", ".jpeg"):
                if check_function(str(file)):
                    results.append(str(file))
            elif file.suffix.lower() in (".mp4", ".mov"):
                pass
            else:
                print(f"Not a supported file: {file}")
    return results


if __name__ == "__main__":
    for result in check_photo(r"photos", date_time_in_filename_and_exif_is_different):
        print(result)
