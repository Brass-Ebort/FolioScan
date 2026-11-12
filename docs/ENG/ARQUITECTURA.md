# Architecture and Design Decisions

## Android

- `MainActivity.java`: presentation, tabs, settings, permissions, file pickers, and confirmations. The package identifier is retained to support upgrades from V2.
- `ScanModel.java`: document library and sequential operations in an ExecutorService. Publishes results through LiveData and prevents concurrent writes.
- `PdfTools.java`: PDFBox for merging/splitting PDFs and PDF operations; PdfRenderer for images; EXIF orientation for photos.
- `LayoutSpec.java`: dimensions in points, uniform scaling, and relative positioning. `LayoutDialog.java` shows the preview; `DocumentOps.layout` exports the same geometry.
- `DocumentOps.java`: replacement and recovery, PDF search, and selection of the rendered photo set.
- `I18n.java`: shared local language catalog, without a remote translation service.

## Windows

- `launcher.py`: entry point; catches self-test errors without opening error dialogs.
- `app.py`: reusable widgets, camera, perspective correction, styling, and Qt worker. `main` launches `WindowV3`.
- `v3.py`: current interface, persistent library, device management, and confirmation when appending pages. `Datos/preferencias.ini` replaces the Windows registry for V3 settings storage.
- `layout_editor.py`: per-page composition; `core.py`: PDF, image, and transactional operations that can be tested without the interface.
- `i18n.py`: local translations. Retains the original control text so switching languages is reversible.
- `desktop.spec`: PyInstaller packaging. Excludes system DLLs and unrelated ICU libraries found on PATH that caused the QtCore error in V2.

## Geometry

The model uses a top-left origin, PDF points, and offsets expressed as fractions of the page. The fit is `min(pageWidth/imageWidth, pageHeight/imageHeight) × scale`. The image is centered and then offset. PDF output reverses the Y-axis when writing. Anything outside the canvas is clipped without changing the image's aspect ratio. For JPG/PNG, the canvas takes the aspect ratio of the requested pixel dimensions. Limits: 6,000 pixels per side and 24 megapixels in total.

## File Integrity

When appending pages, the complete PDF is built in a temporary file in the same directory. The operation verifies that the original file's size or modification time has not changed during processing. It then creates a `.recovery` copy and replaces the original. If creating the recovery copy fails, the operation fails before replacement, not afterward. File-system permissions or insufficient free space may prevent the operation; in that case, an error is reported.

The `.exported` marker is written only after export finishes. `.extended` prevents the old subset of rendered images from being offered as though it represented the expanded PDF. Modifying a PDF invalidates its digital signatures. This is a simple local library, not a multiuser database or version-control system.

## Comments

The source files contain comments covering methods, geometry, permissions, lifecycle, and transactions. `CODIGO_COMENTADO.html` adds an explanation of **every line**, including structural lines, without filling compilable source files with repetitive comments. It opens offline in any browser. Java comments are not included as text in the APK; Python comments are omitted when compiling bytecode. The guide is distributed with the source code, separately from the executable.
