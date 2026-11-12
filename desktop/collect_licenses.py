import importlib.metadata as metadata
import shutil
from pathlib import Path

root = Path(__file__).parent / "licenses"
for name in [
    "PySide6-Essentials",
    "shiboken6",
    "pypdf",
    "pypdfium2",
    "Pillow",
    "reportlab",
    "opencv-python-headless",
    "numpy",
    "pyinstaller",
    "charset-normalizer",
    "altgraph",
    "packaging",
    "pefile",
    "pywin32-ctypes",
    "setuptools",
]:
    distribution = metadata.distribution(name)
    destination = root / name
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "METADATA.txt").write_text(
        distribution.read_text("METADATA") or "", encoding="utf-8"
    )
    for entry in distribution.files or []:
        lower = str(entry).lower()
        if any(
            token in lower for token in ("license", "copying", "notice", "copyright")
        ):
            source = Path(distribution.locate_file(entry))
            if source.is_file() and source.suffix.lower() not in (
                ".pyc",
                ".pyd",
                ".dll",
            ):
                target = destination / str(entry).replace("..", "_")
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)

# The frozen interpreter also carries Python's own license, outside site-packages.
import sys
python_license=Path(sys.base_prefix)/'LICENSE.txt'
if python_license.is_file():shutil.copyfile(python_license,root/'Python-LICENSE.txt')
