"""Exercise consent/cancellation with synthetic terms and a temporary data folder."""
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
import sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtCore import QTimer
from runtime_terms import accept_runtime_terms

class RuntimeTermsTests(unittest.TestCase):
    def test_cancel_accept_and_remember(self):
        app = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            license_file = root/'legal/dependencies/Native/Visual-C-V14-License-Redistributable_and_Runtime_ENU.txt'
            license_file.parent.mkdir(parents=True)
            license_file.write_text('SYNTHETIC TEST TERMS — not a license agreement.', 'utf-8')
            marker = root/'Datos/componentes-microsoft-aceptados.txt'
            def respond(accepted):
                for widget in app.topLevelWidgets():
                    if isinstance(widget, QDialog) and widget.isVisible():
                        widget.accept() if accepted else widget.reject()
            with patch.object(sys,'frozen',True,create=True), patch.object(sys,'_MEIPASS',str(root),create=True), patch.object(sys,'executable',str(root/'test.exe')):
                QTimer.singleShot(0,lambda:respond(False))
                self.assertFalse(accept_runtime_terms())
                self.assertFalse(marker.exists())
                QTimer.singleShot(0,lambda:respond(True))
                self.assertTrue(accept_runtime_terms())
                self.assertTrue(marker.exists())
                # A remembered decision must not create another dialog.
                with patch('PySide6.QtWidgets.QDialog',side_effect=AssertionError('Unexpected prompt')):
                    self.assertTrue(accept_runtime_terms())

if __name__ == '__main__':
    unittest.main()
