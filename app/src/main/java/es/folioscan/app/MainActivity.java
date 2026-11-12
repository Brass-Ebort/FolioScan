package es.folioscan.app;

import android.app.AlertDialog;
import android.content.*;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Bundle;
import android.view.*;
import android.widget.*;
import androidx.activity.ComponentActivity;
import androidx.activity.result.*;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.core.content.FileProvider;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.lifecycle.ViewModelProvider;
import com.google.mlkit.vision.documentscanner.*;
import java.io.File;
import java.util.*;

public class MainActivity extends ComponentActivity {
  private int INK, ACCENT, PAPER, CARD, MUTED, SOFT;
  private boolean dark;
  private int libraryTab;
  private String appendTarget;
  private ActivityResultLauncher<String[]> appendPicker;
  private ActivityResultLauncher<String[]> storagePermissions;
  private int tab = 0;
  private ScanModel model;
  private LinearLayout list;
  private TextView status;
  private Button scan;
  private String pendingExport;
  private String scanFormat = "A4", operation = "merge", pendingToolExport;
  private ActivityResultLauncher<String[]> toolPicker;
  private ActivityResultLauncher<String> toolPdfExport, toolZipExport;
  private Button saveTool;
  private ActivityResultLauncher<IntentSenderRequest> scannerLauncher;
  private ActivityResultLauncher<String> pdfExport;
  private ActivityResultLauncher<Uri> photosExport;

  @Override
  // Restaura preferencias, registra resultados del sistema y construye la interfaz.
  public void onCreate(Bundle saved) {
    dark = getPreferences(0).getBoolean("dark", false);
    setTheme(dark ? R.style.DarkTheme : R.style.AppTheme);
    super.onCreate(saved);
    I18n.load(this);
    model = new ViewModelProvider(this).get(ScanModel.class);
    if (saved != null) {
      appendTarget = saved.getString("appendTarget");
      libraryTab = saved.getInt("libraryTab");
    }
    if (saved != null) {
      pendingExport = saved.getString("export");
      scanFormat = saved.getString("format", "A4");
      tab = saved.getInt("tab");
      operation = saved.getString("operation", "merge");
      pendingToolExport = saved.getString("toolExport");
    }
    scannerLauncher =
        registerForActivityResult(
            new ActivityResultContracts.StartIntentSenderForResult(),
            result -> {
              model.busy = false;
              if (result.getResultCode() == RESULT_OK) {
                GmsDocumentScanningResult pages =
                    GmsDocumentScanningResult.fromActivityResultIntent(result.getData());
                if (pages != null) model.save(pages, scanFormat);
                else model.status.setValue("No se recibieron páginas. Puedes volver a intentarlo.");
              } else {
                appendTarget = null;
                model.status.setValue("Escaneo cancelado");
              }
            });
    pdfExport =
        registerForActivityResult(
            new ActivityResultContracts.CreateDocument("application/pdf"),
            uri -> {
              if (uri != null && pendingExport != null)
                model.export(new File(pendingExport, "Documento.pdf"), uri);
              pendingExport = null;
            });
    photosExport =
        registerForActivityResult(
            new ActivityResultContracts.OpenDocumentTree(),
            uri -> {
              if (uri != null && pendingExport != null)
                model.exportPhotos(new File(pendingExport), uri);
              pendingExport = null;
            });
    toolPicker =
        registerForActivityResult(
            new ActivityResultContracts.OpenMultipleDocuments(),
            uris -> {
              if (uris.isEmpty()) return;
              if ((operation.equals("split") || operation.equals("render")) && uris.size() != 1) {
                message("Selecciona un solo PDF para esta operación.");
                return;
              }
              if (operation.equals("merge") && uris.size() < 2) {
                message("Selecciona al menos dos PDF.");
                return;
              }
              for (Uri uri : uris)
                try {
                  getContentResolver()
                      .takePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION);
                } catch (SecurityException ignored) {
                }
              confirmOrder(new ArrayList<>(uris));
            });
    toolPdfExport =
        registerForActivityResult(
            new ActivityResultContracts.CreateDocument("application/pdf"), this::exportTool);
    toolZipExport =
        registerForActivityResult(
            new ActivityResultContracts.CreateDocument("application/zip"), this::exportTool);
    appendPicker =
        registerForActivityResult(
            new ActivityResultContracts.OpenMultipleDocuments(),
            uris -> {
              if (!uris.isEmpty() && appendTarget != null) prepareAppend(new ArrayList<>(uris));
              else appendTarget = null;
            });
    storagePermissions =
        registerForActivityResult(
            new ActivityResultContracts.RequestMultiplePermissions(),
            result -> {
              if (result.containsValue(true)) searchDevice();
            });
    buildUi();
    model.status.observe(
        this,
        message -> {
          status.setText(I18n.t(message));
          if (scan != null) scan.setEnabled(!model.busy);
          updateTool();
          refresh();
        });
    model.toolResult.observe(this, file -> updateTool());
    model.deviceFiles.observe(this, files -> refresh());
    model.savedScan.observe(
        this,
        dir -> {
          if (dir != null) {
            model.savedScan.setValue(null);
            editLayout(dir);
          }
        });
  }

  @Override
  // Conserva selecciones y operaciones pendientes durante una recreación de Android.
  protected void onSaveInstanceState(Bundle out) {
    out.putString("appendTarget", appendTarget);
    out.putInt("libraryTab", libraryTab);
    out.putString("export", pendingExport);
    out.putString("format", scanFormat);
    out.putInt("tab", tab);
    out.putString("operation", operation);
    out.putString("toolExport", pendingToolExport);
    super.onSaveInstanceState(out);
  }

  private int dp(int value) {
    return Math.round(value * getResources().getDisplayMetrics().density);
  }

  private TextView text(String value, int size, int color, boolean bold) {
    TextView view = new TextView(this);
    view.setText(I18n.t(value));
    view.setTextSize(size);
    view.setTextColor(color);
    if (bold) view.setTypeface(null, Typeface.BOLD);
    view.setPadding(0, dp(4), 0, dp(6));
    return view;
  }

  private GradientDrawable background(int color, int radius) {
    GradientDrawable drawable = new GradientDrawable();
    drawable.setColor(color);
    drawable.setCornerRadius(dp(radius));
    return drawable;
  }

  private Button button(String title, boolean primary, Runnable action) {
    Button button = new Button(this);
    button.setText(I18n.t(title));
    button.setAllCaps(false);
    button.setTextSize(16);
    button.setTextColor(primary ? (dark ? Color.BLACK : Color.WHITE) : ACCENT);
    button.setBackground(background(primary ? ACCENT : SOFT, 16));
    button.setPadding(dp(16), dp(8), dp(16), dp(8));
    LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(-1, dp(56));
    params.setMargins(0, dp(8), 0, dp(8));
    button.setLayoutParams(params);
    button.setOnClickListener(v -> action.run());
    return button;
  }

  private void styleTab(Button button, boolean active) {
    styleTab(button, active, false);
  }

  private void styleTab(Button button, boolean active, boolean mainNavigation) {
    int fill = Color.parseColor(active ? (dark ? (mainNavigation ? "#101B2B" : "#102C50") : "#174A86") : (dark ? "#365678" : "#DCEAFF"));
    // La pestaña principal activa queda abierta por abajo, como una ficha.
    GradientDrawable shape = new GradientDrawable() {
      @Override public void draw(android.graphics.Canvas canvas) {
        super.draw(canvas);
        if (active && mainNavigation) {
          android.graphics.Paint paint = new android.graphics.Paint();
          paint.setColor(fill);
          android.graphics.Rect bounds = getBounds();
          canvas.drawRect(bounds.left + dp(1), bounds.bottom - dp(1), bounds.right - dp(1), bounds.bottom, paint);
        }
      }
    };
    shape.setColor(fill);
    shape.setStroke(dp(1), MUTED);
    button.setBackground(shape);
    button.setTextColor(active || dark ? Color.WHITE : INK);
    button.setSelected(active);
    button.setTypeface(null, active ? Typeface.BOLD : Typeface.NORMAL);
    button.setTextSize(13);
    button.setPadding(dp(4), 0, dp(4), 0);
  }

  // Construye la pantalla con pestañas compactas, respetando tema y márgenes del sistema.
  private void buildUi() {
    INK = Color.parseColor(dark ? "#F1F6FC" : "#17334F");
    ACCENT = Color.parseColor(dark ? "#8EC5FF" : "#2167B1");
    PAPER = Color.parseColor(dark ? "#101B2B" : "#F3F7FC");
    CARD = Color.parseColor(dark ? "#1B2D44" : "#FFFFFF");
    MUTED = Color.parseColor(dark ? "#BACCE0" : "#506782");
    SOFT = Color.parseColor(dark ? "#2D4663" : "#DFEBF8");
    scan = null;
    list = null;
    saveTool = null;
    ScrollView scroll = new ScrollView(this);
    scroll.setFillViewport(true);
    scroll.setBackgroundColor(PAPER);
    LinearLayout body = new LinearLayout(this);
    body.setOrientation(LinearLayout.VERTICAL);
    body.setPadding(dp(24), dp(20), dp(24), dp(24));
    scroll.addView(body);
    ViewCompat.setOnApplyWindowInsetsListener(
        scroll,
        (view, insets) -> {
          androidx.core.graphics.Insets bars =
              insets.getInsets(WindowInsetsCompat.Type.systemBars());
          view.setPadding(bars.left, bars.top, bars.right, bars.bottom);
          return insets;
        });
    Button settings = button("⚙", false, this::settings);
    settings.setContentDescription(I18n.t("Ajustes"));
    LinearLayout tabs = new LinearLayout(this);
    Button scanTab =
        button(
            "Escáner",
            tab == 0,
            () -> {
              tab = 0;
              buildUi();
            });
    Button pdfTab =
        button(
            "Gestor de PDF",
            tab == 1,
            () -> {
              tab = 1;
              buildUi();
            });
    styleTab(scanTab, tab == 0, true);
    styleTab(pdfTab, tab == 1, true);
    settings.setPadding(0, 0, 0, 0);
    LinearLayout.LayoutParams gearParams = new LinearLayout.LayoutParams(dp(48), dp(48));
    gearParams.setMarginEnd(dp(12));
    tabs.addView(settings, gearParams);
    tabs.addView(scanTab, new LinearLayout.LayoutParams(0, dp(48), 1));
    tabs.addView(pdfTab, new LinearLayout.LayoutParams(0, dp(48), 1));
    body.addView(tabs);
    // El título respira bajo la navegación, también al cambiar al gestor PDF.
    View tabSpacing = new View(this);
    body.addView(tabSpacing, new LinearLayout.LayoutParams(-1, dp(20)));
    status = text(model.status.getValue() == null ? "" : model.status.getValue(), 14, ACCENT, false);
    status.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);
    if (tab == 1) {
      body.addView(text("Tus PDF,\na tu manera.", 34, INK, true));

      body.addView(button("Unir varios PDF", false, () -> pick("merge")));
      body.addView(button("Separar PDF en páginas · ZIP", false, () -> pick("split")));
      body.addView(button("PDF a imágenes JPG · ZIP", false, () -> pick("render")));
      body.addView(button("Imágenes a PDF", false, () -> pick("images")));
      body.addView(status);
      saveTool =
          button(
              "Guardar resultado…",
              true,
              () -> {
                File result = model.toolResult.getValue();
                if (result == null || model.busy) return;
                pendingToolExport = result.getPath();
                if (result.getName().endsWith(".zip")) toolZipExport.launch(result.getName());
                else toolPdfExport.launch(result.getName());
              });
      body.addView(saveTool);
      updateTool();
      body.addView(
          text("Selecciona un archivo y usa las flechas para cambiar el orden.", 13, MUTED, false));
      setContentView(scroll);
      return;
    }
    TextView headline = text("Del papel a tu bolsillo.", 26, INK, true);
    headline.setSingleLine(true);
    headline.setAutoSizeTextTypeUniformWithConfiguration(
        14, 26, 1, android.util.TypedValue.COMPLEX_UNIT_SP);
    body.addView(headline);

    LinearLayout hero = new LinearLayout(this);
    hero.setOrientation(LinearLayout.VERTICAL);
    hero.setPadding(dp(20), dp(16), dp(20), dp(16));
    hero.setBackground(background(CARD, 24));
    LinearLayout.LayoutParams hp = new LinearLayout.LayoutParams(-1, -2);
    hp.setMargins(0, dp(24), 0, dp(16));
    body.addView(hero, hp);
    hero.addView(text("Una hoja o un documento entero", 21, INK, true));
    hero.addView(
        text(
            "Captura hasta 50 páginas. Revisa los bordes, gira, ordena y mejora cada imagen antes"
                + " de guardar.",
            15,
            INK,
            false));

    scan = button("＋  Escanear hojas", true, this::startScan);
    hero.addView(scan);
    scan.setEnabled(!model.busy);
    body.addView(status);
    body.addView(text("Mis documentos", 25, INK, true));
    addLibraryTabs(body);
    list = new LinearLayout(this);
    list.setOrientation(LinearLayout.VERTICAL);
    body.addView(list);
    setContentView(scroll);
    refresh();
  }

  // Solicita la interfaz de escaneo de Google Play y limita la sesión a 50 páginas.
  private void startScan() {
    if (model.busy) return;
    scanFormat = "Original";
    model.busy = true;
    scan.setEnabled(false);
    status.setText(I18n.t("Abriendo cámara…"));
    GmsDocumentScannerOptions options =
        new GmsDocumentScannerOptions.Builder()
            .setGalleryImportAllowed(true)
            .setPageLimit(50)
            .setResultFormats(
                GmsDocumentScannerOptions.RESULT_FORMAT_JPEG,
                GmsDocumentScannerOptions.RESULT_FORMAT_PDF)
            .setScannerMode(GmsDocumentScannerOptions.SCANNER_MODE_FULL)
            .build();
    GmsDocumentScanning.getClient(options)
        .getStartScanIntent(this)
        .addOnSuccessListener(
            sender -> {
              scannerLauncher.launch(new IntentSenderRequest.Builder(sender).build());
            })
        .addOnFailureListener(
            error -> {
              model.busy = false;
              if (scan != null) scan.setEnabled(true);
              new I18n.Builder(this)
                  .setTitle("No se pudo abrir el escáner")
                  .setMessage(
                      "Conéctate a Internet para la primera descarga y comprueba que Servicios de"
                          + " Google Play esté actualizado. Después vuelve a intentarlo.\n\n"
                          + "Detalle: "
                          + error.getLocalizedMessage())
                  .setPositiveButton("Entendido", null)
                  .show();
            });
  }

  // Reconstruye la lista de documentos visibles según la pestaña de biblioteca.
  private void refresh() {
    if (list == null) return;
    list.removeAllViews();
    if (libraryTab == 1) {
      refreshDevice();
      return;
    }
    File[] documents =
        model
            .root()
            .listFiles(
                file ->
                    file.isDirectory()
                        && !file.getName().startsWith(".")
                        && new File(file, "Documento.pdf").isFile()
                        && !new File(file, ".exported").exists());
    if (documents == null || documents.length == 0) {
      list.addView(
          text(
              "Tu biblioteca está lista.\nEscanea tu primera hoja para empezar.",
              16,
              MUTED,
              false));
      return;
    }
    Arrays.sort(
        documents, (left, right) -> Long.compare(right.lastModified(), left.lastModified()));
    for (File dir : documents) {
      LinearLayout card = new LinearLayout(this);
      card.setOrientation(LinearLayout.VERTICAL);
      card.setPadding(dp(18), dp(12), dp(18), dp(12));
      card.setBackground(background(CARD, 18));
      LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(-1, -2);
      params.setMargins(0, dp(8), 0, dp(8));
      list.addView(card, params);
      card.addView(text(dir.getName(), 18, INK, true));
      card.addView(
          text(new File(dir, ".extended").exists() ? "PDF" : "PDF + JPG / PNG", 13, ACCENT, false));
      card.addView(button("Abrir / guardar / compartir", false, () -> options(dir)));
    }
  }

  // Abre las acciones del documento interno seleccionado.
  private void options(File dir) {
    if (model.busy) {
      Toast.makeText(this, I18n.t("Espera a que termine el guardado"), Toast.LENGTH_SHORT).show();
      return;
    }
    new I18n.Builder(this)
        .setTitle(dir.getName())
        .setItems(
            new String[] {
              "Ver PDF",
              "Guardar PDF…",
              "Guardar fotos individuales…",
              "Compartir PDF",
              "Compartir imágenes",
              "Cambiar nombre",
              "Eliminar",
              "Añadir hojas",
              "Preparar salida"
            },
            (dialog, which) -> {
              switch (which) {
                case 0:
                  openPdf(dir);
                  break;
                case 1:
                  pendingExport = dir.getPath();
                  pdfExport.launch(dir.getName() + ".pdf");
                  break;
                case 2:
                  if (new File(dir, ".extended").exists()) {
                    message("El PDF ampliado conserva sus páginas. Exporta el PDF completo.");
                    break;
                  }
                  pendingExport = dir.getPath();
                  photosExport.launch(null);
                  break;
                case 3:
                  share(dir, false);
                  break;
                case 4:
                  share(dir, true);
                  break;
                case 5:
                  rename(dir);
                  break;
                case 6:
                  delete(dir);
                  break;
                case 7:
                  addPages(new File(dir, "Documento.pdf"));
                  break;
                case 8:
                  if (!new File(dir, ".extended").exists()) editLayout(dir);
                  else message("El PDF ampliado conserva sus páginas. Exporta el PDF completo.");
                  break;
              }
            })
        .show();
  }

  private Uri uri(File file) {
    return FileProvider.getUriForFile(this, getPackageName() + ".files", file);
  }

  // Entrega al visor externo un URI temporal con permiso de lectura.
  private void openPdf(File dir) {
    Intent intent =
        new Intent(Intent.ACTION_VIEW)
            .setDataAndType(uri(new File(dir, "Documento.pdf")), "application/pdf")
            .addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
    try {
      startActivity(intent);
    } catch (ActivityNotFoundException e) {
      new I18n.Builder(this)
          .setMessage(
              "No hay un visor PDF instalado. Puedes guardar el PDF o compartirlo desde el menú.")
          .setPositiveButton("Entendido", null)
          .show();
    }
  }

  // Comparte únicamente los archivos elegidos mediante permisos de lectura limitados.
  private void share(File dir, boolean photos) {
    ArrayList<Uri> files = new ArrayList<>();
    if (photos && new File(dir, ".extended").exists()) {
      message("El PDF ampliado conserva sus páginas. Exporta el PDF completo.");
      return;
    }
    if (photos) {
      try {
        for (File file : DocumentOps.exportImages(dir)) files.add(uri(file));
      } catch (java.io.IOException e) {
        message("Error");
        return;
      }
    } else files.add(uri(new File(dir, "Documento.pdf")));
    if (files.isEmpty()) return;
    Intent intent =
        new Intent(photos ? Intent.ACTION_SEND_MULTIPLE : Intent.ACTION_SEND)
            .setType(photos ? "image/*" : "application/pdf");
    if (photos) intent.putParcelableArrayListExtra(Intent.EXTRA_STREAM, files);
    else intent.putExtra(Intent.EXTRA_STREAM, files.get(0));
    ClipData clips = ClipData.newUri(getContentResolver(), "Escaneo", files.get(0));
    for (int i = 1; i < files.size(); i++) clips.addItem(new ClipData.Item(files.get(i)));
    intent.setClipData(clips);
    intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
    startActivity(Intent.createChooser(intent, "Compartir documento"));
  }

  // Valida el nombre antes de cambiar la carpeta del documento.
  private void rename(File dir) {
    EditText input = new EditText(this);
    input.setSingleLine(true);
    input.setText(dir.getName());
    input.setSelectAllOnFocus(true);
    AlertDialog dialog =
        new I18n.Builder(this)
            .setTitle("Nombre del documento")
            .setView(input)
            .setNegativeButton("Cancelar", null)
            .setPositiveButton("Guardar", null)
            .create();
    dialog.setOnShowListener(
        v ->
            dialog
                .getButton(AlertDialog.BUTTON_POSITIVE)
                .setOnClickListener(
                    b -> {
                      String name = input.getText().toString().trim();
                      if (name.isEmpty()
                          || name.startsWith(".")
                          || name.length() > 80
                          || name.contains("/")
                          || name.contains("\\")) {
                        input.setError(I18n.t("Nombre no válido"));
                        return;
                      }
                      if (name.equals(dir.getName())) {
                        dialog.dismiss();
                        return;
                      }
                      File target = new File(model.root(), name);
                      if (target.exists() || !dir.renameTo(target)) {
                        input.setError(I18n.t("Nombre ya usado o no disponible"));
                        return;
                      }
                      refresh();
                      dialog.dismiss();
                    }));
    dialog.show();
  }

  // Pide confirmación antes de borrar los archivos internos del documento.
  private void delete(File dir) {
    new I18n.Builder(this)
        .setTitle("¿Eliminar este documento?")
        .setMessage(
            "Se borrarán el PDF y las fotos de la biblioteca. Las copias exportadas se conservan.")
        .setNegativeButton("Cancelar", null)
        .setPositiveButton(
            "Eliminar",
            (d, w) -> {
              boolean ok = DocumentOps.deleteTree(dir);
              refresh();
              if (!ok)
                Toast.makeText(this, "No se pudieron borrar todos los archivos", Toast.LENGTH_LONG)
                    .show();
            })
        .show();
  }

  private void message(String value) {
    new I18n.Builder(this).setMessage(value).setPositiveButton("Entendido", null).show();
  }

  // Abre el panel lateral de ajustes; tocar fuera o volver lo cierra.
  private void settings() {
    if (model.busy) {
      message("Espera a que termine la operación actual.");
      return;
    }
    android.app.Dialog drawer = new android.app.Dialog(this);
    drawer.requestWindowFeature(Window.FEATURE_NO_TITLE);
    LinearLayout panel = new LinearLayout(this);
    panel.setOrientation(LinearLayout.VERTICAL);
    panel.setPadding(dp(20), dp(36), dp(20), dp(24));
    panel.setBackgroundColor(CARD);
    panel.addView(text("⚙  Configuración", 24, INK, true));
    panel.addView(
        button(
            dark ? "☀  Cambiar a modo claro" : "☾  Cambiar a modo noche",
            false,
            () -> {
              getPreferences(0).edit().putBoolean("dark", !dark).apply();
              drawer.dismiss();
              recreate();
            }));
    panel.addView(
        button(
            "Administración de permisos",
            false,
            () -> {
              drawer.dismiss();
              startActivity(
                  new Intent(
                      android.provider.Settings.ACTION_APPLICATION_DETAILS_SETTINGS,
                      Uri.parse("package:" + getPackageName())));
            }));
    panel.addView(
        button(
            "¿Cómo funciona?",
            false,
            () -> {
              drawer.dismiss();
              showInfo();
            }));
    panel.addView(
        button(
            "Idioma",
            false,
            () -> {
              drawer.dismiss();
              chooseLanguage();
            }));
    // El contenido puede desplazarse en pantallas pequeñas sin ocultar el pie.
    View spacer = new View(this);
    panel.addView(spacer, new LinearLayout.LayoutParams(1, 0, 1));
    String version;
    try { version = getPackageManager().getPackageInfo(getPackageName(), 0).versionName; }
    catch (android.content.pm.PackageManager.NameNotFoundException e) { version = "3.2"; }
    panel.addView(text("FolioScan · v" + version, 12, MUTED, false));
    addFooter(panel);
    ScrollView settingsScroll = new ScrollView(this);
    settingsScroll.setFillViewport(true);
    settingsScroll.addView(panel);
    drawer.setContentView(settingsScroll);
    Window window = drawer.getWindow();
    if (window != null) {
      window.setBackgroundDrawableResource(android.R.color.transparent);
      window.setGravity(Gravity.START | Gravity.TOP);
      window.setLayout(
          Math.min(dp(330), getResources().getDisplayMetrics().widthPixels - dp(32)), -1);
    }
    drawer.show();
    if (window != null)
      window.setLayout(
          Math.min(dp(330), getResources().getDisplayMetrics().widthPixels - dp(32)), -1);
  }

  private void pick(String action) {
    if (model.busy) {
      message("Espera a que termine la operación actual.");
      return;
    }
    operation = action;
    toolPicker.launch(new String[] {action.equals("images") ? "image/*" : "application/pdf"});
  }

  private void exportTool(Uri uri) {
    if (uri != null && pendingToolExport != null) model.export(new File(pendingToolExport), uri);
    pendingToolExport = null;
  }

  private void updateTool() {
    if (saveTool != null) {
      saveTool.setVisibility(model.toolResult.getValue() == null ? View.GONE : View.VISIBLE);
      saveTool.setEnabled(!model.busy);
    }
  }

  private String name(Uri uri) {
    try (android.database.Cursor cursor =
        getContentResolver()
            .query(
                uri,
                new String[] {android.provider.OpenableColumns.DISPLAY_NAME},
                null,
                null,
                null)) {
      if (cursor != null && cursor.moveToFirst()) return cursor.getString(0);
    } catch (Exception ignored) {
    }
    return "Archivo";
  }

  private void confirmOrder(ArrayList<Uri> uris) {
    LinearLayout panel = new LinearLayout(this);
    panel.setOrientation(LinearLayout.VERTICAL);
    panel.setPadding(dp(16), dp(4), dp(16), dp(8));
    panel.addView(
        text("Selecciona un archivo y usa las flechas para cambiar el orden.", 14, MUTED, false));
    ArrayList<String> names = new ArrayList<>();
    for (Uri uri : uris) names.add(name(uri));
    ArrayAdapter<String> adapter =
        new ArrayAdapter<>(this, android.R.layout.simple_list_item_single_choice, names);
    ListView choices = new ListView(this);
    choices.setChoiceMode(ListView.CHOICE_MODE_SINGLE);
    choices.setAdapter(adapter);
    panel.addView(choices, new LinearLayout.LayoutParams(-1, dp(240)));
    choices.setItemChecked(0, true);
    LinearLayout actions = new LinearLayout(this);
    for (int direction : new int[] {-1, 1}) {
      Button move =
          button(
              direction < 0 ? "↑ Subir" : "↓ Bajar",
              false,
              () -> {
                int selected = choices.getCheckedItemPosition(), next = selected + direction;
                if (selected >= 0 && next >= 0 && next < uris.size()) {
                  Collections.swap(uris, selected, next);
                  Collections.swap(names, selected, next);
                  adapter.notifyDataSetChanged();
                  choices.setItemChecked(next, true);
                }
              });
      actions.addView(move, new LinearLayout.LayoutParams(0, dp(52), 1));
    }
    panel.addView(actions);
    new I18n.Builder(this)
        .setTitle(I18n.t("Selecciona archivos") + " · " + uris.size())
        .setView(panel)
        .setNegativeButton("Cancelar", null)
        .setPositiveButton(
            "Procesar",
            (d, w) ->
                model.processPdf(
                    operation, new ArrayList<>(uris), "Original"))
        .show();
  }

  // Añade el agradecimiento y el enlace al perfil indicado por el autor.
  private void addFooter(LinearLayout body) {
    TextView thanks = text("Gracias por descargar la aplicación.", 11, MUTED, false);
    body.addView(thanks);
    TextView link = text("github.com/Brass-Ebort", 11, ACCENT, false);
    link.setOnClickListener(
        v ->
            startActivity(
                new Intent(Intent.ACTION_VIEW, Uri.parse("https://github.com/Brass-Ebort"))));
    body.addView(link);
  }

  // Guarda uno de los once idiomas y recrea la interfaz con la nueva selección.
  private void chooseLanguage() {
    new I18n.Builder(this)
        .setTitle(
            I18n.t("Idioma") + " · " + I18n.t("¿Falta tu idioma? Contacta conmigo en GitHub."))
        .setItems(
            I18n.NAMES,
            (d, index) -> {
              getPreferences(0).edit().putString("language", I18n.CODES[index]).apply();
              recreate();
            })
        .setNegativeButton("Cancelar", null)
        .show();
  }

  private void addLibraryTabs(LinearLayout body) {
    LinearLayout tabs = new LinearLayout(this);
    for (int index = 0; index < 2; index++) {
      final int selected = index;
      Button b =
          button(
              index == 0 ? "Sin exportar" : "Del dispositivo",
              libraryTab == index,
              () -> {
                libraryTab = selected;
                buildUi();
              });
      styleTab(b, libraryTab == index);
      tabs.addView(b, new LinearLayout.LayoutParams(0, dp(48), 1));
    }
    body.addView(tabs);
  }

  // Solicita permisos si faltan y busca en el almacenamiento compartido accesible.
  private void searchDevice() {
    if (android.os.Build.VERSION.SDK_INT >= 30
        && !android.os.Environment.isExternalStorageManager()) {
      new I18n.Builder(this)
          .setMessage("Se necesita permiso para buscar PDF en el almacenamiento compartido.")
          .setPositiveButton(
              "Autorizar",
              (d, w) -> {
                try {
                  startActivity(
                      new Intent(
                          android.provider.Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION,
                          Uri.parse("package:" + getPackageName())));
                } catch (ActivityNotFoundException e) {
                  startActivity(
                      new Intent(
                          android.provider.Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION));
                }
              })
          .setNegativeButton("Cancelar", null)
          .show();
      return;
    }
    if (android.os.Build.VERSION.SDK_INT < 30
        && checkSelfPermission(android.Manifest.permission.READ_EXTERNAL_STORAGE)
            != android.content.pm.PackageManager.PERMISSION_GRANTED) {
      storagePermissions.launch(
          new String[] {
            android.Manifest.permission.READ_EXTERNAL_STORAGE,
            android.Manifest.permission.WRITE_EXTERNAL_STORAGE
          });
      return;
    }
    model.discover(android.os.Environment.getExternalStorageDirectory());
  }

  // Muestra los PDF encontrados con su carpeta para distinguir nombres repetidos.
  private void refreshDevice() {
    list.addView(button("Buscar PDF", false, this::searchDevice));
    List<File> files = model.deviceFiles.getValue();
    if (files == null || files.isEmpty()) {
      list.addView(text("No hay documentos.", 14, MUTED, false));
      return;
    }
    for (File file : files) {
      if (!file.isFile()) continue;
      Button b = button(file.getName(), false, () -> deviceMenu(file));
      list.addView(b);
      list.addView(text(file.getParent(), 11, MUTED, false));
    }
  }

  // Gestiona un PDF del almacenamiento compartido sin importarlo a la biblioteca.
  private void deviceMenu(File file) {
    new I18n.Builder(this)
        .setTitle(file.getName())
        .setItems(
            new String[] {"Ver PDF", "Añadir hojas", "Compartir PDF", "Cambiar nombre", "Eliminar"},
            (d, which) -> {
              if (which == 0) {
                try {
                  startActivity(
                      new Intent(Intent.ACTION_VIEW)
                          .setDataAndType(uri(file), "application/pdf")
                          .addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION));
                } catch (ActivityNotFoundException e) {
                  message("No hay un visor PDF instalado.");
                }
              }
              if (which == 1) addPages(file);
              if (which == 2)
                startActivity(
                    Intent.createChooser(
                        new Intent(Intent.ACTION_SEND)
                            .setType("application/pdf")
                            .putExtra(Intent.EXTRA_STREAM, uri(file))
                            .addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION),
                        I18n.t("Compartir PDF")));
              if (which == 3) {
                EditText name = new EditText(this);
                name.setSingleLine(true);
                name.setText(file.getName());
                new I18n.Builder(this)
                    .setTitle("Cambiar nombre")
                    .setView(name)
                    .setNegativeButton("Cancelar", null)
                    .setPositiveButton(
                        "Guardar",
                        (dialog, w) -> {
                          String value = name.getText().toString().trim();
                          if (value.isEmpty()
                              || value.contains("/")
                              || value.contains("\\")
                              || value.startsWith(".")) {
                            message("Error");
                            return;
                          }
                          if (!value.toLowerCase(Locale.ROOT).endsWith(".pdf")) value += ".pdf";
                          File target = new File(file.getParentFile(), value);
                          if (target.exists() || !file.renameTo(target)) message("Error");
                          else searchDevice();
                        })
                    .show();
              }
              if (which == 4)
                new I18n.Builder(this)
                    .setTitle("Eliminar")
                    .setMessage(file.getName())
                    .setNegativeButton("Cancelar", null)
                    .setPositiveButton(
                        "Eliminar",
                        (dialog, w) -> {
                          if (!file.delete()) message("Error");
                          searchDevice();
                        })
                    .show();
            })
        .show();
  }

  // Recuerda el PDF de destino y permite añadir un nuevo escaneo o archivos PDF.
  private void addPages(File target) {
    if (model.busy) return;
    appendTarget = target.getPath();
    new I18n.Builder(this)
        .setTitle("Añadir hojas")
        .setItems(
            new String[] {"Escanear hojas", "Añadir PDF"},
            (d, index) -> {
              if (index == 0) startScan();
              else appendPicker.launch(new String[] {"application/pdf"});
            })
        .setNegativeButton("Cancelar", (d, w) -> appendTarget = null)
        .setOnCancelListener(d -> appendTarget = null)
        .show();
  }

  // Abre el editor posterior al escaneo y entrega sus ajustes al trabajador.
  private void editLayout(File dir) {
    if (ScanModel.images(dir).length == 0) return;
    LayoutDialog editor =
        new LayoutDialog(
            this,
            dir,
            pages ->
                model.layout(
                    dir,
                    pages,
                    () -> {
                      if (appendTarget != null) confirmAppend(new File(dir, "Documento.pdf"));
                      else if (!pages[0].output.equals("PDF")) {
                        pendingExport = dir.getPath();
                        photosExport.launch(null);
                      }
                      refresh();
                    }));
    editor.setOnCancelListener(d -> appendTarget = null);
    editor.show();
  }

  // Requiere confirmación explícita antes de sustituir el PDF seleccionado.
  private void confirmAppend(File addition) {
    if (appendTarget == null) return;
    File target = new File(appendTarget);
    appendTarget = null;
    new I18n.Builder(this)
        .setTitle("Añadir hojas")
        .setMessage(
            "Se añadirán las páginas y se sobrescribirá el PDF original. Se conservará una copia de"
                + " recuperación. ¿Continuar?")
        .setNegativeButton("Cancelar", null)
        .setPositiveButton("Reemplazar", (d, w) -> model.append(target, addition))
        .show();
  }

  // Copia los URI seleccionados al caché y prepara las páginas adicionales.
  private void prepareAppend(List<Uri> inputs) {
    if (model.busy) return;
    model.busy = true;
    model.status.setValue("Procesando…");
    model.worker.execute(
        () -> {
          try {
            File directory = new File(getCacheDir(), "append-" + UUID.randomUUID());
            if (!directory.mkdir()) throw new java.io.IOException("Cannot create cache");
            List<File> files = new ArrayList<>();
            for (Uri input : inputs) {
              File file = new File(directory, "input-" + files.size() + ".pdf");
              try (java.io.InputStream in = getContentResolver().openInputStream(input);
                  java.io.OutputStream out = new java.io.FileOutputStream(file)) {
                ScanModel.copy(in, out);
              }
              files.add(file);
            }
            File result = files.get(0);
            if (files.size() > 1) {
              result = new File(directory, "combined.pdf");
              PdfTools.merge(files, result);
            }
            final File addition = result;
            model.busy = false;
            model.status.postValue("Listo");
            runOnUiThread(() -> confirmAppend(addition));
          } catch (Exception e) {
            model.busy = false;
            model.status.postValue("Error: " + e.getMessage());
          }
        });
  }

  // Explica uso, privacidad, recuperación y límites del reconocimiento de documentos.
  private void showInfo() {
    message(
        "Escanea o importa páginas, ajusta sus bordes y prepara la salida: papel, píxeles, escala y"
            + " posición. En Mis documentos puedes añadir hojas a un PDF tras confirmar; queda una"
            + " copia .recovery. Los PDF del dispositivo requieren permiso o elegir carpeta. Cada"
            + " exportación pide destino. Procesamiento local; Android requiere Servicios de Google"
            + " Play y una descarga inicial. Los pliegues fuertes y el texto oculto no se"
            + " reconstruyen. Haz una copia antes de desinstalar. V3 — código disponible para uso"
            + " no comercial.");
  }
}
