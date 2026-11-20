"""Allow compatible LGPL library replacements before Qt is imported.

Normal execution needs only the EXE. Advanced users can supply an optional
Bibliotecas folder beside it, with PySide6/shiboken6 subdirectories. In onefile
mode, replacements are copied into this run's private extraction directory.
No system installation, network download or runtime dependency is required.
"""
import sys
import shutil
from pathlib import Path

if getattr(sys, 'frozen', False):
    override = Path(sys.executable).parent / 'Bibliotecas'
    for component in ('PySide6', 'shiboken6'):
        source = override / component
        if source.is_dir():
            shutil.copytree(source, Path(sys._MEIPASS) / component, dirs_exist_ok=True)
