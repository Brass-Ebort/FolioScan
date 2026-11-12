"""Regression checks for V3's destructive and persistent workflows."""

import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"
import unittest
import tempfile
from pathlib import Path
from PIL import Image
from pypdf import PdfReader
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtCore import QSettings, Qt
import core
import i18n
from v3 import WindowV3
from layout_editor import LayoutEditor
from app import configure_fonts


class V3Test(unittest.TestCase):
    def test_v32_contextual_format_and_system_language(self):
        from unittest.mock import patch
        from PySide6.QtCore import QLocale, QTimer
        from PySide6.QtWidgets import QDialog
        with tempfile.TemporaryDirectory() as temp:
            with patch("v3.QLocale.system", return_value=QLocale("fr_FR")):
                window = WindowV3(data_root=Path(temp))
            self.assertEqual(i18n.language, "fr")
            window.show()
            window.tabs.setCurrentIndex(1)
            self.app.processEvents()
            self.assertTrue(window.status.isHidden())
            for index in range(4):
                window.operation.setCurrentIndex(index)
                self.assertEqual(window.pdf_format.isHidden(), index != 3)
                self.assertEqual(window.pdf_format_label.isHidden(), index != 3)
            captured = []
            def inspect_dialog():
                for widget in self.app.topLevelWidgets():
                    if isinstance(widget, QDialog) and widget.isVisible():
                        captured.extend(label.text() for label in widget.findChildren(QLabel))
                        widget.accept()
            QTimer.singleShot(50, inspect_dialog)
            window.additional_info()
            self.assertIn("FolioScan · v3.2", captured)
            window.settings.setValue("language", "es")
            window.close()
            with patch("v3.QLocale.system", return_value=QLocale("fr_FR")):
                reopened = WindowV3(data_root=Path(temp))
            self.assertEqual(i18n.language, "es")
            reopened.close()
        with tempfile.TemporaryDirectory() as temp:
            with patch("v3.QLocale.system", return_value=QLocale("de_DE")):
                fallback = WindowV3(data_root=Path(temp))
            self.assertEqual(i18n.language, "en")
            fallback.close()
        i18n.language = "es"

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setStyle("Fusion")
        configure_fonts()

    def test_append_recovers_original_and_rejects_invalid_input(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            image = root / "image.jpg"
            Image.new("RGB", (200, 300), "red").save(image)
            original = root / "original.pdf"
            addition = root / "new.pdf"
            core.images_to_pdf([image], original, "A4")
            core.images_to_pdf([image, image], addition, "A5")
            before = original.read_bytes()
            core.append_pdf(original, [addition])
            self.assertEqual((root / "original.pdf.recovery").read_bytes(), before)
            self.assertEqual(len(PdfReader(original).pages), 3)
            good = original.read_bytes()
            with self.assertRaises(Exception):
                core.append_pdf(original, [root / "missing.pdf"])
            self.assertEqual(original.read_bytes(), good)

    def test_layout_pdf_and_pixels_match_preview(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            image = root / "image.jpg"
            Image.new("RGB", (100, 100), "red").save(image)
            spec = dict(
                width=200,
                height=100,
                scale=0.5,
                x=0.25,
                y=0,
                pixelsWide=400,
                pixelsHigh=200,
            )
            self.assertEqual(core.layout_box(spec, (100, 100)), (125, 25, 50, 50))
            core.layout_pdf([image], root / "page.pdf", [spec])
            core.layout_images([image], root / "pictures", [spec], "PNG")
            page = PdfReader(root / "page.pdf").pages[0]
            self.assertEqual(list(page.mediabox), [0, 0, 200, 100])
            with Image.open(root / "pictures/Pagina-001.png") as result:
                self.assertEqual(result.size, (400, 200))
                self.assertEqual(result.getpixel((20, 20)), (255, 255, 255))
                self.assertGreater(result.getpixel((300, 100))[0], 240)
                self.assertLess(result.getpixel((300, 100))[1], 20)

    def test_window_layout_languages_and_portable_persistence(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            window = WindowV3(data_root=root)
            window.show()
            self.app.processEvents()
            self.assertIs(window.tabs.cornerWidget(Qt.TopRightCorner), window.gear)
            self.assertEqual(window.library_tabs.count(), 2)
            image = root / "Sesion/test.jpg"
            Image.new("RGB", (400, 600), "#ebe2b9").save(image)
            window.add_item(window.scan_files, image)
            window.scan_files.setCurrentRow(0)
            window.persist_session()
            self.app.processEvents()
            i18n.apply(window)
            self.assertFalse(window.preview.pixmap().isNull())
            qa = Path(__file__).parent / "qa"
            qa.mkdir(exist_ok=True)
            window.grab().save(str(qa / "v3-claro.png"))
            window.toggle_theme()
            window.grab().save(str(qa / "v3-oscuro.png"))
            for code in i18n.CODES:
                i18n.language = code
                i18n.apply(window)
                self.assertEqual(
                    window.tabs.tabText(1), i18n.ROWS["Gestor de PDF"][code]
                )
            window.settings.setValue("language", "fr")
            window.close()
            reopened = WindowV3(data_root=root)
            self.assertEqual(reopened.scan_files.count(), 1)
            self.assertTrue(reopened.settings.value("dark", False, type=bool))
            self.assertEqual(i18n.language, "fr")
            reopened.close()
            i18n.language = "es"

    def test_editor_navigation_preserves_geometry(self):
        with tempfile.TemporaryDirectory() as temp:
            image = Path(temp) / "a.jpg"
            Image.new("RGB", (200, 300), "white").save(image)
            editor = LayoutEditor([str(image), str(image)], None)
            editor.show()
            self.app.processEvents()
            editor.controls["scale"].setValue(75)
            editor.controls["x"].setValue(20)
            editor.change(1)
            editor.change(-1)
            self.assertAlmostEqual(editor.specs[0]["scale"], 0.75)
            self.assertAlmostEqual(editor.specs[0]["x"], 0.2)
            editor.output.setCurrentText("PNG")
            editor.pw.setValue(800)
            editor.ph.setValue(400)
            self.assertAlmostEqual(
                editor.specs[0]["width"] / editor.specs[0]["height"], 2
            )
            editor.grab().save(str(Path(__file__).parent / "qa/v3-editor.png"))
            editor.close()

    def test_discovery_and_catalogue(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "a.PDF").touch()
            (root / ".hidden").mkdir()
            (root / ".hidden/x.pdf").touch()
            self.assertEqual(core.discover_pdfs([root]), [str(root / "a.PDF")])
        for key, row in i18n.ROWS.items():
            self.assertEqual(set(row), set(i18n.CODES), key)
            self.assertTrue(all(row.values()), key)


if __name__ == "__main__":
    unittest.main(verbosity=2)
