package es.folioscan.app;

import android.content.Context;
import android.graphics.*;
import android.graphics.pdf.PdfRenderer;
import android.net.Uri;
import android.os.ParcelFileDescriptor;
import androidx.exifinterface.media.ExifInterface;
import com.tom_roush.pdfbox.android.PDFBoxResourceLoader;
import com.tom_roush.pdfbox.io.MemoryUsageSetting;
import com.tom_roush.pdfbox.multipdf.PDFMergerUtility;
import com.tom_roush.pdfbox.pdmodel.*;
import com.tom_roush.pdfbox.pdmodel.common.PDRectangle;
import com.tom_roush.pdfbox.pdmodel.graphics.image.JPEGFactory;
import com.tom_roush.pdfbox.pdmodel.graphics.image.PDImageXObject;
import java.io.*;
import java.util.*;
import java.util.zip.*;

public final class PdfTools {
  private static File scratchDirectory;

  private PdfTools() {}

  // Inicializa los recursos de PDFBox y configura su directorio temporal.
  public static void initialize(Context context) {
    PDFBoxResourceLoader.init(context);
    scratchDirectory = context.getCacheDir();
  }

  private static MemoryUsageSetting memory() {
    return MemoryUsageSetting.setupTempFileOnly().setTempDir(scratchDirectory);
  }

  // Copia las entradas a caché y ejecuta la conversión sin modificar los originales.
  public static File process(Context context, String operation, List<Uri> uris, String format)
      throws IOException {
    initialize(context);
    if (uris.isEmpty()) throw new IOException("Selecciona al menos un archivo.");
    File job = new File(context.getCacheDir(), "pdf-" + UUID.randomUUID());
    if (!job.mkdirs()) throw new IOException("No se pudo crear el archivo temporal.");
    ArrayList<File> files = new ArrayList<>();
    File output =
        new File(
            job,
            operation.equals("split")
                ? "Paginas.zip"
                : operation.equals("render") ? "Imagenes.zip" : "Documento.pdf");
    boolean success = false;
    try {
      for (Uri uri : uris) {
        File file = new File(job, "entrada-" + files.size());
        files.add(file);
        try (InputStream in = context.getContentResolver().openInputStream(uri);
            OutputStream out = new FileOutputStream(file)) {
          ScanModel.copy(in, out);
        }
      }
      if (operation.equals("merge")) merge(files, output);
      else if (operation.equals("split")) split(files.get(0), output);
      else if (operation.equals("render")) render(files.get(0), output);
      else if (operation.equals("images"))
        imagesToPdf(files.toArray(new File[0]), output, format, true);
      else throw new IOException("Operación desconocida.");
      success = true;
      return output;
    } catch (com.tom_roush.pdfbox.pdmodel.encryption.InvalidPasswordException error) {
      throw new IOException("El PDF está protegido. Usa una copia sin contraseña.", error);
    } finally {
      for (File file : files) file.delete();
      if (!success) {
        output.delete();
        job.delete();
      }
    }
  }

  // Concatena las páginas PDF conservando recursos y texto.
  public static void merge(List<File> files, File output) throws IOException {
    if (files.size() < 2) throw new IOException("Selecciona al menos dos PDF.");
    PDFMergerUtility merger = new PDFMergerUtility();
    try (PDDocument destination = new PDDocument(memory())) {
      for (File file : files)
        try (PDDocument source = PDDocument.load(file, memory())) {
          check(source);
          merger.appendDocument(destination, source);
        }
      destination.save(output);
    }
  }

  private static void check(PDDocument doc) throws IOException {
    if (doc.isEncrypted())
      throw new IOException("Este PDF está protegido. Usa una copia sin contraseña.");
    if (doc.getNumberOfPages() == 0) throw new IOException("El PDF no contiene páginas.");
  }

  // Introduce un PDF independiente por página dentro del ZIP de salida.
  public static void split(File source, File output) throws IOException {
    try (PDDocument doc = PDDocument.load(source, memory());
        ZipOutputStream zip = new ZipOutputStream(new FileOutputStream(output))) {
      check(doc);
      for (int i = 0; i < doc.getNumberOfPages(); i++) {
        zip.putNextEntry(new ZipEntry(String.format(Locale.ROOT, "Pagina-%03d.pdf", i + 1)));
        try (PDDocument one = new PDDocument()) {
          PDPage original = doc.getPage(i);
          PDPage page = one.importPage(original);
          page.setResources(original.getResources());
          page.setCropBox(original.getCropBox());
          page.setMediaBox(original.getMediaBox());
          page.setRotation(original.getRotation());
          one.save(
              new FilterOutputStream(zip) {
                @Override
                public void close() throws IOException {
                  flush();
                }
              });
        }
        zip.closeEntry();
      }
    }
  }

  // Convierte cada página a imagen con resolución acotada para controlar la memoria.
  public static void render(File source, File output) throws IOException {
    try (ParcelFileDescriptor fd =
            ParcelFileDescriptor.open(source, ParcelFileDescriptor.MODE_READ_ONLY);
        PdfRenderer renderer = new PdfRenderer(fd);
        ZipOutputStream zip = new ZipOutputStream(new FileOutputStream(output))) {
      for (int i = 0; i < renderer.getPageCount(); i++)
        try (PdfRenderer.Page page = renderer.openPage(i)) {
          float scale = Math.min(2.0f, 3200f / Math.max(page.getWidth(), page.getHeight()));
          Bitmap bitmap =
              Bitmap.createBitmap(
                  Math.max(1, Math.round(page.getWidth() * scale)),
                  Math.max(1, Math.round(page.getHeight() * scale)),
                  Bitmap.Config.ARGB_8888);
          try {
            bitmap.eraseColor(Color.WHITE);
            page.render(bitmap, null, null, PdfRenderer.Page.RENDER_MODE_FOR_PRINT);
            zip.putNextEntry(new ZipEntry(String.format(Locale.ROOT, "Pagina-%03d.jpg", i + 1)));
            if (!bitmap.compress(Bitmap.CompressFormat.JPEG, 95, zip))
              throw new IOException("No se pudo convertir la página.");
            zip.closeEntry();
          } finally {
            bitmap.recycle();
          }
        }
    }
  }

  // Lee una imagen con muestreo de resolución y corrige su orientación EXIF.
  static Bitmap decode(File file) throws IOException {
    BitmapFactory.Options options = new BitmapFactory.Options();
    options.inJustDecodeBounds = true;
    BitmapFactory.decodeFile(file.getPath(), options);
    options.inSampleSize = 1;
    while (Math.max(options.outWidth, options.outHeight) / options.inSampleSize > 3200)
      options.inSampleSize *= 2;
    options.inJustDecodeBounds = false;
    Bitmap image = BitmapFactory.decodeFile(file.getPath(), options);
    if (image == null) throw new IOException("Formato de imagen no compatible. Utiliza JPG o PNG.");
    Matrix matrix = new Matrix();
    int orientation;
    try {
      orientation = new ExifInterface(file).getAttributeInt(ExifInterface.TAG_ORIENTATION, 1);
    } catch (IOException e) {
      orientation = 1;
    }
    switch (orientation) {
      case 2:
        matrix.setScale(-1, 1);
        break;
      case 3:
        matrix.setRotate(180);
        break;
      case 4:
        matrix.setRotate(180);
        matrix.postScale(-1, 1);
        break;
      case 5:
        matrix.setRotate(90);
        matrix.postScale(-1, 1);
        break;
      case 6:
        matrix.setRotate(90);
        break;
      case 7:
        matrix.setRotate(-90);
        matrix.postScale(-1, 1);
        break;
      case 8:
        matrix.setRotate(-90);
        break;
    }
    if (!matrix.isIdentity()) {
      Bitmap rotated =
          Bitmap.createBitmap(image, 0, 0, image.getWidth(), image.getHeight(), matrix, true);
      if (rotated != image) image.recycle();
      image = rotated;
    }
    if (image.hasAlpha()) {
      Bitmap white =
          Bitmap.createBitmap(image.getWidth(), image.getHeight(), Bitmap.Config.RGB_565);
      Canvas canvas = new Canvas(white);
      canvas.drawColor(Color.WHITE);
      canvas.drawBitmap(image, 0, 0, null);
      image.recycle();
      image = white;
    }
    return image;
  }

  // Convierte la lista de imágenes en un documento PDF ordenado.
  public static void imagesToPdf(File[] files, File output, String format, boolean normalize)
      throws IOException {
    try (PDDocument pdf = new PDDocument(memory())) {
      for (File file : files) {
        PDImageXObject image;
        if (normalize) {
          Bitmap bitmap = decode(file);
          try {
            image = JPEGFactory.createFromImage(pdf, bitmap, 0.95f);
          } finally {
            bitmap.recycle();
          }
        } else
          try (InputStream stream = new FileInputStream(file)) {
            image = JPEGFactory.createFromStream(pdf, stream);
          }
        int[] size =
            format.equals("Original")
                ? new int[] {
                  Math.max(1, Math.round(image.getWidth() * 72f / 150)),
                  Math.max(1, Math.round(image.getHeight() * 72f / 150))
                }
                : PageFormats.points(format, image.getWidth() > image.getHeight());
        int margin = format.equals("Original") ? 0 : Math.min(12, Math.min(size[0], size[1]) / 20);
        float[] box = PageFit.fit(image.getWidth(), image.getHeight(), size[0], size[1], margin);
        PDPage page = new PDPage(new PDRectangle(size[0], size[1]));
        pdf.addPage(page);
        try (PDPageContentStream stream = new PDPageContentStream(pdf, page)) {
          stream.drawImage(image, box[0], box[1], box[2] - box[0], box[3] - box[1]);
        }
      }
      pdf.save(output);
    }
  }
}
