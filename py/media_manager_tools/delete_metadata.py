import sys
from pathlib import Path

path = r""

if input(f"Delete all metadata files in {path}? (y/n) ").lower() != "y":
    sys.exit()

include_extensions = (".nfo", ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg", ".txt", "bif")

for file in Path(path).rglob("*"):
    if file.is_file() and str(file).endswith(include_extensions):
        file.unlink()
        print(f"Deleted: {file}")
    if file.is_dir() and file.name == "metadata":
        file.rmdir()
        print(f"Deleted: {file}")
