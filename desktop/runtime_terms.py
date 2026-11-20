"""Present the bundled Microsoft runtime terms once, storing consent portably."""
from pathlib import Path
import sys, hashlib

def accept_runtime_terms(parent=None):
    if not getattr(sys, 'frozen', False):
        return True
    from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QDialogButtonBox, QLabel
    text = (Path(sys._MEIPASS) / 'legal/dependencies/Native/Visual-C-V14-License-Redistributable_and_Runtime_ENU.txt').read_text('utf-8')
    digest = hashlib.sha256(text.encode('utf-8')).hexdigest()
    marker = Path(sys.executable).parent / 'Datos/componentes-microsoft-aceptados.txt'
    if marker.is_file() and marker.read_text('utf-8') == digest:
        return True
    dialog = QDialog(parent)
    dialog.setWindowTitle('FolioScan · Microsoft runtime terms')
    dialog.resize(760, 560)
    layout = QVBoxLayout(dialog)
    label = QLabel('Condiciones de los componentes Microsoft incluidos / Bundled Microsoft component terms.\n'
                   'Solo afectan a esos componentes; FolioScan y Qt conservan sus propias licencias.\n'
                   'These terms apply only to Microsoft components, not to FolioScan or Qt.')
    label.setWordWrap(True)
    layout.addWidget(label)
    browser = QTextBrowser()
    browser.setPlainText(text)
    layout.addWidget(browser)
    buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    buttons.button(QDialogButtonBox.Ok).setText('Acepto / I agree')
    buttons.button(QDialogButtonBox.Cancel).setText('Salir / Exit')
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    layout.addWidget(buttons)
    if dialog.exec() != QDialog.Accepted:
        return False
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(digest, encoding='utf-8')
    return True
