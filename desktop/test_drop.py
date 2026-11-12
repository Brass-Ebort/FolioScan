"""Pruebas de eventos de arrastre reales, importación de páginas y rechazo seguro."""

import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from PySide6.QtCore import Qt, QMimeData, QUrl, QPoint, QPointF
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtTest import QTest
from v3 import WindowV3
from drop_files import local_paths
import core


class DropTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def drop(self, widget, paths):
        mime = QMimeData()
        mime.setUrls([QUrl.fromLocalFile(str(p)) for p in paths])
        enter = QDragEnterEvent(
            QPoint(8, 8), Qt.CopyAction, mime, Qt.LeftButton, Qt.NoModifier
        )
        self.app.sendEvent(widget, enter)
        if not enter.isAccepted():
            return False
        event = QDropEvent(
            QPointF(8, 8), Qt.CopyAction, mime, Qt.LeftButton, Qt.NoModifier
        )
        self.app.sendEvent(widget, event)
        return event.isAccepted()

    def test_drop_on_scanner_and_tools(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            photo = root / "foto á.png"
            Image.new("RGB", (160, 240), "blue").save(photo)
            pdf = root / "two pages.pdf"
            core.images_to_pdf([photo, photo], pdf)
            window = WindowV3(data_root=root / "data")
            window.show()
            self.app.processEvents()
            with patch.object(QMessageBox, "warning") as warning:
                self.assertTrue(self.drop(window.scan_files.viewport(), [photo, pdf]))
                limit = time.monotonic() + 15
                while window.scan_files.count() != 3 and time.monotonic() < limit:
                    QTest.qWait(10)
                warning.assert_not_called()
                self.assertEqual(window.scan_files.count(), 3)
            self.assertEqual(len(list((root / "data/Sesion").glob("*.jpg"))), 3)
            window.tabs.setCurrentIndex(1)
            self.app.processEvents()
            self.assertTrue(self.drop(window.tool_files.viewport(), [pdf, pdf]))
            self.assertEqual(window.tool_files.count(), 2)
            window.operation.setCurrentIndex(1)
            self.assertFalse(self.drop(window.tool_files.viewport(), [pdf, pdf]))
            self.assertTrue(self.drop(window.tool_files.viewport(), [pdf]))
            self.assertEqual(window.tool_files.count(), 1)
            window.operation.setCurrentIndex(3)
            self.assertFalse(self.drop(window.tool_files.viewport(), [pdf]))
            self.assertTrue(self.drop(window.tabs.widget(1), [photo]))
            self.assertEqual(window.tool_files.count(), 1)
            window.close()

    def test_import_failure_rolls_back_and_preserves_original(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            session = root / "session"
            session.mkdir()
            image = root / "image.png"
            Image.new("RGB", (50, 70), "red").save(image)
            before = image.read_bytes()
            bad = root / "bad.pdf"
            bad.write_bytes(b"broken")
            with self.assertRaises(Exception):
                core.import_scan_files([image, bad], session)
            self.assertEqual(list(session.iterdir()), [])
            self.assertEqual(image.read_bytes(), before)

    def test_remote_and_directory_urls_are_rejected(self):
        mime = QMimeData()
        mime.setUrls([QUrl("https://example.com/document.pdf")])
        self.assertEqual(local_paths(mime), [])
        with tempfile.TemporaryDirectory() as folder:
            mime.setUrls([QUrl.fromLocalFile(folder)])
            self.assertEqual(local_paths(mime), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
