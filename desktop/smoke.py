"""Offline packaged-application smoke test; does not access user documents."""


def run(report_path):
    import os, json, tempfile, zipfile, traceback
    from pathlib import Path

    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    result = {"ok": False}
    try:
        from PIL import Image
        from pypdf import PdfReader
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QSettings
        from app import configure_fonts
        from v3 import WindowV3 as Window
        import core

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            image = root / "image.png"
            Image.new("RGB", (400, 600), "white").save(image)
            core.images_to_pdf([image], root / "a.pdf", "A4")
            core.merge_pdfs([root / "a.pdf", root / "a.pdf"], root / "merged.pdf")
            assert len(PdfReader(root / "merged.pdf").pages) == 2
            core.split_pdf(root / "merged.pdf", root / "pages.zip")
            core.pdf_to_images(root / "merged.pdf", root / "images.zip")
            assert len(zipfile.ZipFile(root / "pages.zip").namelist()) == 2
            assert len(zipfile.ZipFile(root / "images.zip").namelist()) == 2
            core.rectify_image(
                image, root / "crop.jpg", [[0, 0], [1, 0], [1, 1], [0, 1]]
            )
            app = QApplication.instance() or QApplication([])
            app.setStyle("Fusion")
            configure_fonts()
            window = Window(
                QSettings(str(root / "settings.ini"), QSettings.IniFormat),
                data_root=root / "data",
            )
            window.show()
            app.processEvents()
            window.toggle_theme()
            app.processEvents()
            assert window.windowTitle() == 'FolioScan'
            assert window.library_tabs.count() == 2
            assert window.status.isHidden()
            window.tabs.setCurrentIndex(1)
            for index in range(4):
                window.operation.setCurrentIndex(index)
                assert window.pdf_format.isHidden() == (index != 3)
            window.operation.setCurrentIndex(0)
            from app import ASSETS
            assert (ASSETS / 'arrow-dark.png').is_file()
            assert (ASSETS / 'arrow-light.png').is_file()
            # La distribución final debe conservar las zonas de arrastre y el importador.
            assert window.accept_scan_drop([image,root/'a.pdf'])
            imported=core.import_scan_files([image,root/'merged.pdf'],root/'data/Sesion')
            assert len(imported)==3
            from PySide6.QtCore import QMimeData,QUrl,QPoint,QPointF,Qt
            from PySide6.QtGui import QDragEnterEvent,QDropEvent
            window.tabs.setCurrentIndex(1);app.processEvents()
            mime=QMimeData();mime.setUrls([QUrl.fromLocalFile(str(root/'a.pdf'))])
            target=window.tool_files.viewport()
            enter=QDragEnterEvent(QPoint(10,10),Qt.CopyAction,mime,Qt.LeftButton,Qt.NoModifier)
            app.sendEvent(target,enter);assert enter.isAccepted()
            drop=QDropEvent(QPointF(10,10),Qt.CopyAction,mime,Qt.LeftButton,Qt.NoModifier)
            app.sendEvent(target,drop);assert window.tool_files.count()==1
            core.append_pdf(root / 'a.pdf', [root / 'merged.pdf'])
            assert len(PdfReader(root / 'a.pdf').pages) == 3
            assert len(PdfReader(root / 'a.pdf.recovery').pages) == 1
            from layout_editor import LayoutEditor
            editor=LayoutEditor([str(image)],window)
            editor.output.setCurrentText('PNG')
            core.layout_pdf([image],root/'layout.pdf',editor.specs)
            core.layout_images([image],root/'images',editor.specs,'PNG')
            assert (root/'images/Pagina-001.png').is_file()
            import i18n
            for language in i18n.CODES:
                i18n.language=language;i18n.apply(window)
                assert window.tabs.tabText(1)==i18n.ROWS['Gestor de PDF'][language]
            editor.close()
            window.close()
            result = {
                "ok": True,
                "checks": [
                    "images_to_pdf",
                    "merge",
                    "split_zip",
                    "pdf_to_jpg_zip",
                    "perspective",
                    "Qt_window",
                    "theme",
                    "append_and_recovery",
                    "layout_pdf_png",
                    "11_languages",
                    "FolioScan_brand",
                    "drop_pdf_event",
                    "import_photo_and_pdf_pages",
                ],
            }
    except Exception:
        result["error"] = traceback.format_exc()
    Path(report_path).write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if not result["ok"]:
        raise SystemExit(1)
