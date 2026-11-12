"""Offline translations shared with the Android build, without network calls."""

import csv
from pathlib import Path
import sys
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QTabWidget,
    QComboBox,
    QApplication,
    QMessageBox,
)

CODES = ["es", "en", "fr", "it", "pt", "nl", "uk", "ru", "sv", "pl", "cs"]
NAMES = [
    "Español",
    "English",
    "Français",
    "Italiano",
    "Português",
    "Nederlands",
    "Українська",
    "Русский",
    "Svenska",
    "Polski",
    "Čeština",
]
ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
with (ROOT / "translations.tsv").open(encoding="utf-8", newline="") as stream:
    ROWS = {
        row["es"].replace("\\n", "\n"): {
            key: value.replace("\\n", "\n") for key, value in row.items()
        }
        for row in csv.DictReader(stream, delimiter="\t")
    }
language = "es"


def source(value):
    """Recover a catalogue key without passing translated values to algorithms."""
    if value in ROWS:
        return value
    for key, row in ROWS.items():
        if value in row.values():
            return key
    return value


def tr(source):
    if source in ROWS:
        return ROWS[source].get(language, source)
    for prefix in ["⚙  ", "⚙ ", "+ ", "↑ ", "↓ "]:
        if source.startswith(prefix):
            return prefix + tr(source[len(prefix) :])
    return source


# Aplica el recorte solicitado o muestra el error si las esquinas no son válidas.
def apply(root):
    """Retain source text as widget metadata so changing language is reversible."""
    for widget in [root] + root.findChildren(QLabel) + root.findChildren(QPushButton):
        if not isinstance(widget, (QLabel, QPushButton)):
            continue
        if widget.property("footer"):
            widget.setText(
                tr("Gracias por descargar la aplicación.")
                + '  ·  <a href="https://github.com/Brass-Ebort">github.com/Brass-Ebort</a>'
            )
            continue
        current = widget.text()
        previous = widget.property("translated_text")
        if current != previous:
            widget.setProperty("source_text", source(current))
        translated = tr(widget.property("source_text") or current)
        widget.setProperty("translated_text", translated)
        if current != translated:
            widget.setText(translated)
    root.setWindowTitle(tr(source(root.windowTitle())))
    for combo in root.findChildren(QComboBox):
        old = combo.blockSignals(True)
        for index in range(combo.count()):
            text = combo.itemText(index)
            combo.setItemText(index, tr(source(text)))
        combo.blockSignals(old)
    for tabs in root.findChildren(QTabWidget):
        for i in range(tabs.count()):
            page = tabs.widget(i)
            key = page.property("tab_source") or tabs.tabText(i)
            page.setProperty("tab_source", key)
            tabs.setTabText(i, tr(key))
    if isinstance(root, QMessageBox):
        root.setWindowTitle(tr(root.windowTitle()))
        root.setText(tr(root.text()))
        root.setInformativeText(tr(root.informativeText()))


def start_timer(owner):
    timer = QTimer(owner)

    def update():
        for root in QApplication.topLevelWidgets():
            if root.isVisible():
                apply(root)

    timer.timeout.connect(update)
    timer.start(200)
    return timer
