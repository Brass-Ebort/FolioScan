"""Local document processing. Originals are read-only; outputs are atomic."""

from pathlib import Path
from contextlib import contextmanager
from io import BytesIO
import os
import tempfile
import zipfile
import shutil
import math
import uuid


# Construye un PDF nuevo, comprueba cambios externos y conserva el original como .recovery antes de reemplazarlo.
def append_pdf(target, additions, progress=lambda _: None):
    """Prepare a complete replacement, retain a recovery copy, then atomically swap.

    Confirmation belongs to the UI. This function never edits the PDF in place.
    A concurrent external change aborts the replacement instead of losing edits.
    """
    target = Path(target)
    before = (target.stat().st_mtime_ns, target.stat().st_size)
    fd, temporary = tempfile.mkstemp(
        prefix=".append-", suffix=".pdf", dir=target.parent
    )
    os.close(fd)
    staged = Path(temporary)
    try:
        merge_pdfs([target] + list(additions), staged, progress)
        if (target.stat().st_mtime_ns, target.stat().st_size) != before:
            raise ValueError("The original changed during processing. Try again.")
        shutil.copy2(target, str(target) + ".recovery")
        os.replace(staged, target)
    finally:
        staged.unlink(missing_ok=True)
    return str(target)


# Calcula el rectángulo de la imagen conservando proporciones; x e y son fracciones del tamaño de página.
def layout_box(spec, image_size):
    """Top-left coordinates shared with Android and the Qt preview."""
    width, height = spec["width"], spec["height"]
    iw, ih = image_size
    scale = min(width / iw, height / ih) * spec.get("scale", 1)
    w, h = iw * scale, ih * scale
    return (
        (width - w) / 2 + spec.get("x", 0) * width,
        (height - h) / 2 + spec.get("y", 0) * height,
        w,
        h,
    )


# Genera cada página con sus dimensiones y convierte el eje vertical de pantalla al de PDF.
def layout_pdf(paths, destination, specs, progress=lambda _: None):
    """Export the exact per-page placement shown by the layout editor."""
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.lib.utils import ImageReader

    if len(paths) != len(specs) or not paths:
        raise ValueError("Invalid page count")
    with atomic_output(destination, paths) as output:
        canvas = Canvas(str(output), pageCompression=1)
        for i, (path, spec) in enumerate(zip(paths, specs)):
            width, height = spec["width"], spec["height"]
            canvas.setPageSize((width, height))
            with normalized_image(path) as image:
                x, y, w, h = layout_box(spec, image.size)
                canvas.saveState()
                clip = canvas.beginPath()
                clip.rect(0, 0, width, height)
                canvas.clipPath(clip, stroke=0)
                stream = BytesIO()
                image.save(stream, "JPEG", quality=95)
                stream.seek(0)
                canvas.drawImage(ImageReader(stream), x, height - y - h, w, h)
                canvas.restoreState()
                canvas.showPage()
            progress(str(i + 1) + " / " + str(len(paths)))
        canvas.save()
    return str(destination)


# Rasteriza solo el lienzo final para limitar memoria incluso con ampliaciones grandes.
def layout_images(paths, directory, specs, kind="PNG", progress=lambda _: None):
    """Render to requested pixel dimensions with clipping and a white background."""
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    for i, (path, spec) in enumerate(zip(paths, specs)):
        width, height = int(spec["pixelsWide"]), int(spec["pixelsHigh"])
        if (
            min(width, height) < 64
            or max(width, height) > 6000
            or width * height > 24000000
        ):
            raise ValueError("Invalid image dimensions")
        with normalized_image(path) as image:
            x, y, w, h = layout_box(spec, image.size)
            sx = width / spec["width"]
            sy = height / spec["height"]
            # Image layout coordinates have the output aspect ratio, avoiding stretching.
            # Inverse mapping allocates only the final canvas, even at 400% zoom.
            ax, ay = image.width / (w * sx), image.height / (h * sy)
            result = image.transform(
                (width, height),
                Image.Transform.AFFINE,
                (ax, 0, -x * sx * ax, 0, ay, -y * sy * ay),
                Image.Resampling.BICUBIC,
                fillcolor="white",
            )
            result.save(
                target / f"Pagina-{i+1:03}.{kind.lower()}",
                format="JPEG" if kind == "JPG" else "PNG",
                quality=95,
            )
            result.close()
        progress(str(i + 1) + " / " + str(len(paths)))
    return str(target)


# Recorre las carpetas elegidas sin seguir enlaces simbólicos; omite directorios ocultos.
def discover_pdfs(roots):
    """Enumerate user-selected roots without following symlink loops or hidden dirs."""
    found = set()
    for root in roots:
        for directory, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = [
                name
                for name in dirs
                if not name.startswith(".")
                and not os.path.islink(Path(directory) / name)
            ]
            for name in files:
                if name.lower().endswith(".pdf"):
                    found.add(str(Path(directory) / name))
    return sorted(found, key=str.casefold)


from PIL import Image, ImageOps
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject
import pypdfium2 as pdfium


def import_scan_files(paths, directory, progress=lambda _: None):
    """Copia fotos y rasteriza PDF para editarlos como páginas del escáner.

    El lote se prepara antes de publicarlo; si falla, se eliminan solo sus
    temporales y no se altera la sesión ni los archivos originales.
    """
    directory = Path(directory)
    staged = Path(tempfile.mkdtemp(prefix=".import-", dir=directory))
    prepared, published = [], []
    try:
        for source in map(Path, paths):
            if source.suffix.lower() == ".pdf":
                reader(source)  # Rechaza PDF vacíos/protegidos antes de rasterizar.
                with pdfium.PdfDocument(str(source)) as document:
                    for index in range(len(document)):
                        page = document[index]
                        try:
                            scale = min(2.0, 3200 / max(page.get_size()))
                            bitmap = page.render(scale=scale)
                            try:
                                image = bitmap.to_pil().convert("RGB")
                                target = staged / (uuid.uuid4().hex + ".jpg")
                                try:
                                    image.save(target, quality=95)
                                finally:
                                    image.close()
                            finally:
                                bitmap.close()
                        finally:
                            page.close()
                        prepared.append((target, f"{source.name} · {index+1}"))
                        progress(f"{index+1} / {len(document)}")
            else:
                target = staged / (uuid.uuid4().hex + ".jpg")
                with normalized_image(source) as image:
                    image.save(target, quality=97)
                prepared.append((target, source.name))
        for source, label in prepared:
            target = directory / source.name
            os.replace(source, target)
            published.append((str(target), label))
        return published
    except Exception:
        for path, _ in published:
            Path(path).unlink(missing_ok=True)
        raise
    finally:
        shutil.rmtree(staged)


FORMATS = {
    f"A{i}": size
    for i, size in enumerate(
        [
            (841, 1189),
            (594, 841),
            (420, 594),
            (297, 420),
            (210, 297),
            (148, 210),
            (105, 148),
            (74, 105),
            (52, 74),
            (37, 52),
            (26, 37),
        ]
    )
}


# Convierte milímetros a puntos PDF (72 por pulgada) y adapta la orientación.
def page_size(fmt, image_size):
    w, h = image_size
    if fmt == "Original":
        return w * 72 / 150, h * 72 / 150
    if fmt not in FORMATS:
        raise ValueError("Formato de papel desconocido")
    pw, ph = (x * 72 / 25.4 for x in FORMATS[fmt])
    return (ph, pw) if w > h else (pw, ph)


# Encaja la imagen dentro de los márgenes sin deformarla.
def fit_box(image_size, paper_size, margin):
    w, h = image_size
    pw, ph = paper_size
    if min(w, h, pw - 2 * margin, ph - 2 * margin) <= 0:
        raise ValueError("Dimensiones no válidas")
    scale = min((pw - 2 * margin) / w, (ph - 2 * margin) / h)
    return (pw - w * scale) / 2, (ph - h * scale) / 2, w * scale, h * scale


@contextmanager
# Escribe en un temporal del mismo directorio y publica el resultado solo cuando se completa.
def atomic_output(destination, inputs=()):
    destination = Path(destination)
    if any(destination.resolve() == Path(p).resolve() for p in inputs):
        raise ValueError("Elige un nombre distinto al de los archivos originales.")
    if not destination.parent.is_dir():
        raise ValueError("La carpeta de destino no existe.")
    fd, temp = tempfile.mkstemp(
        prefix=".escaner-", suffix=destination.suffix, dir=destination.parent
    )
    os.close(fd)
    try:
        yield Path(temp)
        os.replace(temp, destination)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


# Abre el PDF y rechaza documentos vacíos o protegidos antes de procesarlos.
def reader(path):
    pdf = PdfReader(path)
    if pdf.is_encrypted:
        raise ValueError("El PDF está protegido. Utiliza una copia sin contraseña.")
    if not pdf.pages:
        raise ValueError("El PDF no contiene páginas.")
    return pdf


# Concatena páginas conservando texto y recursos del PDF, sin convertirlo en fotografías.
def merge_pdfs(paths, destination, progress=lambda _: None):
    if len(paths) < 2:
        raise ValueError("Selecciona al menos dos PDF.")
    with atomic_output(destination, paths) as output, PdfWriter() as writer:
        for i, path in enumerate(paths):
            pdf = reader(path)
            # Namespaces preserve fields with the same name across different PDFs.
            if pdf.get_fields():
                pdf.add_form_topname(f"documento_{i+1}")
            writer.append(pdf)
            progress(f"Uniendo archivo {i+1} de {len(paths)}")
        writer.write(output)
    return str(destination)


# Escribe un PDF por página dentro de un ZIP; conserva el orden del original.
def split_pdf(path, destination, progress=lambda _: None):
    pdf = reader(path)
    with atomic_output(destination, [path]) as output, zipfile.ZipFile(
        output, "w", zipfile.ZIP_DEFLATED
    ) as archive:
        for i, page in enumerate(pdf.pages):
            with PdfWriter() as writer:
                writer.add_page(page)
                # Restore fields referenced by widgets on the isolated page.
                if page.get("/Annots"):
                    writer.reattach_fields()
                data = BytesIO()
                writer.write(data)
                archive.writestr(f"Pagina-{i+1:03}.pdf", data.getvalue())
            progress(f"Separando página {i+1} de {len(pdf.pages)}")
    return str(destination)


# Renderiza cada página y añade su imagen al ZIP de salida.
def pdf_to_images(path, destination, progress=lambda _: None):
    reader(path)  # Explicit unsupported-password error before any output is written.
    with atomic_output(destination, [path]) as output, zipfile.ZipFile(
        output, "w", zipfile.ZIP_DEFLATED
    ) as archive, pdfium.PdfDocument(path) as pdf:
        for i in range(len(pdf)):
            page = pdf[i]
            try:
                scale = min(2.0, 3200 / max(page.get_size()))
                bitmap = page.render(scale=scale, rev_byteorder=True)
                try:
                    image = bitmap.to_pil().convert("RGB")
                    try:
                        data = BytesIO()
                        image.save(data, "JPEG", quality=95)
                        archive.writestr(f"Pagina-{i+1:03}.jpg", data.getvalue())
                    finally:
                        image.close()
                finally:
                    bitmap.close()
            finally:
                page.close()
            progress(f"Convirtiendo página {i+1} de {len(pdf)}")
    return str(destination)


# Aplica orientación EXIF y compone transparencias sobre blanco antes del procesamiento.
def normalized_image(path):
    with Image.open(path) as original:
        oriented = ImageOps.exif_transpose(original)
        if oriented.mode in ("RGBA", "LA") or "transparency" in oriented.info:
            rgba = oriented.convert("RGBA")
            image = Image.new("RGB", rgba.size, "white")
            image.paste(rgba, mask=rgba.getchannel("A"))
            rgba.close()
        else:
            image = oriented.convert("RGB")
        image.thumbnail((4000, 4000), Image.Resampling.LANCZOS)
        return image


# Convierte imágenes ordenadas a páginas PDF con el formato solicitado.
def images_to_pdf(paths, destination, fmt="A4", progress=lambda _: None):
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.lib.utils import ImageReader

    if not paths:
        raise ValueError("Selecciona al menos una imagen.")
    with atomic_output(destination, paths) as output:
        canvas = Canvas(str(output), pageCompression=1)
        for i, path in enumerate(paths):
            with normalized_image(path) as image:
                size = page_size(fmt, image.size)
                canvas.setPageSize(size)
                margin = 0 if fmt == "Original" else min(12, min(size) / 20)
                x, y, w, h = fit_box(image.size, size, margin)
                data = BytesIO()
                image.save(data, "JPEG", quality=95)
                data.seek(0)
                canvas.drawImage(ImageReader(data), x, y, width=w, height=h)
                canvas.showPage()
            progress(f"Añadiendo imagen {i+1} de {len(paths)}")
        canvas.save()
    return str(destination)


# Crea fotos individuales en el destino elegido sin modificar las imágenes de origen.
def export_photos(paths, directory, progress=lambda _: None):
    if not paths:
        raise ValueError("No hay páginas para exportar.")
    directory = Path(directory)
    target = directory / ("Escaneo-" + uuid.uuid4().hex[:8])
    staging = Path(tempfile.mkdtemp(prefix=".escaner-", dir=directory))
    try:
        for i, path in enumerate(paths):
            with normalized_image(path) as image:
                image.save(staging / f"Pagina-{i+1:03}.jpg", quality=95)
            progress(f"Guardando foto {i+1} de {len(paths)}")
        staging.rename(target)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return str(target)


# Propone cuatro bordes a partir de contornos; el usuario puede corregirlos manualmente.
def detect_corners(path):
    import cv2
    import numpy as np

    with normalized_image(path) as pil:
        image = np.array(pil)
    h, w = image.shape[:2]
    factor = min(1, 1200 / max(h, w))
    small = cv2.resize(image, None, fx=factor, fy=factor)
    gray = cv2.cvtColor(small, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 45, 140)
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8))
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    for contour in sorted(contours, key=cv2.contourArea, reverse=True)[:20]:
        polygon = cv2.approxPolyDP(contour, 0.025 * cv2.arcLength(contour, True), True)
        if (
            len(polygon) == 4
            and cv2.isContourConvex(polygon)
            and cv2.contourArea(polygon) > 0.12 * small.shape[0] * small.shape[1]
        ):
            points = polygon.reshape(4, 2).astype(float)
            points[:, 0] /= small.shape[1]
            points[:, 1] /= small.shape[0]
            # Order around the centre, starting at upper-left; avoids duplicate extrema.
            centre = points.mean(axis=0)
            points = points[
                np.argsort(
                    np.arctan2(points[:, 1] - centre[1], points[:, 0] - centre[0])
                )
            ]
            points = np.roll(points, -np.argmin(points.sum(axis=1)), axis=0)
            return points.tolist()
    return [[0.03, 0.03], [0.97, 0.03], [0.97, 0.97], [0.03, 0.97]]


# Valida las cuatro esquinas y aplica una homografía; no reconstruye texto oculto por pliegues.
def rectify_image(path, destination, corners, mode="Color"):
    import cv2
    import numpy as np

    with normalized_image(path) as image:
        rgb = np.array(image)
    h, w = rgb.shape[:2]
    points = np.asarray(corners, dtype=np.float32) * [w, h]
    points = points.astype(np.float32)
    if (
        not cv2.isContourConvex(points.astype(np.int32))
        or abs(cv2.contourArea(points)) < w * h * 0.01
    ):
        raise ValueError(
            "Coloca las cuatro esquinas en orden alrededor de la hoja, sin cruzarlas."
        )
    width = int(
        max(
            np.linalg.norm(points[1] - points[0]), np.linalg.norm(points[2] - points[3])
        )
    )
    height = int(
        max(
            np.linalg.norm(points[3] - points[0]), np.linalg.norm(points[2] - points[1])
        )
    )
    if min(width, height) < 20:
        raise ValueError("La selección es demasiado pequeña.")
    transform = cv2.getPerspectiveTransform(
        points,
        np.float32([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]]),
    )
    result = cv2.warpPerspective(
        rgb, transform, (width, height), borderValue=(255, 255, 255)
    )
    if mode == "Gris":
        result = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)
    elif mode == "Blanco y negro":
        gray = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)
        result = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 12
        )
    with Image.fromarray(result) as image:
        image.save(destination, "JPEG", quality=95)
    return str(destination)
