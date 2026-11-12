"""V3 desktop shell: persistent local library and explicit export destinations.

The scanning/cropping controls are reused from app.py. File processing stays in
core.py, so its transaction and geometry rules can be tested without a GUI.
"""

import json
import os
import shutil
import sys
import uuid
from pathlib import Path
from types import SimpleNamespace

from PySide6.QtCore import Qt, QSettings
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QListWidget,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QMenu,
    QDialog,
    QComboBox,
    QDialogButtonBox,
    QInputDialog,
    QSplitter,
)
from app import Window, Worker
from layout_editor import LayoutEditor
import core
import i18n
from drop_files import FileDropFilter, IMAGE_EXTENSIONS


class WindowV3(Window):
    """A portable workspace lives beside the executable, including preferences."""

    def __init__(self, settings=None, data_root=None):
        base = (
            Path(sys.executable).parent
            if getattr(sys, "frozen", False)
            else Path(__file__).parent
        )
        self.data_root = Path(data_root or base / "Datos")
        self.data_root.mkdir(parents=True, exist_ok=True)
        self.drafts = self.data_root / "Biblioteca"
        self.drafts.mkdir(exist_ok=True)
        settings = settings or QSettings(
            str(self.data_root / "preferencias.ini"), QSettings.IniFormat
        )
        i18n.language = str(settings.value("language", "es"))
        super().__init__(settings)
        # Replace the temporary scan workspace with a persistent portable one.
        self.session.cleanup()
        session = self.data_root / "Sesion"
        session.mkdir(exist_ok=True)
        self.session = SimpleNamespace(name=str(session), cleanup=lambda: None)
        self.manifest = session / "paginas.json"
        try:
            for path in json.loads(self.manifest.read_text("utf-8")):
                candidate = session / Path(path).name
                if candidate.is_file():
                    self.add_item(self.scan_files, candidate)
        except (OSError, ValueError):
            pass  # A first launch has no saved session yet.
        # Move the gear into the same row as the two actual tabs.
        outer = self.centralWidget().layout()
        header = outer.takeAt(0).layout()
        while header.count():
            item = header.takeAt(0)
            if item.widget() and item.widget() is not self.gear:
                item.widget().hide()
                item.widget().setParent(None)
                item.widget().deleteLater()
        self.gear.setText("⚙")
        self.gear.setToolTip(i18n.tr("Configuración"))
        self.tabs.setCornerWidget(self.gear, Qt.TopRightCorner)
        footer = QLabel(
            'Gracias por descargar la aplicación.  ·  <a href="https://github.com/Brass-Ebort">github.com/Brass-Ebort</a>'
        )
        footer.setProperty("footer", True)
        footer.setOpenExternalLinks(True)
        footer.setStyleSheet("font-size:11px;")
        outer.addWidget(footer)
        self.refresh_library()
        self.scan_files.model().rowsMoved.connect(self.persist_session)
        self.scan_files.model().rowsRemoved.connect(self.persist_session)
        self.translator = i18n.start_timer(self)
        i18n.apply(self)
        # Se aceptan archivos sobre toda la pestaña, no solo sobre su lista.
        self.scan_drop = FileDropFilter(
            self.tabs.widget(0), self.accept_scan_drop, self.import_paths
        )
        self.pdf_drop = FileDropFilter(
            self.tabs.widget(1), self.accept_tool_drop, self.receive_tool_files
        )

    # Construye los controles de captura, previsualización y edición del escáner.
    def scanner_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        hero = self.label("Del papel a tu bolsillo.", "hero")
        hero.setWordWrap(False)
        layout.addWidget(hero)
        row = QHBoxLayout()
        row.addWidget(self.button("Importar fotos", self.import_scan))
        row.addWidget(self.button("Abrir webcam", self.camera))
        row.addWidget(self.button("Preparar salida", self.save_scan_pdf, True))
        layout.addLayout(row)
        layout.addWidget(
            self.label("Arrastra fotos o PDF aquí para añadir páginas.", "muted")
        )
        split = QSplitter()
        left = QWidget()
        column = QVBoxLayout(left)
        self.scan_files = self.file_list()
        self.scan_files.setMinimumHeight(100)
        self.scan_files.currentItemChanged.connect(self.preview_scan)
        self.scan_files.itemDoubleClicked.connect(lambda _: self.crop())
        column.addWidget(self.scan_files)
        column.addLayout(self.list_controls(self.scan_files))
        row = QHBoxLayout()
        row.addWidget(self.button("Ajustar bordes / color", self.crop))
        row.addWidget(self.button("Girar 90°", self.rotate))
        column.addLayout(row)
        split.addWidget(left)
        self.preview = QLabel("Selecciona una página para verla")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setObjectName("preview")
        self.preview.setMinimumSize(260, 180)
        split.addWidget(self.preview)
        layout.addWidget(split, 2)
        layout.addWidget(self.label("Mis documentos"))
        self.library_tabs = QTabWidget()
        self.internal_files = QListWidget()
        self.device_files = QListWidget()
        self.internal_files.itemDoubleClicked.connect(
            lambda item: self.library_menu(item, True)
        )
        self.device_files.itemDoubleClicked.connect(
            lambda item: self.library_menu(item, False)
        )
        for listing, internal in [
            (self.internal_files, True),
            (self.device_files, False),
        ]:
            listing.setContextMenuPolicy(Qt.CustomContextMenu)
            listing.customContextMenuRequested.connect(
                lambda point, w=listing, own=internal: self.library_menu(
                    w.itemAt(point), own
                )
            )
        self.library_tabs.addTab(self.internal_files, "Sin exportar")
        device = QWidget()
        area = QVBoxLayout(device)
        area.setContentsMargins(0, 0, 0, 0)
        row = QHBoxLayout()
        row.addWidget(self.button("Buscar PDF", self.search_device))
        row.addWidget(self.button("Elegir carpeta", self.choose_root))
        area.addLayout(row)
        area.addWidget(self.device_files)
        self.library_tabs.addTab(device, "Del dispositivo")
        layout.addWidget(self.library_tabs, 1)
        return widget

    # Construye el gestor de PDF y conecta las cuatro operaciones disponibles.
    def pdf_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.operation = QComboBox()
        self.operation.addItems(
            [
                "Unir varios PDF",
                "Separar PDF en páginas · ZIP",
                "PDF a imágenes JPG · ZIP",
                "Imágenes a PDF",
            ]
        )
        self.operation.currentIndexChanged.connect(self.operation_changed)
        layout.addWidget(self.operation)
        self.tool_hint = self.label(
            "Selecciona un archivo y usa las flechas para cambiar el orden."
        )
        layout.addWidget(self.tool_hint)
        layout.addWidget(
            self.label(
                "Arrastra aquí los archivos de la operación seleccionada.", "muted"
            )
        )
        row = QHBoxLayout()
        row.addWidget(self.button("Selecciona archivos", self.add_tools))
        row.addStretch()
        row.addWidget(QLabel(i18n.tr("Formato de papel")))
        self.pdf_format = self.format_box()
        row.addWidget(self.pdf_format)
        layout.addLayout(row)
        self.tool_files = self.file_list()
        layout.addWidget(self.tool_files, 1)
        layout.addLayout(self.list_controls(self.tool_files))
        layout.addWidget(self.button("Procesar", self.process_tools, True))
        return widget

    # Vacía la selección anterior para no mezclar tipos de archivo entre operaciones.
    def operation_changed(self):
        self.tool_files.clear()
        self.pdf_format.setEnabled(self.operation.currentIndex() == 3)

    # Actualiza el manifiesto de páginas con reemplazo atómico para poder reabrir la sesión.
    def persist_session(self, *_):
        if not hasattr(self, "manifest"):
            return
        # Atomic manifest updates preserve the previous list if writing is interrupted.
        staged = self.manifest.with_suffix(".tmp")
        staged.write_text(
            json.dumps([Path(p).name for p in self.paths(self.scan_files)]), "utf-8"
        )
        os.replace(staged, self.manifest)

    # Normaliza las fotos importadas y las incorpora a la lista de páginas.
    def import_scan(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            i18n.tr("Importar fotos"),
            "",
            "PDF / imágenes (*.pdf *.jpg *.jpeg *.png *.bmp *.webp *.tif *.tiff)",
        )
        if paths:
            self.import_paths([Path(path) for path in paths])

    def accept_scan_drop(self, paths):
        return not (self.worker and self.worker.isRunning()) and all(
            path.suffix.lower() in IMAGE_EXTENSIONS | {".pdf"} for path in paths
        )

    def accept_tool_drop(self, paths):
        if self.worker and self.worker.isRunning():
            return False
        index = self.operation.currentIndex()
        extensions = IMAGE_EXTENSIONS if index == 3 else {".pdf"}
        return all(path.suffix.lower() in extensions for path in paths) and (
            index not in (1, 2) or len(paths) == 1
        )

    def receive_tool_files(self, paths):
        # Separar/renderizar admite un PDF; unir e imágenes→PDF acumulan archivos.
        if not self.accept_tool_drop(paths):
            return
        if self.operation.currentIndex() in (1, 2):
            self.tool_files.clear()
        for path in paths:
            self.add_item(self.tool_files, path)

    def import_paths(self, paths):
        if not paths or not self.accept_scan_drop(paths):
            return
        imported = []

        def prepare(progress):
            imported.extend(core.import_scan_files(paths, self.session.name, progress))
            return ""

        # Detiene el temporizador y libera el dispositivo de cámara.
        def done(_):
            for path, label in imported:
                self.add_item(self.scan_files, path, label)
            if imported:
                self.scan_files.setCurrentRow(self.scan_files.count() - 1)
            self.persist_session()
            self.status.setText(i18n.tr("Listo"))

        self.run_job(prepare, done)

    # Abre la captura de cámara y añade las fotos obtenidas a la sesión.
    def camera(self):
        super().camera()
        self.persist_session()

    # Abre el editor de cuatro esquinas y conserva el resultado como una nueva imagen.
    def crop(self):
        super().crop()
        self.persist_session()

    # Gira la imagen seleccionada 90 grados y actualiza su previsualización.
    def rotate(self):
        super().rotate()
        self.persist_session()

    # Cambia el orden de una página; el orden visible será el orden exportado.
    def move(self, files, delta):
        super().move(files, delta)
        self.persist_session()

    # Abre la composición posterior al escaneo y prepara una copia en la biblioteca local.
    def save_scan_pdf(self):
        paths = self.need_images()
        if not paths:
            return
        editor = LayoutEditor(paths, self)
        if editor.exec() != QDialog.Accepted:
            return
        directory = self.drafts / uuid.uuid4().hex
        directory.mkdir()
        kind = editor.output.currentText()

        def prepare(progress):
            # Keep originals with the draft; later edits never depend on session files.
            images = directory / "originales"
            images.mkdir()
            copies = []
            for index, source in enumerate(paths):
                destination = images / f"{index:03}.jpg"
                shutil.copy2(source, destination)
                copies.append(str(destination))
            core.layout_pdf(copies, directory / "Documento.pdf", editor.specs, progress)
            if kind != "PDF":
                core.layout_images(
                    copies, directory / "imagenes", editor.specs, kind, progress
                )
            (directory / "salida.json").write_text(
                json.dumps({"kind": kind, "specs": editor.specs}), "utf-8"
            )
            return str(directory / "Documento.pdf")

        self.run_job(
            prepare,
            lambda path: (self.refresh_library(), self.export_draft(Path(path))),
        )

    # Muestra únicamente documentos completos que aún no tienen marca de exportación.
    def refresh_library(self):
        self.internal_files.clear()
        for file in sorted(self.drafts.glob("*/Documento.pdf")):
            if not (file.parent / ".exported").exists():
                name = file.parent / "nombre.txt"
                self.add_item(
                    self.internal_files,
                    file,
                    (
                        name.read_text("utf-8")
                        if name.exists()
                        else "Documento · " + file.parent.name[:8]
                    ),
                )

    # Pregunta el destino y marca como exportado solamente después de guardar con éxito.
    def export_draft(self, path):
        metadata = path.parent / "salida.json"
        kind = (
            json.loads(metadata.read_text("utf-8"))["kind"]
            if metadata.exists()
            else "PDF"
        )
        # An appended document must export the full PDF, never its old image subset.
        if (path.parent / ".extended").exists():
            kind = "PDF"
        if kind == "PDF":
            target = self.destination(
                i18n.tr("Guardar PDF: elige la carpeta de destino"), ".pdf"
            )
            if not target:
                return

            # Escribe el archivo seleccionado en el URI de destino concedido por Android.
            def export(progress):
                with core.atomic_output(target, [path]) as staged:
                    shutil.copyfile(path, staged)
                return target

        else:
            directory = QFileDialog.getExistingDirectory(
                self, i18n.tr("Elige dónde guardar las fotos")
            )
            if not directory:
                return
            # A fresh subfolder prevents accidental replacement of other image files.
            target = str(Path(directory) / ("Documento-" + uuid.uuid4().hex[:8]))

            # Escribe el archivo seleccionado en el URI de destino concedido por Android.
            def export(progress):
                shutil.copytree(path.parent / "imagenes", target)
                return target

        # Detiene el temporizador y libera el dispositivo de cámara.
        def done(result):
            (path.parent / ".exported").touch()
            self.refresh_library()
            self.remember_root(Path(result).parent)
            self.completed(result)

        # The previous worker may be emitting completed; wait for its finished event.
        from PySide6.QtCore import QTimer

        QTimer.singleShot(0, lambda: self.run_job(export, done))

    # Recupera las carpetas de búsqueda configuradas para este equipo.
    def roots(self):
        return json.loads(
            str(
                self.settings.value(
                    "roots",
                    json.dumps(
                        [str(Path.home() / "Documents"), str(Path.home() / "Downloads")]
                    ),
                )
            )
        )

    # Añade una carpeta a la búsqueda sin duplicar entradas existentes.
    def remember_root(self, root):
        roots = self.roots()
        if str(root) not in roots:
            roots.append(str(root))
        self.settings.setValue("roots", json.dumps(roots))

    # Pide al usuario una carpeta accesible y actualiza los resultados.
    def choose_root(self):
        directory = QFileDialog.getExistingDirectory(self, i18n.tr("Elegir carpeta"))
        if directory:
            self.remember_root(directory)
            self.search_device()

    # Busca PDF fuera del hilo gráfico para que la ventana siga respondiendo.
    def search_device(self):
        roots = self.roots()
        found = []

        def search(progress):
            found.extend(core.discover_pdfs(roots))
            return ""

        # Detiene el temporizador y libera el dispositivo de cámara.
        def done(_):
            self.device_files.clear()
            for path in found:
                self.add_item(self.device_files, path)
            self.status.setText(i18n.tr("Listo"))

        self.run_job(search, done)

    # Ofrece acciones sobre la ruta del documento seleccionado, no sobre su etiqueta visible.
    def library_menu(self, item, internal):
        if item is None or (self.worker and self.worker.isRunning()):
            return
        path = Path(item.data(Qt.UserRole))
        menu = QMenu(self)
        menu.addAction(i18n.tr("Ver PDF"), lambda: os.startfile(str(path)))
        menu.addAction(i18n.tr("Añadir hojas"), lambda: self.append_menu(path))
        if internal:
            menu.addAction(i18n.tr("Guardar PDF…"), lambda: self.export_draft(path))
        menu.addAction(
            i18n.tr("Cambiar nombre"), lambda: self.rename_document(path, internal)
        )
        menu.addAction(
            i18n.tr("Eliminar"), lambda: self.delete_document(path, internal)
        )
        from PySide6.QtGui import QCursor

        menu.exec(QCursor.pos())

    # Valida el nombre y evita reemplazar otro archivo al renombrar.
    def rename_document(self, path, internal):
        name, accepted = QInputDialog.getText(
            self, i18n.tr("Cambiar nombre"), i18n.tr("Nombre del documento")
        )
        if not accepted:
            return
        if (
            not name.strip()
            or any(char in name for char in '/\\:*?"<>|')
            or name.startswith(".")
        ):
            QMessageBox.warning(self, i18n.tr("Error"), i18n.tr("Nombre no válido"))
            return
        try:
            if internal:
                (path.parent / "nombre.txt").write_text(name.strip(), "utf-8")
                self.refresh_library()
            else:
                target = path.with_name(
                    name if name.lower().endswith(".pdf") else name + ".pdf"
                )
                if target.exists():
                    raise ValueError(i18n.tr("Nombre ya usado o no disponible"))
                path.rename(target)
                self.search_device()
        except (OSError, ValueError) as error:
            self.failed(str(error))

    # Pide confirmación; limita el borrado recursivo a una carpeta propia de la biblioteca.
    def delete_document(self, path, internal):
        if (
            QMessageBox.question(
                self,
                i18n.tr("Eliminar"),
                path.name,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            != QMessageBox.Yes
        ):
            return
        try:
            if internal:
                # Only delete a known child of the application's own library.
                if path.parent.parent.resolve() != self.drafts.resolve():
                    raise ValueError("Invalid library path")
                shutil.rmtree(path.parent)
                self.refresh_library()
            else:
                path.unlink()
                self.search_device()
        except OSError as error:
            self.failed(str(error))

    # Permite elegir entre añadir PDF existentes o las páginas actuales del escáner.
    def append_menu(self, target):
        menu = QMenu(self)
        menu.addAction(i18n.tr("Añadir PDF"), lambda: self.append_from_pdf(target))
        menu.addAction(
            i18n.tr("Añadir páginas del escáner"), lambda: self.append_from_scan(target)
        )
        from PySide6.QtGui import QCursor

        menu.exec(QCursor.pos())

    # Selecciona los documentos que se añadirán al PDF original.
    def append_from_pdf(self, target):
        paths, _ = QFileDialog.getOpenFileNames(
            self, i18n.tr("Añadir PDF"), "", "PDF (*.pdf)"
        )
        if paths:
            self.confirm_append(target, paths)

    # Compone primero las nuevas páginas; solo después solicita reemplazar el original.
    def append_from_scan(self, target):
        paths = self.need_images()
        if not paths:
            return
        editor = LayoutEditor(paths, self)
        if editor.exec() != QDialog.Accepted:
            return
        addition = Path(self.session.name) / (uuid.uuid4().hex + ".pdf")
        self.run_job(
            lambda progress: core.layout_pdf(paths, addition, editor.specs, progress),
            lambda _: self.confirm_append(target, [addition]),
        )

    # Presenta la advertencia explícita de sobrescritura antes de ejecutar la transacción.
    def confirm_append(self, target, additions):
        question = i18n.tr(
            "Se añadirán las páginas y se sobrescribirá el PDF original. Se conservará una copia de recuperación. ¿Continuar?"
        )
        if (
            QMessageBox.warning(
                self,
                i18n.tr("Añadir hojas"),
                question + "\n\n" + str(target),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            != QMessageBox.Yes
        ):
            return

        # Detiene el temporizador y libera el dispositivo de cámara.
        def done(result):
            if target.parent.parent == self.drafts:
                (target.parent / ".extended").touch()
            self.completed(result)

        from PySide6.QtCore import QTimer

        QTimer.singleShot(
            0,
            lambda: self.run_job(
                lambda progress: core.append_pdf(target, additions, progress), done
            ),
        )

    # Deshabilita acciones mientras trabaja el hilo y entrega resultados cuando este termina.
    def run_job(self, fn, on_success=None):
        if self.worker and self.worker.isRunning():
            return
        self.tabs.setEnabled(False)
        self.gear.setEnabled(False)
        self.status.setText(i18n.tr("Procesando…"))
        self.worker = Worker(fn)
        self.worker.progress.connect(self.status.setText)
        # Deliver the result only after QThread has stopped, allowing chained jobs.
        result = {}
        self.worker.completed.connect(lambda value: result.update(value=value))
        self.worker.failed.connect(self.failed)

        def finished():
            self.finish_job()
            if "value" in result:
                (on_success or self.completed)(result["value"])

        self.worker.finished.connect(finished)
        self.worker.start()

    # Despliega tema, permisos, idioma y ayuda sin un botón redundante de cierre.
    def settings_menu(self):
        menu = QMenu(self)
        dark = self.settings.value("dark", False, type=bool)
        menu.addAction(
            i18n.tr("Cambiar a modo claro" if dark else "Cambiar a modo noche"),
            self.toggle_theme,
        )
        menu.addAction(
            i18n.tr("Administración de permisos"),
            lambda: os.startfile("ms-settings:privacy-webcam"),
        )
        menu.addAction(i18n.tr("Idioma"), self.choose_language)
        menu.addAction(i18n.tr("¿Cómo funciona?"), self.help)
        menu.exec(self.gear.mapToGlobal(self.gear.rect().bottomLeft()))

    # Persiste el idioma seleccionado y actualiza la interfaz con el catálogo local.
    def choose_language(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(i18n.tr("Idioma"))
        layout = QVBoxLayout(dialog)
        choices = QComboBox()
        choices.addItems(i18n.NAMES)
        choices.setCurrentIndex(i18n.CODES.index(i18n.language))
        layout.addWidget(choices)
        notice = QLabel(
            i18n.tr("¿Falta tu idioma? Contacta conmigo en GitHub.")
            + '<br><a href="https://github.com/Brass-Ebort">github.com/Brass-Ebort</a>'
        )
        notice.setOpenExternalLinks(True)
        layout.addWidget(notice)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        if dialog.exec() == QDialog.Accepted:
            i18n.language = i18n.CODES[choices.currentIndex()]
            self.settings.setValue("language", i18n.language)
            self.settings.sync()
            i18n.apply(self)

    # Muestra instrucciones y límites reales del escaneo y la exportación.
    def help(self):
        QMessageBox.information(
            self,
            i18n.tr("¿Cómo funciona?"),
            i18n.tr(
                "Escanea o importa páginas, ajusta sus bordes y prepara la salida: papel, píxeles, escala y posición. En Mis documentos puedes añadir hojas a un PDF tras confirmar; queda una copia .recovery. Los PDF del dispositivo requieren permiso o elegir carpeta. Cada exportación pide destino. Procesamiento local; Android requiere Servicios de Google Play y una descarga inicial. Los pliegues fuertes y el texto oculto no se reconstruyen. Haz una copia antes de desinstalar. V3 — código disponible para uso no comercial."
            ),
        )

    # Impide cerrar durante una escritura y conserva preferencias y sesión.
    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            event.ignore()
            return
        self.persist_session()
        self.settings.sync()
        event.accept()
