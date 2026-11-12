import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"
import unittest
import tempfile
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings
from app import Window, configure_fonts


class UiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setStyle("Fusion")
        configure_fonts()

    def test_theme_order_and_all_tools(self):
        with tempfile.TemporaryDirectory() as temp:
            settings = QSettings(str(Path(temp) / "prefs.ini"), QSettings.IniFormat)
            window = Window(settings)
            window.show()
            self.app.processEvents()
            window.add_item(
                window.scan_files,
                str(Path(__file__).parent / "qa" / "foto.png"),
                "Hoja de prueba",
            )
            window.scan_files.setCurrentRow(0)
            self.app.processEvents()
            window.grab().save(
                str(Path(__file__).parent / "qa" / "escritorio-claro.png")
            )
            window.toggle_theme()
            self.app.processEvents()
            self.assertTrue(settings.value("dark", False, type=bool))
            window.grab().save(
                str(Path(__file__).parent / "qa" / "escritorio-oscuro.png")
            )
            window.tabs.setCurrentIndex(1)
            for i in range(4):
                window.operation.setCurrentIndex(i)
                self.app.processEvents()
            window.operation.setCurrentIndex(0)
            window.add_item(window.tool_files, "uno.pdf")
            window.add_item(window.tool_files, "dos.pdf")
            window.tool_files.setCurrentRow(1)
            window.move(window.tool_files, -1)
            self.assertEqual(window.paths(window.tool_files), ["dos.pdf", "uno.pdf"])
            self.app.processEvents()
            window.grab().save(str(Path(__file__).parent / "qa" / "gestor-pdf.png"))
            window.scan_files.clear()
            window.close()
            reopened = Window(
                QSettings(str(Path(temp) / "prefs.ini"), QSettings.IniFormat)
            )
            self.assertTrue(reopened.settings.value("dark", False, type=bool))
            reopened.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
