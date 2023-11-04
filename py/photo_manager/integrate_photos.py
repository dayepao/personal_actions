import shutil
from pathlib import Path

from check_photos import is_screenshot


def integrate_photos(raw_path: Path, target_path: Path):
    if isinstance(raw_path, str):
        raw_path = Path(raw_path)
    if isinstance(target_path, str):
        target_path = Path(target_path)
    target_path.mkdir(parents=True, exist_ok=True)
    (target_path / "DCIM").mkdir(parents=True, exist_ok=True)
    (target_path / "Screenshots").mkdir(parents=True, exist_ok=True)
    for raw_photo in raw_path.rglob("*"):
        if raw_photo.is_file():
            if raw_photo.suffix.lower() in [".jpg", ".jpeg"]:
                if is_screenshot(str(raw_photo)):
                    shutil.copy(raw_photo, target_path / "Screenshots")
                else:
                    shutil.copy(raw_photo, target_path / "DCIM")
            elif raw_photo.suffix.lower() in [".mp4", ".mov"]:
                shutil.copy(raw_photo, target_path / "DCIM")


def total_sum(path: Path):
    if isinstance(path, str):
        path = Path(path)
    total = 0
    for file in path.rglob("*.mp4"):
        if file.is_file():
            total += 1
    return total


if __name__ == "__main__":
    integrate_photos(r".\photos\photos", r".\Desktop\photos")
