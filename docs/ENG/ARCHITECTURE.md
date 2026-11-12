# Architecture and design decisions

## Android

- MainActivity.java owns tabs, settings, permissions, pickers and overwrite confirmations. Package identity is retained, but upgrading also requires the same signing certificate.
- ScanModel.java serializes operations on an ExecutorService and publishes results through LiveData to avoid concurrent writes.
- PdfTools.java uses PDFBox for merging/splitting and PDF creation, Android PdfRenderer for rasterization, and EXIF orientation for imported images.
- LayoutSpec.java stores page dimensions in PDF points, uniform scale and relative offsets. LayoutDialog.java previews those settings; DocumentOps.layout exports the same geometry. Rotating the sheet swaps its dimensions and output pixel dimensions, without rotating the original photo.
- DocumentOps.java handles replacement/recovery, discovery and rendered-photo selection.
- I18n.java loads an offline shared catalogue. A manual language overrides the system language; unsupported system languages fall back to English.
- The legal page is a local asset opened with JavaScript disabled. External legal references are handed to the browser only when selected.

## Windows

- launcher.py is the entry point. Its limited library-verification mode checks replacement separately from application functional tests.
- app.py supplies reusable controls, DirectShow camera capture, perspective cropping, styling and a Qt worker thread. main starts WindowV3.
- v3.py contains the current shell, persistent library, device-file management and append confirmation. Datos/preferencias.ini replaces registry-based settings.
- layout_editor.py provides per-page composition. core.py implements PDF/image operations and transactional output independently of the GUI.
- i18n.py preserves original catalogue keys so changing language is reversible.
- desktop.spec builds an onedir portable package with external DLLs and legal texts. The entire directory must be kept together. Information additional exposes the legal folder.

## Geometry

Coordinates use a top-left origin. Dimensions are PDF points and offsets are fractions of the page. The fit factor is `min(pageWidth/imageWidth, pageHeight/imageHeight) * scale`. The image is centered and then translated. PDF output flips the Y axis. Content outside the canvas is clipped without stretching the image. JPG/PNG canvas proportions follow the requested pixel dimensions, limited to 6000 pixels per side and 24 megapixels total.

## File integrity

Appending first creates a complete PDF in a temporary file in the same directory. The original file's size and modification time are checked for concurrent changes. A .recovery copy is created before replacement; failure to create that recovery copy aborts the replacement. Permissions and insufficient disk space can still prevent an operation and must be reported.

The .exported marker is written only after successful export. The .extended marker prevents an old subset of scan images being presented as the full appended PDF. Modifying a PDF invalidates digital signatures. This is a local library, not a multiuser database or an unlimited version history.

## Reading the source

Maintenance comments remain in the original source. CODE_GUIDE.html provides English line-by-line syntax explanations; the ESP edition provides Spanish explanations. Structural explanations are reading aids, not a proof of correctness. Algorithm-specific comments take precedence. Java comments and Python source comments are not shipped as executable instructions.
