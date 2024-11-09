from pathlib import Path


def check_subdirectory_sizes(target_directory, size_threshold_mb):
    # Convert size threshold to bytes
    size_threshold_bytes = size_threshold_mb * 1024 * 1024

    # List all subdirectories in the target directory
    for subdir in Path(target_directory).iterdir():
        if subdir.is_dir():
            total_size = 0
            # Walk through the current subdirectory to sum file sizes
            for file in subdir.rglob('*'):
                if file.is_dir():
                    continue
                total_size += file.stat().st_size
            # Check if the total size is below the threshold
            if total_size < size_threshold_bytes:
                print(f"Directory: {subdir}, Size: {total_size / (1024 * 1024):.2f} MB")
                # delete the directory
                subdir.rmdir()


# Specify the target directory and size threshold in MB
target_directory = r""  # 请替换为你的目标目录
size_threshold_mb = 3  # 设定大小阈值，单位为 MB

check_subdirectory_sizes(target_directory, size_threshold_mb)
