import piexif
from PIL import Image

# pip install piexif
# pip install pillow


def get_exif(filename):
    exif_dict = piexif.load(filename)
    for ifd in ("0th", "Exif", "GPS", "1st"):
        for tag in exif_dict[ifd]:
            print(piexif.TAGS[ifd][tag]["name"], exif_dict[ifd][tag])


def get_gps_ifd(filename):
    exif_dict = piexif.load(filename)
    print(exif_dict["GPS"])
    return exif_dict["GPS"]


def copy_gps_exif(src, dst):
    original_ifd = piexif.load(dst)
    original_ifd["GPS"] = get_gps_ifd(src)
    original_ifd["Exif"].pop(piexif.ExifIFD.SceneType) if piexif.ExifIFD.SceneType in original_ifd["Exif"] else None
    piexif.insert(piexif.dump(original_ifd), dst)


def set_gps_exif(filename):
    gps_ifd = {piexif.GPSIFD.GPSLatitudeRef: b'N',
               piexif.GPSIFD.GPSLatitude: ((38, 1), (26, 1), (883, 100)),
               piexif.GPSIFD.GPSLongitudeRef: b'E',
               piexif.GPSIFD.GPSLongitude: ((116, 1), (6, 1), (3918, 100)),
               piexif.GPSIFD.GPSAltitudeRef: 0,
               piexif.GPSIFD.GPSAltitude: (0, 1000),
               piexif.GPSIFD.GPSTimeStamp: ((2, 1), (40, 1), (19, 1)),
               piexif.GPSIFD.GPSProcessingMethod: b'ASCII\x00\x00\x00CELLID\x00',
               piexif.GPSIFD.GPSDateStamp: b'2022:07:04'}
    original_ifd = piexif.load(filename)
    original_ifd["GPS"] = gps_ifd
    piexif.insert(piexif.dump(original_ifd), filename)


if __name__ == "__main__":
    set_gps_exif(r"IMG_20220704_103712.jpg")
