import os
import sys
import uuid
import tempfile
from pathlib import Path

from PySide6.QtCore import Qt, QSettings, QThread, Signal, QTimer, QPointF, QRectF
from PySide6.QtGui import (
    QPixmap,
    QImage,
    QIcon,
    QPainter,
    QColor,
    QPen,
    QPalette,
    QFontDatabase,
)
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
    QFileDialog,
    QMessageBox,
    QMenu,
    QDialog,
    QDialogButtonBox,
    QSplitter,
    QFrame,
)
import core

ASSETS = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))


# Carga fuentes locales para mostrar los mismos glifos en la interfaz y las pruebas.
def configure_fonts():
    font_dir = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
    for name in ("segoeui.ttf", "segoeuib.ttf", "seguisym.ttf"):
        if (font_dir / name).is_file():
            QFontDatabase.addApplicationFont(str(font_dir / name))


class Worker(QThread):
    progress = Signal(str)
    completed = Signal(str)
    failed = Signal(str)

    def __init__(self, fn):
        super().__init__()
        self.fn = fn

    def run(self):
        try:
            self.completed.emit(self.fn(self.progress.emit))
        except Exception as error:
            self.failed.emit(str(error) or type(error).__name__)


class Corners(QWidget):
    def __init__(self, path):
        super().__init__()
        self.pixmap = QPixmap(path)
        self.points = core.detect_corners(path)
        self.drag = -1
        self.setMinimumSize(480, 360)
        self.setMouseTracking(True)

    def image_rect(self):
        size = self.pixmap.size()
        size.scale(self.size(), Qt.KeepAspectRatio)
        return QRectF(
            (self.width() - size.width()) / 2,
            (self.height() - size.height()) / 2,
            size.width(),
            size.height(),
        )

    # Dibuja la previsualización usando la misma geometría que la exportación.
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#0D1726"))
        rect = self.image_rect()
        painter.drawPixmap(rect.toRect(), self.pixmap)
        dots = [
            QPointF(rect.x() + x * rect.width(), rect.y() + y * rect.height())
            for x, y in self.points
        ]
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor("#55B5FF"), 3))
        for i in range(4):
            painter.drawLine(dots[i], dots[(i + 1) % 4])
        for i, dot in enumerate(dots):
            painter.setBrush(QColor("#55B5FF"))
            painter.drawEllipse(dot, 10, 10)
            painter.setPen(QColor("#000000"))
            painter.drawText(
                QRectF(dot.x() - 10, dot.y() - 10, 20, 20), Qt.AlignCenter, str(i + 1)
            )
            painter.setPen(QPen(QColor("#55B5FF"), 3))

    # Registra el punto inicial del arrastre en coordenadas del control.
    def mousePressEvent(self, event):
        rect = self.image_rect()
        p = event.position()
        distances = [
            (p.x() - (rect.x() + x * rect.width())) ** 2
            + (p.y() - (rect.y() + y * rect.height())) ** 2
            for x, y in self.points
        ]
        selected = distances.index(min(distances))
        if distances[selected] < 45**2:
            self.drag = selected

    # Convierte el movimiento del puntero a coordenadas normalizadas de la hoja.
    def mouseMoveEvent(self, event):
        if self.drag < 0:
            return
        rect = self.image_rect()
        point = event.position()
        self.points[self.drag] = [
            max(0, min(1, (point.x() - rect.x()) / rect.width())),
            max(0, min(1, (point.y() - rect.y()) / rect.height())),
        ]
        self.update()

    # Termina el arrastre y sincroniza los valores de los controles.
    def mouseReleaseEvent(self, event):
        self.drag = -1


class CropDialog(QDialog):
    def __init__(self, path, destination, parent):
        super().__init__(parent)
        self.path = path
        self.destination = destination
        self.setWindowTitle("Ajustar hoja")
        self.resize(820, 760)
        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel("Arrastra las cuatro esquinas hasta los bordes de la hoja.")
        )
        self.canvas = Corners(path)
        layout.addWidget(self.canvas, 1)
        row = QHBoxLayout()
        self.mode = QComboBox()
        self.mode.addItems(["Color", "Gris", "Blanco y negro"])
        row.addWidget(QLabel("Acabado"))
        row.addWidget(self.mode)
        row.addStretch()
        layout.addLayout(row)
        buttons = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Save)
        buttons.button(QDialogButtonBox.Cancel).setText("Cancelar")
        buttons.button(QDialogButtonBox.Save).setText("Aplicar recorte")
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.apply)
        layout.addWidget(buttons)

    # Aplica el recorte solicitado o muestra el error si las esquinas no son válidas.
    def apply(self):
        try:
            core.rectify_image(
                self.path,
                self.destination,
                self.canvas.points,
                __import__("i18n").source(self.mode.currentText()),
            )
        except Exception as error:
            QMessageBox.warning(self, "Revisa las esquinas", str(error))
            return
        self.accept()


class CameraDialog(QDialog):
    def __init__(self, directory, parent):
        super().__init__(parent)
        self.paths = []
        self.directory = Path(directory)
        self.camera = None
        self.frame = None
        self.setWindowTitle("Capturar hojas con la webcam")
        self.resize(850, 650)
        layout = QVBoxLayout(self)
        self.preview = QLabel("Abriendo cámara…")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumSize(600, 400)
        layout.addWidget(self.preview, 1)
        self.note = QLabel(
            "Coloca una hoja frente a la cámara. Puedes capturar varias y recortarlas después."
        )
        self.note.setWordWrap(True)
        layout.addWidget(self.note)
        row = QHBoxLayout()
        self.capture = QPushButton("Capturar hoja")
        self.capture.setEnabled(False)
        self.capture.clicked.connect(self.take)
        done = QPushButton("Terminar")
        done.clicked.connect(self.accept)
        row.addWidget(self.capture)
        row.addWidget(done)
        layout.addLayout(row)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        QTimer.singleShot(50, self.start)

    # Abre la cámara disponible y comienza la actualización periódica de la imagen.
    def start(self):
        import cv2

        self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.camera.isOpened():
            self.note.setText(
                "No se ha podido abrir la webcam. Comprueba la conexión y los permisos de cámara de Windows."
            )
            return
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.timer.start(65)

    # Obtiene un fotograma y lo convierte al formato de visualización de Qt.
    def tick(self):
        import cv2

        ok, frame = self.camera.read()
        if not ok:
            self.capture.setEnabled(False)
            return
        self.frame = frame
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(
            rgb.data, rgb.shape[1], rgb.shape[0], rgb.strides[0], QImage.Format_RGB888
        ).copy()
        self.preview.setPixmap(
            QPixmap.fromImage(image).scaled(
                self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
        self.capture.setEnabled(True)

    # Guarda el fotograma actual y lo añade a las capturas de esta sesión.
    def take(self):
        import cv2

        if self.frame is None:
            return
        path = self.directory / (uuid.uuid4().hex + ".jpg")
        if not cv2.imwrite(str(path), self.frame):
            QMessageBox.warning(self, "Cámara", "No se pudo guardar la captura.")
            return
        self.paths.append(str(path))
        self.note.setText(
            f"{len(self.paths)} hoja(s) capturada(s). Puedes capturar otra o terminar."
        )

    # Detiene el temporizador y libera el dispositivo de cámara.
    def done(self, result):
        self.timer.stop()
        if self.camera is not None:
            self.camera.release()
        super().done(result)


class Window(QMainWindow):
    def __init__(self, settings=None):
        super().__init__()
        self.settings = settings or QSettings("EscanerDocumentos", "Escritorio")
        self.session = tempfile.TemporaryDirectory(prefix="escaner-")
        self.worker = None
        self.setWindowTitle("FolioScan")
        self.resize(1120, 820)
        self.setMinimumSize(880, 680)
        self.setWindowIcon(QIcon(str(ASSETS / "scanner.png")))
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(28, 22, 28, 22)
        layout.setSpacing(16)
        header = QHBoxLayout()
        logo = QLabel()
        logo.setPixmap(
            QPixmap(str(ASSETS / "scanner.png")).scaled(
                48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
        header.addWidget(logo)
        title = QLabel("ESCÁNER DE DOCUMENTOS")
        title.setObjectName("brand")
        header.addWidget(title)
        header.addStretch()
        self.gear = QPushButton("⚙  Ajustes")
        self.gear.clicked.connect(self.settings_menu)
        header.addWidget(self.gear)
        layout.addLayout(header)
        self.tabs = QTabWidget()
        self.tabs.addTab(self.scanner_tab(), "Escáner de documentos")
        self.tabs.addTab(self.pdf_tab(), "Gestor de PDF")
        layout.addWidget(self.tabs, 1)
        self.status = QLabel("Listo. Tus archivos se procesan en este ordenador.")
        self.status.setWordWrap(True)
        self.status.setObjectName("status")
        layout.addWidget(self.status)
        self.apply_theme()

    def label(self, text, kind=None):
        result = QLabel(text)
        result.setWordWrap(True)
        if kind:
            result.setObjectName(kind)
        return result

    def button(self, title, callback, primary=False):
        result = QPushButton(title)
        result.clicked.connect(callback)
        result.setMinimumHeight(42)
        if primary:
            result.setObjectName("primary")
        return result

    def format_box(self):
        box = QComboBox()
        box.addItems(["Original"] + list(core.FORMATS))
        box.setCurrentText(str(self.settings.value("format", "A4")))
        box.currentTextChanged.connect(
            lambda value: self.settings.setValue("format", value)
        )
        return box

    def file_list(self):
        result = QListWidget()
        result.setDragDropMode(QAbstractItemView.InternalMove)
        result.setSelectionMode(QAbstractItemView.SingleSelection)
        result.setMinimumHeight(170)
        return result

    def list_controls(self, files):
        row = QHBoxLayout()
        for title, action in [
            ("↑ Subir", lambda: self.move(files, -1)),
            ("↓ Bajar", lambda: self.move(files, 1)),
            (
                "Quitar",
                lambda: (
                    files.takeItem(files.currentRow())
                    if files.currentRow() >= 0
                    else None
                ),
            ),
        ]:
            row.addWidget(self.button(title, action))
        return row

    # Construye los controles de captura, previsualización y edición del escáner.
    def scanner_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(14)
        layout.addWidget(self.label("Del papel a tu escritorio.", "hero"))
        layout.addWidget(
            self.label(
                "Importa fotos o captura con la webcam. Ajusta los bordes y guarda un PDF o fotos individuales.",
                "muted",
            )
        )
        split = QSplitter()
        left = QWidget()
        column = QVBoxLayout(left)
        column.setContentsMargins(0, 0, 12, 0)
        row = QHBoxLayout()
        row.addWidget(self.button("+ Importar fotos", self.import_scan))
        row.addWidget(self.button("Abrir webcam", self.camera))
        column.addLayout(row)
        self.scan_files = self.file_list()
        self.scan_files.currentItemChanged.connect(self.preview_scan)
        self.scan_files.itemDoubleClicked.connect(lambda _: self.crop())
        column.addWidget(self.scan_files, 1)
        column.addLayout(self.list_controls(self.scan_files))
        row = QHBoxLayout()
        row.addWidget(self.button("Ajustar bordes / color", self.crop))
        row.addWidget(self.button("Girar 90°", self.rotate))
        column.addLayout(row)
        split.addWidget(left)
        self.preview = QLabel("Selecciona una página para verla")
        self.preview.setObjectName("preview")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumSize(300, 260)
        split.addWidget(self.preview)
        split.setSizes([480, 440])
        layout.addWidget(split, 1)
        row = QHBoxLayout()
        row.addWidget(QLabel("Tamaño de página"))
        self.scan_format = self.format_box()
        row.addWidget(self.scan_format)
        row.addStretch()
        row.addWidget(self.button("Guardar fotos JPG…", self.save_photos))
        row.addWidget(self.button("Guardar PDF…", self.save_scan_pdf, True))
        layout.addLayout(row)
        layout.addWidget(
            self.label(
                "Arrastra para ordenar. DIN A añade margen sin deformar la hoja; Original usa su proporción. El recorte corrige la perspectiva, no aplana pliegues complejos.",
                "muted",
            )
        )
        return widget

    # Construye el gestor de PDF y conecta las cuatro operaciones disponibles.
    def pdf_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(14)
        layout.addWidget(self.label("Tus PDF, a tu manera.", "hero"))
        layout.addWidget(
            self.label(
                "Une, separa y convierte. Sin anuncios, cuentas ni subida de documentos.",
                "muted",
            )
        )
        self.operation = QComboBox()
        self.operation.addItems(
            [
                "Unir varios PDF",
                "Separar PDF en hojas → ZIP",
                "PDF a imágenes JPG → ZIP",
                "Imágenes a PDF",
            ]
        )
        self.operation.currentIndexChanged.connect(self.operation_changed)
        layout.addWidget(self.operation)
        self.tool_hint = self.label(
            "Añade varios PDF y ordénalos como quieras que aparezcan en el resultado.",
            "muted",
        )
        layout.addWidget(self.tool_hint)
        row = QHBoxLayout()
        row.addWidget(self.button("+ Añadir archivos", self.add_tools))
        row.addStretch()
        row.addWidget(QLabel("Tamaño para imágenes"))
        self.pdf_format = self.format_box()
        row.addWidget(self.pdf_format)
        layout.addLayout(row)
        self.tool_files = self.file_list()
        layout.addWidget(self.tool_files, 1)
        layout.addLayout(self.list_controls(self.tool_files))
        layout.addWidget(self.button("Procesar y guardar…", self.process_tools, True))
        layout.addWidget(
            self.label(
                "Siempre elegirás la carpeta y el nombre antes de guardar. Al separar, el ZIP contiene un PDF por página; al convertir a imágenes, un JPG por página (hasta 144 ppp).",
                "muted",
            )
        )
        return widget

    # Vacía la selección anterior para no mezclar tipos de archivo entre operaciones.
    def operation_changed(self):
        self.tool_files.clear()
        hints = [
            "Añade varios PDF y ordénalos como quieras que aparezcan en el resultado.",
            "Elige un PDF. Cada página se guardará en un PDF independiente dentro del ZIP.",
            "Elige un PDF. Cada página se convertirá en un JPG dentro del ZIP.",
            "Añade una o varias imágenes y revisa el orden antes de generar el PDF.",
        ]
        self.tool_hint.setText(hints[self.operation.currentIndex()])
        self.pdf_format.setEnabled(self.operation.currentIndex() == 3)

    def add_item(self, files, path, label=None):
        item = QListWidgetItem(label or Path(path).name)
        item.setData(Qt.UserRole, str(path))
        item.setToolTip(str(path))
        files.addItem(item)

    def paths(self, files):
        return [files.item(i).data(Qt.UserRole) for i in range(files.count())]

    # Cambia el orden de una página; el orden visible será el orden exportado.
    def move(self, files, delta):
        i = files.currentRow()
        j = i + delta
        if i >= 0 and 0 <= j < files.count():
            item = files.takeItem(i)
            files.insertItem(j, item)
            files.setCurrentRow(j)

    # Normaliza las fotos importadas y las incorpora a la lista de páginas.
    def import_scan(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleccionar fotos",
            "",
            "Imágenes (*.jpg *.jpeg *.png *.bmp *.webp *.tif *.tiff)",
        )
        for path in paths:
            try:
                target = Path(self.session.name) / (uuid.uuid4().hex + ".jpg")
                with core.normalized_image(path) as image:
                    image.save(target, quality=97)
                self.add_item(self.scan_files, target, Path(path).name)
            except Exception as error:
                QMessageBox.warning(self, "No se pudo importar", str(error))
        if self.scan_files.count():
            self.scan_files.setCurrentRow(self.scan_files.count() - 1)

    # Actualiza la miniatura sin cambiar el archivo ni su resolución original.
    def preview_scan(self, *_):
        item = self.scan_files.currentItem()
        if not item:
            self.preview.clear()
            self.preview.setText("Selecciona una página para verla")
            return
        pixmap = QPixmap(item.data(Qt.UserRole))
        self.preview.setPixmap(
            pixmap.scaled(
                max(100, self.preview.width() - 20),
                max(100, self.preview.height() - 20),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "preview"):
            QTimer.singleShot(0, self.preview_scan)

    # Abre el editor de cuatro esquinas y conserva el resultado como una nueva imagen.
    def crop(self):
        item = self.scan_files.currentItem()
        if not item:
            return
        target = str(Path(self.session.name) / (uuid.uuid4().hex + ".jpg"))
        try:
            dialog = CropDialog(item.data(Qt.UserRole), target, self)
        except Exception as error:
            QMessageBox.warning(self, "No se pudo abrir la foto", str(error))
            return
        if dialog.exec() == QDialog.Accepted:
            item.setData(Qt.UserRole, target)
            self.preview_scan()

    # Gira la imagen seleccionada 90 grados y actualiza su previsualización.
    def rotate(self):
        item = self.scan_files.currentItem()
        if not item:
            return
        target = Path(self.session.name) / (uuid.uuid4().hex + ".jpg")
        with core.normalized_image(item.data(Qt.UserRole)) as image:
            image.rotate(-90, expand=True).save(target, quality=97)
        item.setData(Qt.UserRole, str(target))
        self.preview_scan()

    # Abre la captura de cámara y añade las fotos obtenidas a la sesión.
    def camera(self):
        dialog = CameraDialog(self.session.name, self)
        dialog.exec()
        for path in dialog.paths:
            self.add_item(self.scan_files, path, f"Captura {self.scan_files.count()+1}")
        if self.scan_files.count():
            self.scan_files.setCurrentRow(self.scan_files.count() - 1)

    # Usa el diálogo nativo para elegir carpeta y nombre en cada exportación.
    def destination(self, title, extension):
        directory = str(
            self.settings.value("lastFolder", str(Path.home() / "Documents"))
        )
        path, _ = QFileDialog.getSaveFileName(
            self,
            title,
            str(Path(directory) / ("Documento" + extension)),
            f"Archivos {extension} (*{extension})",
        )
        if path:
            if not path.lower().endswith(extension):
                path += extension
            self.settings.setValue("lastFolder", str(Path(path).parent))
        return path

    # Detiene la operación y explica cómo añadir páginas cuando la sesión está vacía.
    def need_images(self):
        paths = self.paths(self.scan_files)
        if not paths:
            QMessageBox.information(
                self,
                "Añade páginas",
                "Importa una foto o captura una hoja con la webcam.",
            )
        return paths

    # Abre la composición posterior al escaneo y prepara una copia en la biblioteca local.
    def save_scan_pdf(self):
        paths = self.need_images()
        if not paths:
            return
        target = self.destination("Guardar PDF: elige la carpeta de destino", ".pdf")
        fmt = self.scan_format.currentText()
        if target:
            self.run_job(
                lambda progress: core.images_to_pdf(paths, target, fmt, progress)
            )

    def save_photos(self):
        paths = self.need_images()
        if not paths:
            return
        directory = QFileDialog.getExistingDirectory(
            self,
            "Elige dónde guardar las fotos",
            str(self.settings.value("lastFolder", str(Path.home() / "Documents"))),
        )
        if directory:
            self.settings.setValue("lastFolder", directory)
            self.run_job(
                lambda progress: core.export_photos(paths, directory, progress)
            )

    # Selecciona PDF o imágenes según la operación activa.
    def add_tools(self):
        index = self.operation.currentIndex()
        filter = (
            "Imágenes (*.jpg *.jpeg *.png *.bmp *.webp *.tif *.tiff)"
            if index == 3
            else "PDF (*.pdf)"
        )
        if index in (1, 2):
            path, _ = QFileDialog.getOpenFileName(self, "Seleccionar PDF", "", filter)
            if path:
                self.tool_files.clear()
                self.add_item(self.tool_files, path)
        else:
            paths, _ = QFileDialog.getOpenFileNames(
                self, "Seleccionar archivos", "", filter
            )
            for path in paths:
                self.add_item(self.tool_files, path)

    # Despacha la operación elegida después de pedir un destino.
    def process_tools(self):
        paths = self.paths(self.tool_files)
        operation = self.operation.currentIndex()
        fmt = self.pdf_format.currentText()
        if not paths or (operation == 0 and len(paths) < 2):
            QMessageBox.information(
                self,
                "Faltan archivos",
                "Selecciona al menos dos PDF para unir, o un archivo para convertir.",
            )
            return
        target = self.destination(
            "Guardar resultado: elige la carpeta de destino",
            ".zip" if operation in (1, 2) else ".pdf",
        )
        if not target:
            return
        jobs = [
            lambda p: core.merge_pdfs(paths, target, p),
            lambda p: core.split_pdf(paths[0], target, p),
            lambda p: core.pdf_to_images(paths[0], target, p),
            lambda p: core.images_to_pdf(paths, target, fmt, p),
        ]
        self.run_job(jobs[operation])

    # Deshabilita acciones mientras trabaja el hilo y entrega resultados cuando este termina.
    def run_job(self, fn):
        if self.worker and self.worker.isRunning():
            return
        self.tabs.setEnabled(False)
        self.gear.setEnabled(False)
        self.status.setText("Procesando…")
        self.worker = Worker(fn)
        self.worker.progress.connect(self.status.setText)
        self.worker.completed.connect(self.completed)
        self.worker.failed.connect(self.failed)
        self.worker.finished.connect(self.finish_job)
        self.worker.start()

    # Notifica el resultado e incluye una acción para abrir su carpeta.
    def completed(self, path):
        self.status.setText("Guardado en: " + path)
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Resultado guardado")
        dialog.setText("El archivo se ha guardado correctamente.")
        dialog.setInformativeText(path)
        open_button = dialog.addButton("Abrir carpeta", QMessageBox.ActionRole)
        dialog.addButton("Aceptar", QMessageBox.AcceptRole)
        dialog.exec()
        if dialog.clickedButton() == open_button:
            os.startfile(path if Path(path).is_dir() else str(Path(path).parent))

    # Muestra el error sin simular que la operación se ha completado.
    def failed(self, error):
        self.status.setText("No se pudo completar la operación.")
        QMessageBox.warning(self, "Revisa los archivos", error)

    # Vuelve a habilitar las acciones después de finalizar el trabajo.
    def finish_job(self):
        self.tabs.setEnabled(True)
        self.gear.setEnabled(True)

    # Despliega tema, permisos, idioma y ayuda sin un botón redundante de cierre.
    def settings_menu(self):
        menu = QMenu(self)
        dark = self.settings.value("dark", False, type=bool)
        menu.addAction(
            "Cambiar a modo claro" if dark else "Cambiar a modo noche",
            self.toggle_theme,
        )
        menu.addAction(
            "Administración de permisos de cámara",
            lambda: os.startfile("ms-settings:privacy-webcam"),
        )
        menu.addAction("¿Cómo funciona?", self.help)
        menu.exec(self.gear.mapToGlobal(self.gear.rect().bottomLeft()))

    # Invierte la preferencia de tema y la guarda para la próxima apertura.
    def toggle_theme(self):
        self.settings.setValue(
            "dark", not self.settings.value("dark", False, type=bool)
        )
        self.settings.sync()
        self.apply_theme()

    # Aplica una paleta coherente a fondos, texto, botones y selección.
    def apply_theme(self):
        dark = self.settings.value("dark", False, type=bool)
        bg, card, ink, muted, accent, soft = (
            ("#101B2B", "#1B2D44", "#F1F6FC", "#BACCE0", "#8EC5FF", "#2D4663")
            if dark
            else ("#F3F7FC", "#FFFFFF", "#17334F", "#506782", "#2167B1", "#DFEBF8")
        )
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(bg))
        palette.setColor(QPalette.WindowText, QColor(ink))
        palette.setColor(QPalette.Base, QColor(card))
        palette.setColor(QPalette.AlternateBase, QColor(soft))
        palette.setColor(QPalette.Text, QColor(ink))
        palette.setColor(QPalette.Button, QColor(soft))
        palette.setColor(QPalette.ButtonText, QColor(ink))
        palette.setColor(QPalette.Highlight, QColor(accent))
        palette.setColor(
            QPalette.HighlightedText, QColor("#101B2B" if dark else "white")
        )
        QApplication.instance().setPalette(palette)
        self.setStyleSheet(
            f"""
            QWidget {{font-family:'Segoe UI';font-size:14px;color:{ink};}}
            QMainWindow,QDialog {{background:{bg};}}
            QLabel#brand {{font-size:15px;font-weight:700;color:{accent};letter-spacing:1px;}}
            QLabel#hero {{font-size:34px;font-weight:700;}}
            QLabel#muted {{color:{muted};font-size:13px;}}
            QLabel#status {{background:{soft};border-radius:10px;padding:12px;}}
            QLabel#preview {{background:{card};border:1px solid {soft};border-radius:16px;}}
            QPushButton {{background:{soft};border:0;border-radius:10px;padding:10px 16px;font-weight:600;}}
            QPushButton:hover {{border:1px solid {accent};}}
            QPushButton:disabled {{color:{muted};}}
            QPushButton#primary {{background:{accent};color:{'#101B2B' if dark else '#FFFFFF'};}}
            QComboBox {{background:{card};border:1px solid {soft};border-radius:8px;padding:10px;min-width:90px;}}
            QListWidget {{background:{card};border:1px solid {soft};border-radius:12px;padding:8px;}}
            QListWidget::item {{padding:12px;border-radius:8px;}}
            QListWidget::item:selected {{background:{soft};color:{ink};}}
            QTabWidget::pane {{border:1px solid {soft};border-radius:14px;}}
            QTabBar::tab {{padding:14px 24px;background:{"#365678" if dark else "#DCEAFF"};margin-right:6px;border-top-left-radius:10px;border-top-right-radius:10px;}}
            QTabBar::tab:selected {{background:{"#102C50" if dark else "#174A86"};color:#FFFFFF;font-weight:700;}}
        """
        )

    # Muestra instrucciones y límites reales del escaneo y la exportación.
    def help(self):
        QMessageBox.information(
            self,
            "Cómo funciona y privacidad",
            "ESCÁNER\nImporta fotos o usa la webcam. Selecciona una página y pulsa Ajustar bordes para arrastrar sus cuatro esquinas. Puedes girar, ordenar y elegir A0–A10 u Original. Guarda en PDF o JPG.\n\nGESTOR PDF\nElige una operación, añade los archivos y revisa el orden. Separar genera un ZIP con un PDF por hoja; PDF a imágenes crea un ZIP con JPG. Siempre se pregunta el destino.\n\nLos archivos se procesan localmente. No hay publicidad, cuentas ni servidores propios. Los originales no se modifican. Los PDF protegidos necesitan una copia sin contraseña. El recorte corrige perspectiva; no reconstruye pliegues ni texto oculto. Exporta las capturas antes de cerrar: la sesión del escáner es temporal.\n\nEscáner de documentos 2.0 · Windows",
        )

    # Impide cerrar durante una escritura y conserva preferencias y sesión.
    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            QMessageBox.information(
                self, "Procesando", "Espera a que termine el guardado antes de cerrar."
            )
            event.ignore()
            return
        if (
            self.scan_files.count()
            and QMessageBox.question(
                self,
                "Cerrar aplicación",
                "Las páginas de esta sesión son temporales. ¿Cerrar? Las copias que hayas guardado se conservan.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            != QMessageBox.Yes
        ):
            event.ignore()
            return
        self.settings.sync()
        self.session.cleanup()
        event.accept()


# Arranca la aplicación o ejecuta el autodiagnóstico sin ventanas.
def main():
    if "--self-test" in sys.argv:
        from smoke import run

        run(sys.argv[sys.argv.index("--self-test") + 1])
        return
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("FolioScan")
    configure_fonts()
    from v3 import WindowV3

    window = WindowV3()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
