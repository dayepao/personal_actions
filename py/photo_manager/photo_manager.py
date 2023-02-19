import os

import check_photos
from utils_pm import fix_date_time_in_exif, set_date_time_in_Exif_exif, convert_to_jpg

if __name__ == "__main__":
    path = r""

    # for file in os.listdir(path):
    #     if file.lower().endswith("png"):
    #         convert_to_jpg(os.path.join(path, file))


    # for result in check_photos.check_photos(path, check_photos.GPS_exif_is_empty):
    #     print(result)

    # for result in check_photos.check_photos(path, check_photos.date_time_in_exif_is_empty):
    #     print(result)
        # set_date_time_in_Exif_exif(result)

    for root, _, files in os.walk(path):
        for file in files:
            filepath = os.path.join(root, file)
            if file.lower().endswith((".jpg", ".jpeg")):
                fix_date_time_in_exif(filepath)

    # for result in check_photos.check_photos(path, check_photos.date_time_in_filename_and_exif_is_different):
    #     print(result)
