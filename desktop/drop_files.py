"""Arrastre de archivos locales; los movimientos internos de las listas siguen en Qt."""

from pathlib import Path
from PySide6.QtCore import QObject, QEvent, Qt
from PySide6.QtWidgets import QWidget

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}


def local_paths(mime):
    """No descarga enlaces ni recorre carpetas arrastradas accidentalmente."""
    if not mime.hasUrls():
        return []
    urls = mime.urls()
    if not urls or any(not url.isLocalFile() for url in urls):
        return []
    paths = [Path(url.toLocalFile()) for url in urls]
    return paths if all(path.is_file() for path in paths) else []


class FileDropFilter(QObject):
    """La página y sus hijos son una sola zona de entrada, incluida la lista vacía."""

    def __init__(self, page, accepts, receive):
        super().__init__(page)
        self.accepts, self.receive = accepts, receive
        for widget in [page] + page.findChildren(QWidget):
            widget.setAcceptDrops(True)
            widget.installEventFilter(self)

    def eventFilter(self, watched, event):
        if event.type() not in (QEvent.DragEnter, QEvent.DragMove, QEvent.Drop):
            return False
        if not event.mimeData().hasUrls():
            return False  # Qt conserva su protocolo de reordenación interna.
        paths = local_paths(event.mimeData())
        if not paths or not self.accepts(paths):
            event.ignore()
            return True
        event.setDropAction(Qt.CopyAction)
        event.accept()
        if event.type() == QEvent.Drop:
            self.receive(paths)
        return True
