# Architecture and Design Decisions

## Android

- `MainActivity.java`: presentation, tabs, settings, permissions, file pickers, and confirmation dialogs. The package identifier is retained to allow updates from V2.
- `ScanModel.java`: library and sequential operations in an ExecutorService. Publishes results through LiveData and prevents simultaneous writes.
- `PdfTools.java`: PDFBox for PDF merging/splitting and PDF operations; PdfRenderer for images; EXIF orientation for photos.
- `LayoutSpec.java`: dimensions in points, uniform scaling, and relative positioning. `LayoutDialog.java` displays the preview; `DocumentOps.layout` exports the same geometry.
- `DocumentOps.java`: replacement and recovery operations, PDF searching, and selection of the set of rendered photos.
- `I18n.java`: shared local translation catalog, with no remote translation service.

## Windows

- `launcher.py`: entry point; captures self-test errors without displaying error windows.
- `app.py`: reusable controls, camera, perspective cropping, styling, and Qt worker. `main` starts `WindowV3`.
- `v3.py`: current interface, persistent library, device management, and confirmation when appending pages. `Datos/preferencias.ini` replaces the registry as the settings store in V3.
- `layout_editor.py`: per-page composition; `core.py`: PDF, image, and transactional operations that can be tested without the interface.
- `i18n.py`: local translations. Preserves the controls' source text so language changes can be reversed.
- `desktop.spec`: PyInstaller packaging. Excludes system DLLs and unrelated ICU libraries found on PATH that caused the QtCore error in V2.

## Geometry

The model uses a top-left origin, PDF points, and offsets expressed as fractions of the page. Fitting is calculated as `min(pageWidth/imageWidth, pageHeight/imageHeight) × scale`. The image is centered and then offset. PDF output reverses the Y axis when writing. Anything outside the canvas is clipped without changing the image's aspect ratio. For JPG/PNG, the canvas adopts the aspect ratio of the requested pixel dimensions. Limit: 6,000 pixels per side and 24 megapixels in total.

## File Integrity

When appending pages, the complete PDF is built in a temporary file in the same directory. The operation checks whether the original's size or modification time has changed. It then creates a `.recovery` copy and replaces the original. If creation of the recovery copy fails, the operation stops before replacement, not afterward. File-system permissions or insufficient space may prevent the operation; an error is reported in that case.

The `.exported` marker is written only after export is complete. `.extended` prevents the old subset of images from being offered as though it represented the extended PDF. Modifying a PDF invalidates its digital signatures. This is a simple local library, not a multi-user database or version-control system.

## Comments

The source files contain comments about methods, geometry, permissions, lifecycle, and transactions. `CODIGO_COMENTADO.html` adds an explanation of **every line**, including structural lines, without filling compilable files with repetitive comments. It can be opened offline in any browser. Java comments are not included as text in the APK; Python comments are omitted during bytecode compilation. The guide is distributed alongside the source code, separately from the executable.
