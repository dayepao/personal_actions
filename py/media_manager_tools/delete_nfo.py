import os
import sys
from pathlib import Path

path = r""

if input(f"Delete all .nfo, .jpg, .png, .txt, .svg files in {path}? (y/n) ").lower() != "y":
    sys.exit()

for root, dirs, files in os.walk(path):
    for file in files:
        if file.endswith((".nfo", ".jpg", ".png", ".txt", ".svg")):
            os.remove(Path(root, file))
            print(f"Deleted: {Path(root, file)}")
