import unittest
import tempfile
import zipfile
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageDraw
from reportlab.pdfgen.canvas import Canvas
from pypdf import PdfReader, PdfWriter
import pypdfium2 as pdfium
import core

ARTIFACTS = Path(__file__).parent / "qa"


class DocumentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ARTIFACTS.mkdir(exist_ok=True)
        cls.a = ARTIFACTS / "uno.pdf"
        cls.b = ARTIFACTS / "dos.pdf"
        for path, labels in [
            (cls.a, ["PRIMERA PAGINA", "SEGUNDA PAGINA"]),
            (cls.b, ["TERCERA PAGINA"]),
        ]:
            canvas = Canvas(str(path), pagesize=(595, 842))
            for label in labels:
                canvas.setFillColorRGB(0.08, 0.42, 0.36)
                canvas.rect(30, 742, 535, 65, fill=1, stroke=0)
                canvas.setFillColorRGB(1, 1, 1)
                canvas.setFont("Helvetica-Bold", 22)
                canvas.drawString(48, 765, label)
                canvas.setFillColorRGB(0, 0, 0)
                canvas.setFont("Helvetica", 14)
                canvas.drawString(
                    48, 700, "Texto seleccionable y proporciones conservadas."
                )
                canvas.rect(48, 600, 120, 60, fill=0)
                canvas.showPage()
            canvas.save()
        cls.photo = ARTIFACTS / "foto.png"
        image = Image.new("RGB", (900, 1300), "white")
        d = ImageDraw.Draw(image)
        d.rectangle((15, 15, 884, 1284), outline="black", width=8)
        d.rectangle((90, 130, 810, 270), fill="#2167B1")
        d.text((120, 330), "DOCUMENTO DE PRUEBA", fill="black")
        image.save(cls.photo)

    def test_merge_preserves_order_and_text(self):
        out = ARTIFACTS / "unido.pdf"
        core.merge_pdfs([self.a, self.b], out)
        pdf = PdfReader(out)
        self.assertEqual(len(pdf.pages), 3)
        for page, label in zip(pdf.pages, ["PRIMERA", "SEGUNDA", "TERCERA"]):
            self.assertIn(label, page.extract_text())

    def test_split_zip_keeps_pages(self):
        out = ARTIFACTS / "hojas.zip"
        core.split_pdf(self.a, out)
        with zipfile.ZipFile(out) as z:
            self.assertEqual(z.namelist(), ["Pagina-001.pdf", "Pagina-002.pdf"])
            for i, name in enumerate(z.namelist()):
                pdf = PdfReader(BytesIO(z.read(name)))
                self.assertEqual(len(pdf.pages), 1)
                self.assertIn(["PRIMERA", "SEGUNDA"][i], pdf.pages[0].extract_text())

    def test_render_jpg_dimensions_and_nonblank(self):
        out = ARTIFACTS / "imagenes.zip"
        core.pdf_to_images(self.a, out)
        with zipfile.ZipFile(out) as z:
            self.assertEqual(len(z.namelist()), 2)
            image = Image.open(BytesIO(z.read(z.namelist()[0])))
            self.assertEqual(image.size, (1190, 1684))
            self.assertLess(image.getpixel((100, 110))[0], 100)
            image.save(ARTIFACTS / "pdf-render.jpg")

    def test_images_to_pdf_all_sizes(self):
        for fmt in core.FORMATS:
            out = ARTIFACTS / (fmt + ".pdf")
            core.images_to_pdf([self.photo], out, fmt)
            page = PdfReader(out).pages[0]
            w, h = core.page_size(fmt, (900, 1300))
            self.assertAlmostEqual(float(page.mediabox.width), w, places=2)
            self.assertAlmostEqual(float(page.mediabox.height), h, places=2)
        core.images_to_pdf([self.photo, self.photo], ARTIFACTS / "fotos.pdf", "A4")
        self.assertEqual(len(PdfReader(ARTIFACTS / "fotos.pdf").pages), 2)
        with pdfium.PdfDocument(ARTIFACTS / "fotos.pdf") as pdf:
            page = pdf[0]
            bitmap = page.render(scale=1.3)
            bitmap.to_pil().save(ARTIFACTS / "fotos-preview.png")
            bitmap.close()
            page.close()

    def test_export_individual_photos(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(core.export_photos([self.photo, self.photo], folder))
            self.assertEqual(len(list(target.glob("*.jpg"))), 2)

    def test_protected_pdf_is_rejected_without_overwriting(self):
        protected = ARTIFACTS / "protegido.pdf"
        writer = PdfWriter()
        writer.add_blank_page(width=100, height=100)
        writer.encrypt("clave")
        writer.write(protected)
        writer.close()
        out = ARTIFACTS / "keep.zip"
        out.write_bytes(b"original")
        with self.assertRaisesRegex(ValueError, "protegido"):
            core.split_pdf(protected, out)
        self.assertEqual(out.read_bytes(), b"original")

    def test_cannot_overwrite_input(self):
        before = self.a.read_bytes()
        with self.assertRaises(ValueError):
            core.merge_pdfs([self.a, self.b], self.a)
        self.assertEqual(before, self.a.read_bytes())

    def test_corrupt_pdf_does_not_leave_output(self):
        path = ARTIFACTS / "roto.pdf"
        path.write_text("not pdf")
        target = ARTIFACTS / "no-debe-existir.pdf"
        with self.assertRaises(Exception):
            core.merge_pdfs([self.a, path], target)
        self.assertFalse(target.exists())

    def test_alpha_composites_to_white(self):
        path = ARTIFACTS / "transparente.png"
        Image.new("RGBA", (100, 100), (0, 0, 0, 0)).save(path)
        with core.normalized_image(path) as image:
            self.assertEqual(image.getpixel((0, 0)), (255, 255, 255))

    def test_rectify_and_bad_corners(self):
        output = ARTIFACTS / "recortada.jpg"
        corners = core.detect_corners(self.photo)
        self.assertEqual(len(corners), 4)
        core.rectify_image(self.photo, output, [[0, 0], [1, 0], [1, 1], [0, 1]])
        with Image.open(output) as image:
            self.assertEqual(image.size, (900, 1300))
        with self.assertRaises(ValueError):
            core.rectify_image(self.photo, output, [[0, 0], [1, 1], [1, 0], [0, 1]])


if __name__ == "__main__":
    unittest.main(verbosity=2)
