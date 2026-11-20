package es.folioscan.app;

import android.app.Application;
import android.graphics.*;
import android.net.Uri;
import android.provider.DocumentsContract;
import androidx.annotation.NonNull;
import androidx.lifecycle.AndroidViewModel;
import androidx.lifecycle.MutableLiveData;
import com.google.mlkit.vision.documentscanner.GmsDocumentScanningResult;
import java.io.*;
import java.text.SimpleDateFormat;
import java.util.*;
import java.util.concurrent.*;

public class ScanModel extends AndroidViewModel {
  final MutableLiveData<String> status = new MutableLiveData<>("");
  final ExecutorService worker = Executors.newSingleThreadExecutor();
  volatile boolean busy;
  final MutableLiveData<File> savedScan = new MutableLiveData<>();
  final MutableLiveData<java.util.List<DeviceDocument>> deviceFiles =
      new MutableLiveData<>(new ArrayList<>());

  // Isolate search from PDF/export work; a stalled filesystem cannot occupy that worker.
  private final ThreadPoolExecutor searchWorker = new ThreadPoolExecutor(
      1, 1, 0L, TimeUnit.MILLISECONDS, new ArrayBlockingQueue<>(1));
  private final android.os.Handler searchHandler = new android.os.Handler(android.os.Looper.getMainLooper());
  private Future<?> searchTask;
  private Runnable searchTimeout;
  private int searchGeneration;
  volatile boolean searching;
  private android.os.CancellationSignal searchSignal;
  private File lastSearchRoot;
  private Uri lastSearchFolder;
  interface Search { DocumentStore.Discovery run(android.os.CancellationSignal signal) throws Exception; }


  void discover(File root) {
    if(busy) return;
    lastSearchRoot=root;lastSearchFolder=null;
    startSearch(signal -> {
      DocumentOps.Discovery found=DocumentOps.discover(root,200,20000,10000);
      DocumentStore.Discovery result=new DocumentStore.Discovery();result.partial=found.partial;
      for(File file:found.files) result.files.add(new DeviceDocument(file));
      return result;
    });
  }
  void discoverFolder(Uri folder) {
    if(busy) return;
    lastSearchFolder=folder;lastSearchRoot=null;
    startSearch(signal -> DocumentStore.discover(getApplication().getContentResolver(),folder,signal));
  }
  void rediscover() {
    if(lastSearchFolder!=null) discoverFolder(lastSearchFolder);
    else if(lastSearchRoot!=null) discover(lastSearchRoot);
  }
  private void startSearch(Search search) {
    if (busy) return;
    searchSignal=new android.os.CancellationSignal();
    final android.os.CancellationSignal signal=searchSignal;
    busy = true;
    searching = true;
    final int generation = ++searchGeneration;
    deviceFiles.setValue(new ArrayList<>());
    status.setValue("Buscando PDF…");
    searchTimeout = () -> {
      if (generation != searchGeneration || !searching) return;
      cancelSearch();
      status.setValue("La búsqueda ha agotado el tiempo. Vuelve a intentarlo.");
    };
    searchHandler.postDelayed(searchTimeout, 15000);
    searchWorker.purge();
    try {
      searchTask = searchWorker.submit(() -> {
        List<DeviceDocument> files = new ArrayList<>();
        String message;
        try {
          DocumentStore.Discovery result = search.run(signal);
          files = result.files;
          message = result.partial ? "Búsqueda parcial: se ha alcanzado un límite o hay carpetas inaccesibles." : "Listo";
        } catch (Exception | OutOfMemoryError error) {
          message = "No se pudo completar la búsqueda. Comprueba el permiso de almacenamiento.";
        }
        final List<DeviceDocument> completed = files;
        final String outcome = message;
        searchHandler.post(() -> {
          // Cancelled/timed-out work must not overwrite a newer operation's state.
          if (generation != searchGeneration || !searching) return;
          searchHandler.removeCallbacks(searchTimeout);
          searching = false;
          busy = false;
          deviceFiles.setValue(completed);
          status.setValue(outcome);
        });
      });
    } catch (RejectedExecutionException error) {
      cancelSearch();
      status.setValue("La búsqueda ha agotado el tiempo. Vuelve a intentarlo.");
    }
  }

  void cancelSearch() {
    if (!searching) return;
    ++searchGeneration;
    if (searchTask != null) searchTask.cancel(true);
    if (searchSignal != null) searchSignal.cancel();
    if (searchTimeout != null) searchHandler.removeCallbacks(searchTimeout);
    searching = false;
    busy = false;
    status.setValue("Búsqueda cancelada");
  }

  void configureFolder(Uri tree) {
    if(busy) return;
    busy=true;status.setValue("Procesando…");
    worker.execute(() -> {
      try {
        Uri folder=DocumentStore.ensureFolder(getApplication().getContentResolver(),tree);
        searchHandler.post(() -> {
          getApplication().getSharedPreferences("MainActivity",0).edit().putString("documentFolder",folder.toString()).apply();
          busy=false;discoverFolder(folder);
        });
      } catch(Exception error) {
        searchHandler.post(() -> {busy=false;status.setValue("No se pudo abrir la carpeta. Autorízala de nuevo.");});
      }
    });
  }
  interface FileOperation { void run() throws Exception; }
  void mutateDevice(FileOperation operation) {
    if(busy) return;
    busy=true;status.setValue("Procesando…");
    worker.execute(() -> {
      try {
        operation.run();
        searchHandler.post(() -> {busy=false;status.setValue("Guardado");rediscover();});
      } catch(Exception error) {
        searchHandler.post(() -> {busy=false;status.setValue("Error: "+error.getMessage());});
      }
    });
  }
  void append(Uri target,Uri parent,File addition) {
    mutateDevice(() -> DocumentStore.append(getApplication(),target,parent,addition));
  }

  // Genera PDF e imágenes con la misma geometría empleada por la previsualización.
  void layout(File directory, LayoutSpec[] pages, Runnable finished) {
    if (busy) return;
    busy = true;
    status.setValue("Procesando…");
    worker.execute(
        () -> {
          try {
            DocumentOps.layout(directory, pages);
            busy = false;
            status.postValue("Guardado");
            new android.os.Handler(android.os.Looper.getMainLooper()).post(finished);
          } catch (Exception | OutOfMemoryError e) {
            busy = false;
            status.postValue("Error: " + e.getMessage());
          }
        });
  }

  // Une las páginas en un temporal; el aviso de sobrescritura se gestiona en la interfaz.
  void append(File target, File addition) {
    if (busy) return;
    busy = true;
    status.setValue("Procesando…");
    worker.execute(
        () -> {
          try {
            DocumentOps.append(target, addition);
            if (target.getParentFile().getParentFile().equals(root()))
              new File(target.getParentFile(), ".extended").createNewFile();
            busy = false;
            status.postValue("Guardado");
          } catch (Exception e) {
            busy = false;
            status.postValue("Error: " + e.getMessage());
          }
        });
  }

  final MutableLiveData<File> toolResult = new MutableLiveData<>();

  // Procesa la herramienta elegida en segundo plano y publica el resultado pendiente de guardar.
  void processPdf(String operation, List<Uri> inputs, String format) {
    if (busy) return;
    busy = true;
    status.setValue("Procesando archivos…");
    toolResult.setValue(null);
    worker.execute(
        () -> {
          try {
            File output = PdfTools.process(getApplication(), operation, inputs, format);
            toolResult.postValue(output);
            busy = false;
            status.postValue("Resultado listo. Pulsa Guardar resultado para elegir el destino.");
          } catch (Exception error) {
            busy = false;
            status.postValue(
                "No se pudo procesar: "
                    + (error.getMessage() == null
                        ? "archivo no compatible o protegido."
                        : error.getMessage()));
          } catch (OutOfMemoryError error) {
            busy = false;
            status.postValue("No hay memoria suficiente. Prueba con archivos más pequeños.");
          }
        });
  }

  public ScanModel(@NonNull Application app) {
    super(app);
    PdfTools.initialize(app);
  }

  File root() {
    File root = new File(getApplication().getFilesDir(), "documents");
    root.mkdirs();
    return root;
  }

  static File[] images(File dir) {
    File[] files = dir.listFiles((d, n) -> n.endsWith(".jpg"));
    if (files == null) return new File[0];
    Arrays.sort(files);
    return files;
  }

  // Copia los resultados del escáner a almacenamiento privado antes de ofrecer su edición.
  void save(GmsDocumentScanningResult result, String format) {
    busy = true;
    status.setValue("Guardando tus páginas…");
    worker.execute(
        () -> {
          File temporary = new File(root(), ".pending-" + UUID.randomUUID());
          try {
            if (result.getPages() == null || result.getPages().isEmpty())
              throw new IOException("No hay páginas");
            if (!temporary.mkdirs()) throw new IOException("No se pudo crear el documento");
            int i = 0;
            for (GmsDocumentScanningResult.Page page : result.getPages()) {
              try (InputStream in =
                      getApplication().getContentResolver().openInputStream(page.getImageUri());
                  OutputStream out =
                      new FileOutputStream(
                          new File(
                              temporary, String.format(Locale.ROOT, "Pagina-%03d.jpg", ++i)))) {
                copy(in, out);
              }
            }
            File pdf = new File(temporary, "Documento.pdf");
            if (!format.equals("Original"))
              PdfTools.imagesToPdf(images(temporary), pdf, format, false);
            else {
              if (result.getPdf() == null) throw new IOException("No se generó el PDF");
              try (InputStream in =
                      getApplication()
                          .getContentResolver()
                          .openInputStream(result.getPdf().getUri());
                  OutputStream out = new FileOutputStream(pdf)) {
                copy(in, out);
              }
            }
            String name =
                "Escaneo "
                    + new SimpleDateFormat("yyyy-MM-dd HH-mm-ss", Locale.ROOT).format(new Date());
            File destination = new File(root(), name);
            if (destination.exists())
              destination = new File(root(), name + "-" + System.currentTimeMillis());
            if (!temporary.renameTo(destination))
              throw new IOException("No se pudo finalizar el guardado");
            busy = false;
            status.postValue("Guardado");
            savedScan.postValue(destination);
          } catch (Exception e) {
            File[] files = temporary.listFiles();
            if (files != null) for (File file : files) file.delete();
            temporary.delete();
            busy = false;
            status.postValue(
                "No se pudo guardar. Comprueba el espacio libre y vuelve a intentarlo.");
          }
        });
  }

  // Copia los valores de composición para mantener ajustes independientes por página.
  static void copy(InputStream in, OutputStream out) throws IOException {
    if (in == null || out == null) throw new IOException("No se pudo abrir el archivo");
    byte[] buffer = new byte[32768];
    int n;
    while ((n = in.read(buffer)) != -1) out.write(buffer, 0, n);
  }

  // Escribe el archivo seleccionado en el URI de destino concedido por Android.
  void export(File source, Uri destination) {
    busy = true;
    status.setValue("Exportando…");
    worker.execute(
        () -> {
          String message;
          try {
            try (InputStream in = new FileInputStream(source);
                OutputStream out =
                    getApplication().getContentResolver().openOutputStream(destination, "wt")) {
              copy(in, out);
            }
            message = "Guardado";
            if (source.getParentFile().getParentFile().equals(root()))
              new File(source.getParentFile(), ".exported").createNewFile();
          } catch (Exception e) {
            message = "No se pudo exportar. Tu original sigue en la biblioteca.";
          }
          busy = false;
          status.postValue(message);
        });
  }

  // Crea una imagen por hoja en la carpeta autorizada y marca el documento al finalizar.
  void exportPhotos(File directory, Uri tree) {
    busy = true;
    status.setValue("Guardando fotos individuales…");
    worker.execute(
        () -> {
          int count = 0;
          String message;
          try {
            Uri parent =
                DocumentsContract.buildDocumentUriUsingTree(
                    tree, DocumentsContract.getTreeDocumentId(tree));
            for (File source : DocumentOps.exportImages(directory)) {
              Uri destination =
                  DocumentsContract.createDocument(
                      getApplication().getContentResolver(),
                      parent,
                      source.getName().endsWith(".png") ? "image/png" : "image/jpeg",
                      directory.getName() + "-" + source.getName());
              if (destination == null) throw new IOException("No se pudo crear la foto");
              try (InputStream in = new FileInputStream(source);
                  OutputStream out =
                      getApplication().getContentResolver().openOutputStream(destination)) {
                copy(in, out);
              }
              count++;
            }
            new File(directory, ".exported").createNewFile();
            message = "Guardado";
          } catch (Exception e) {
            message =
                "Se guardaron "
                    + count
                    + " fotos. No se pudo completar la exportación; los originales siguen en la"
                    + " biblioteca.";
          }
          busy = false;
          status.postValue(message);
        });
  }

  @Override
  protected void onCleared() {
    ++searchGeneration;
    searchHandler.removeCallbacksAndMessages(null);
    if(searchSignal!=null) searchSignal.cancel();
    searchWorker.shutdownNow();
    worker.shutdown();
  }
}
