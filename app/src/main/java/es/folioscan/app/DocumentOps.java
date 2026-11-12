package es.folioscan.app;

import android.graphics.*;
import com.tom_roush.pdfbox.pdmodel.*;
import com.tom_roush.pdfbox.pdmodel.common.PDRectangle;
import com.tom_roush.pdfbox.pdmodel.graphics.image.JPEGFactory;
import com.tom_roush.pdfbox.pdmodel.graphics.image.PDImageXObject;
import java.io.*;
import java.nio.file.*;
import java.util.*;

/** Transactional operations: fully build and validate before touching the original. */
public final class DocumentOps {
  /** Delete only a library directory selected by the owner; never follow symlinks. */
  public static boolean deleteTree(File dir) {
    boolean ok = true;
    if (!Files.isSymbolicLink(dir.toPath()) && dir.isDirectory()) {
      File[] children = dir.listFiles();
      if (children != null) for (File child : children) ok &= deleteTree(child);
    }
    return dir.delete() && ok;
  }

  // Crea la copia de recuperación y reemplaza el archivo con el resultado ya completo.
  public static void replace(File prepared, File target) throws IOException {
    File backup = new File(target.getPath() + ".recovery");
    if (target.exists())
      Files.copy(target.toPath(), backup.toPath(), StandardCopyOption.REPLACE_EXISTING);
    try {
      Files.move(
          prepared.toPath(),
          target.toPath(),
          StandardCopyOption.ATOMIC_MOVE,
          StandardCopyOption.REPLACE_EXISTING);
    } catch (AtomicMoveNotSupportedException error) {
      Files.move(prepared.toPath(), target.toPath(), StandardCopyOption.REPLACE_EXISTING);
    }
  }

  // Une las páginas en un temporal; el aviso de sobrescritura se gestiona en la interfaz.
  public static void append(File target, File addition) throws IOException {
    long modified = target.lastModified(), length = target.length();
    File staged = File.createTempFile(".append-", ".pdf", target.getParentFile());
    try {
      PdfTools.merge(Arrays.asList(target, addition), staged);
      try (PDDocument checked = PDDocument.load(staged)) {
        if (checked.getNumberOfPages() < 1) throw new IOException("Empty result");
      }
      if (target.lastModified() != modified || target.length() != length)
        throw new IOException("Original changed during processing");
      replace(staged, target);
    } finally {
      staged.delete();
    }
  }

  // Genera PDF e imágenes con la misma geometría empleada por la previsualización.
  public static void layout(File directory, LayoutSpec[] specs) throws IOException {
    File[] sources = ScanModel.images(directory);
    if (sources.length != specs.length) throw new IOException("Page count changed");
    File staged = File.createTempFile(".layout-", ".pdf", directory);
    File rendered = new File(directory, "rendered-" + UUID.randomUUID());
    if (!rendered.mkdir()) throw new IOException("Cannot create output folder");
    try (PDDocument pdf = new PDDocument()) {
      for (int i = 0; i < sources.length; i++) {
        LayoutSpec s = specs[i];
        s.validate();
        try (InputStream input = new FileInputStream(sources[i])) {
          PDImageXObject image = JPEGFactory.createFromStream(pdf, input);
          float[] box = s.box(image.getWidth(), image.getHeight());
          PDPage page = new PDPage(new PDRectangle(s.width, s.height));
          pdf.addPage(page);
          try (PDPageContentStream stream = new PDPageContentStream(pdf, page)) {
            stream.addRect(0, 0, s.width, s.height);
            stream.clip();
            stream.drawImage(image, box[0], s.height - box[1] - box[3], box[2], box[3]);
          }
        }
        // Image output uses the same geometry as PDF and the live preview.
        {
          Bitmap input = PdfTools.decode(sources[i]);
          Bitmap output = Bitmap.createBitmap(s.pixelsWide, s.pixelsHigh, Bitmap.Config.ARGB_8888);
          try {
            Canvas canvas = new Canvas(output);
            canvas.drawColor(Color.WHITE);
            // Uniform fitting also protects later photo exports of a PDF layout.
            float rasterScale=Math.min(s.pixelsWide/s.width,s.pixelsHigh/s.height);
            canvas.translate((s.pixelsWide-s.width*rasterScale)/2,(s.pixelsHigh-s.height*rasterScale)/2);
            canvas.scale(rasterScale,rasterScale);
            float[] b = s.box(input.getWidth(), input.getHeight());
            canvas.drawBitmap(
                input,
                null,
                new RectF(b[0], b[1], b[0] + b[2], b[1] + b[3]),
                new Paint(Paint.FILTER_BITMAP_FLAG));
            boolean png = s.output.equals("PNG");
            File file =
                new File(
                    rendered,
                    String.format(Locale.ROOT, "Pagina-%03d.%s", i + 1, png ? "png" : "jpg"));
            try (OutputStream out = new FileOutputStream(file)) {
              if (!output.compress(
                  png ? Bitmap.CompressFormat.PNG : Bitmap.CompressFormat.JPEG, 95, out))
                throw new IOException("Image export failed");
            }
          } finally {
            input.recycle();
            output.recycle();
          }
        }
      }
      pdf.save(staged);
      replace(staged, new File(directory, "Documento.pdf"));
      // A pointer is published only after the whole export succeeds.
      Files.write(
          new File(directory, "rendered.txt").toPath(),
          rendered.getName().getBytes(java.nio.charset.StandardCharsets.UTF_8));
    } finally {
      staged.delete();
    }
  }

  // Resuelve el conjunto de imágenes renderizadas; recurre a las originales si no hay otro.
  public static File[] exportImages(File directory) throws IOException {
    File pointer = new File(directory, "rendered.txt");
    if (pointer.isFile()) {
      String name =
          new String(Files.readAllBytes(pointer.toPath()), java.nio.charset.StandardCharsets.UTF_8);
      if (name.matches("rendered-[a-f0-9-]+")) {
        File[] files = new File(directory, name).listFiles();
        if (files != null && files.length > 0) {
          Arrays.sort(files);
          return files;
        }
      }
    }
    return ScanModel.images(directory);
  }

  // Busca PDF accesibles; la interfaz obtiene los permisos antes de llamar a esta operación.
  public static List<File> discover(File root) {
    List<File> found = new ArrayList<>();
    ArrayDeque<File> queue = new ArrayDeque<>();
    Set<String> seen = new HashSet<>();
    queue.add(root);
    while (!queue.isEmpty()) {
      File dir = queue.removeFirst();
      try {
        if (!seen.add(dir.getCanonicalPath())) continue;
      } catch (IOException e) {
        continue;
      }
      File[] children = dir.listFiles();
      if (children == null) continue;
      for (File file : children) {
        if (file.isDirectory()
            && !file.getName().startsWith(".")
            && !file.getPath().contains("/Android/data")
            && !file.getPath().contains("/Android/obb")) queue.add(file);
        else if (file.isFile() && file.getName().toLowerCase(Locale.ROOT).endsWith(".pdf"))
          found.add(file);
      }
    }
    found.sort(Comparator.comparing(File::getName, String.CASE_INSENSITIVE_ORDER));
    return found;
  }
}
