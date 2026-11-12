"""Per-page output composition. All coordinates use a top-left page origin."""

import copy
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QDoubleSpinBox,
    QSpinBox,
    QSlider,
    QWidget,
    QDialogButtonBox,
)
from i18n import tr
import core


class PagePreview(QWidget):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.setMinimumSize(300, 250)
        self.last = None

    # Dibuja la previsualización usando la misma geometría que la exportación.
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#26384D"))
        s = self.editor.specs[self.editor.index]
        self.factor = min(
            (self.width() - 20) / s["width"], (self.height() - 20) / s["height"]
        )
        painter.translate(
            (self.width() - s["width"] * self.factor) / 2,
            (self.height() - s["height"] * self.factor) / 2,
        )
        painter.scale(self.factor, self.factor)
        painter.setClipRect(QRectF(0, 0, s["width"], s["height"]))
        painter.fillRect(QRectF(0, 0, s["width"], s["height"]), Qt.white)
        pixmap = self.editor.pixmap
        x, y, w, h = core.layout_box(s, (pixmap.width(), pixmap.height()))
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.drawPixmap(QRectF(x, y, w, h), pixmap, QRectF(pixmap.rect()))

    # Registra el punto inicial del arrastre en coordenadas del control.
    def mousePressEvent(self, event):
        self.last = event.position()

    # Convierte el movimiento del puntero a coordenadas normalizadas de la hoja.
    def mouseMoveEvent(self, event):
        if self.last is None:
            return
        delta = event.position() - self.last
        self.last = event.position()
        s = self.editor.specs[self.editor.index]
        s["x"] = max(-1, min(1, s["x"] + delta.x() / self.factor / s["width"]))
        s["y"] = max(-1, min(1, s["y"] + delta.y() / self.factor / s["height"]))
        self.update()

    # Termina el arrastre y sincroniza los valores de los controles.
    def mouseReleaseEvent(self, event):
        self.last = None
        self.editor.load_controls()


class LayoutEditor(QDialog):
    def __init__(self, paths, parent):
        super().__init__(parent)
        self.paths = paths
        self.index = 0
        self.loading = False
        self.setWindowTitle(tr("Preparar salida"))
        self.resize(850, 850)
        self.specs = [
            dict(
                format="A4",
                width=595.0,
                height=842.0,
                scale=1.0,
                x=0.0,
                y=0.0,
                pixelsWide=1240,
                pixelsHigh=1754,
            )
            for _ in paths
        ]
        outer = QVBoxLayout(self)
        nav = QHBoxLayout()
        self.number = QLabel()
        for label, delta in [("‹", -1), ("›", 1)]:
            button = QPushButton(label)
            button.clicked.connect(lambda checked=False, d=delta: self.change(d))
            nav.addWidget(button)
        nav.insertWidget(1, self.number)
        outer.addLayout(nav)
        self.preview = PagePreview(self)
        outer.addWidget(self.preview, 1)
        row = QHBoxLayout()
        self.paper = QComboBox()
        self.paper.addItems(["Original"] + list(core.FORMATS) + [tr("Personalizado")])
        row.addWidget(QLabel(tr("Formato de papel")))
        row.addWidget(self.paper)
        self.output = QComboBox()
        self.output.addItems(["PDF", "JPG", "PNG"])
        row.addWidget(QLabel(tr("Salida")))
        row.addWidget(self.output)
        outer.addLayout(row)
        row = QHBoxLayout()
        self.w = self.number_field(row, "Ancho (mm)", 4, 1411)
        self.h = self.number_field(row, "Alto (mm)", 4, 1411)
        outer.addLayout(row)
        row = QHBoxLayout()
        self.pw = self.number_field(row, "Ancho (px)", 64, 6000, True)
        self.ph = self.number_field(row, "Alto (px)", 64, 6000, True)
        outer.addLayout(row)
        self.controls = {}
        for name, key, minimum, maximum in [
            ("Escala", "scale", 10, 400),
            ("Horizontal", "x", -100, 100),
            ("Vertical", "y", -100, 100),
        ]:
            row = QHBoxLayout()
            row.addWidget(QLabel(tr(name)))
            slider = QSlider(Qt.Horizontal)
            slider.setRange(minimum, maximum)
            slider.valueChanged.connect(self.changed)
            self.controls[key] = slider
            row.addWidget(slider)
            outer.addLayout(row)
        row = QHBoxLayout()
        center = QPushButton(tr("Centrar"))
        center.clicked.connect(self.center)
        all_pages = QPushButton(tr("Aplicar a todas"))
        all_pages.clicked.connect(self.all_pages)
        row.addWidget(center)
        row.addWidget(all_pages)
        outer.addLayout(row)
        outer.addWidget(QLabel(tr("Lo que queda fuera de la hoja se recorta.")))
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Save).setText(tr("Guardar"))
        buttons.button(QDialogButtonBox.Cancel).setText(tr("Cancelar"))
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        outer.addWidget(buttons)
        self.paper.currentIndexChanged.connect(self.paper_changed)
        self.output.currentIndexChanged.connect(self.changed)
        for spin in [self.w, self.h, self.pw, self.ph]:
            spin.valueChanged.connect(self.changed)
        self.load_page()

    # Crea una entrada numérica con límites explícitos para evitar tamaños inválidos.
    def number_field(self, row, name, minimum, maximum, integer=False):
        row.addWidget(QLabel(tr(name)))
        spin = QSpinBox() if integer else QDoubleSpinBox()
        spin.setRange(minimum, maximum)
        row.addWidget(spin)
        return spin

    # Carga la imagen de la página activa y presenta sus ajustes independientes.
    def load_page(self):
        self.pixmap = QPixmap(self.paths[self.index])
        self.load_controls()

    # Sincroniza controles sin disparar cambios que sobrescriban el modelo.
    def load_controls(self):
        self.loading = True
        s = self.specs[self.index]
        self.number.setText(f"{self.index+1} / {len(self.paths)}")
        self.paper.setCurrentIndex(
            (["Original"] + list(core.FORMATS) + ["Custom"]).index(s["format"])
        )
        self.w.setValue(s["width"] * 25.4 / 72)
        self.h.setValue(s["height"] * 25.4 / 72)
        self.pw.setValue(s["pixelsWide"])
        self.ph.setValue(s["pixelsHigh"])
        for key, slider in self.controls.items():
            slider.setValue(round(s[key] * 100))
        self.loading = False
        self.preview.update()

    # Pasa los valores de los controles al modelo y redibuja el resultado.
    def changed(self, *_):
        if self.loading:
            return
        s = self.specs[self.index]
        s["width"] = self.w.value() * 72 / 25.4
        s["height"] = self.h.value() * 72 / 25.4
        s["pixelsWide"] = self.pw.value()
        s["pixelsHigh"] = self.ph.value()
        if self.output.currentText() != "PDF":
            s["width"] = s["pixelsWide"] * 72 / 150
            s["height"] = s["pixelsHigh"] * 72 / 150
        for key, slider in self.controls.items():
            s[key] = slider.value() / 100
        self.preview.update()

    # Actualiza el papel seleccionado y calcula una resolución inicial acotada.
    def paper_changed(self, index):
        if self.loading:
            return
        s = self.specs[self.index]
        s["format"] = (["Original"] + list(core.FORMATS) + ["Custom"])[index]
        if s["format"] != "Custom":
            s["width"], s["height"] = core.page_size(
                s["format"], (self.pixmap.width(), self.pixmap.height())
            )
        factor = min(150 / 72, 4096 / max(s["width"], s["height"]))
        s["pixelsWide"] = max(64, round(s["width"] * factor))
        s["pixelsHigh"] = max(64, round(s["height"] * factor))
        self.load_controls()
        self.changed()

    # Restablece el encaje proporcional centrado de la imagen.
    def center(self):
        self.specs[self.index].update(scale=1, x=0, y=0)
        self.load_controls()

    # Copia los ajustes actuales a todas las páginas sin compartir objetos mutables.
    def all_pages(self):
        self.specs = [copy.deepcopy(self.specs[self.index]) for _ in self.paths]

    # Cambia de página conservando los ajustes de la anterior.
    def change(self, delta):
        if 0 <= self.index + delta < len(self.paths):
            self.index += delta
            self.load_page()

    # Valida el tamaño final antes de confirmar el editor.
    def accept(self):
        from PySide6.QtWidgets import QMessageBox

        self.changed()
        if any(s["pixelsWide"] * s["pixelsHigh"] > 24000000 for s in self.specs):
            QMessageBox.warning(
                self,
                tr("Error"),
                tr("Ancho/alto: 4–1411 mm; imagen: 64–6000 px, máximo 24 megapíxeles."),
            )
            return
        super().accept()
