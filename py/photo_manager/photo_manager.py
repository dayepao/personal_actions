from utils_pm import set_date_time_in_Exif_exif
import check_photos

if __name__ == "__main__":
    for result in check_photos.check_photos(r"Camera", check_photos.date_time_in_exif_is_empty):
        set_date_time_in_Exif_exif(result)