import zipfile
from pathlib import Path


def pack_pdf_files(folder_path: Path, zip_file_name: str = "pdf_files.zip"):
    if isinstance(folder_path, str):
        folder_path = Path(folder_path)
    zip_file_name = Path(__file__).parent / zip_file_name
    if zip_file_name.exists():
        print(f"{zip_file_name} already exists.")
        return
    with zipfile.ZipFile(zip_file_name, "w") as zip_file:
        for file in folder_path.rglob("*.pdf"):
            zip_file.write(file, file.name)


folder_path = r".\files"
pack_pdf_files(folder_path)
