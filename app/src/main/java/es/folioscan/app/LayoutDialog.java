package es.folioscan.app;

import android.app.*;
import android.graphics.*;
import android.os.Bundle;
import android.view.*;
import android.widget.*;
import java.io.File;
import java.util.function.Consumer;

/** Post-scan layout editor. Each page has independent scale and translation. */
public final class LayoutDialog extends Dialog {
  private final File[] files;
  private final LayoutSpec[] pages;
  private final Consumer<LayoutSpec[]> saved;
  private int index;
  private boolean loading;
  private Preview preview;
  private TextView number;
  private Spinner format, output;
  private EditText width, height, pw, ph;
  private SeekBar zoom, x, y;
  private Bitmap bitmap;
  private final Activity activity;

  public LayoutDialog(Activity a, File dir, Consumer<LayoutSpec[]> callback) {
    super(a);
    activity = a;
    files = ScanModel.images(dir);
    saved = callback;
    pages = new LayoutSpec[files.length];
    for (int i = 0; i < pages.length; i++) pages[i] = new LayoutSpec();
  }

  private TextView label(String text) {
    TextView v = new TextView(activity);
    v.setText(I18n.t(text));
    v.setPadding(8, 8, 8, 4);
    return v;
  }

  private Button button(String title, Runnable action) {
    Button b = new Button(activity);
    b.setText(I18n.t(title));
    b.setAllCaps(false);
    b.setOnClickListener(v -> action.run());
    return b;
  }

  private Spinner select(String[] items) {
    Spinner s = new Spinner(activity);
    s.setAdapter(
        new ArrayAdapter<>(activity, android.R.layout.simple_spinner_dropdown_item, items));
    return s;
  }

  @Override
  // Restaura preferencias, registra resultados del sistema y construye la interfaz.
  protected void onCreate(Bundle state) {
    super.onCreate(state);
    setTitle(I18n.t("Preparar salida"));
    LinearLayout body = new LinearLayout(activity);
    body.setOrientation(LinearLayout.VERTICAL);
    body.setPadding(12, 12, 12, 12);
    ScrollView scroll = new ScrollView(activity);
    scroll.addView(body);
    setContentView(scroll);
    LinearLayout nav = new LinearLayout(activity);
    nav.addView(button("‹", () -> change(-1)), new LinearLayout.LayoutParams(0, 52, 1));
    number = label("");
    nav.addView(number, new LinearLayout.LayoutParams(0, 52, 1));
    nav.addView(button("›", () -> change(1)), new LinearLayout.LayoutParams(0, 52, 1));
    body.addView(nav);
    preview = new Preview();
    body.addView(
        preview,
        new LinearLayout.LayoutParams(
            -1, Math.round(240 * activity.getResources().getDisplayMetrics().density)));
    body.addView(label("Formato de papel"));
    String[] formats = new String[PageFormats.NAMES.length + 1];
    System.arraycopy(PageFormats.NAMES, 0, formats, 0, PageFormats.NAMES.length);
    formats[formats.length - 1] = I18n.t("Personalizado");
    format = select(formats);
    body.addView(format);
    LinearLayout dimensions = new LinearLayout(activity);
    width = field(dimensions, "Ancho (mm)");
    height = field(dimensions, "Alto (mm)");
    body.addView(dimensions);
    body.addView(button("Girar hoja 90°", this::rotateSheet));
    zoom = slider(body, "Escala", 390);
    x = slider(body, "Horizontal", 200);
    y = slider(body, "Vertical", 200);
    body.addView(
        button(
            "Centrar",
            () -> {
              pages[index].scale = 1;
              pages[index].x = pages[index].y = 0;
              loadControls();
            }));
    body.addView(label("Salida"));
    output = select(new String[] {"PDF", "JPG", "PNG"});
    body.addView(output);
    LinearLayout pixels = new LinearLayout(activity);
    pw = field(pixels, "Ancho (px)");
    ph = field(pixels, "Alto (px)");
    body.addView(pixels);
    body.addView(label("Lo que queda fuera de la hoja se recorta."));
    body.addView(
        button(
            "Aplicar a todas",
            () -> {
              try {
                readFields();
                for (int i = 0; i < pages.length; i++) pages[i] = pages[index].copy();
              } catch (Exception e) {
                invalid();
              }
            }));
    body.addView(
        button(
            "Guardar",
            () -> {
              try {
                readFields();
                for (LayoutSpec s : pages) s.validate();
                saved.accept(pages);
                dismiss();
              } catch (Exception e) {
                invalid();
              }
            }));
    format.setOnItemSelectedListener(
        new AdapterView.OnItemSelectedListener() {
          public void onNothingSelected(AdapterView<?> p) {}

          public void onItemSelected(AdapterView<?> p, View v, int position, long id) {
            if (loading) return;
            LayoutSpec s = pages[index];
            String selected = position < PageFormats.NAMES.length ? PageFormats.NAMES[position] : "Custom";
            // Cargar otra página no debe reiniciar su orientación guardada.
            if (selected.equals(s.format)) return;
            s.format = selected;
            if (position == 0 && bitmap != null) {
              s.width = bitmap.getWidth() * 72f / 150;
              s.height = bitmap.getHeight() * 72f / 150;
            } else if (position < PageFormats.NAMES.length) {
              int[] size = PageFormats.points(s.format, false);
              s.width = size[0];
              s.height = size[1];
            }
            float resolution = Math.min(150f / 72, 4096 / Math.max(s.width, s.height));
            s.pixelsWide = Math.max(64, Math.round(s.width * resolution));
            s.pixelsHigh = Math.max(64, Math.round(s.height * resolution));
            loadControls();
          }
        });
    output.setOnItemSelectedListener(
        new AdapterView.OnItemSelectedListener() {
          public void onNothingSelected(AdapterView<?> p) {}

          public void onItemSelected(AdapterView<?> p, View v, int position, long id) {
            if (!loading) {
              String value = new String[] {"PDF", "JPG", "PNG"}[position];
              for (LayoutSpec s : pages) {
                s.output = value;
                if (!value.equals("PDF")) {
                  s.width = s.pixelsWide * 72f / 150;
                  s.height = s.pixelsHigh * 72f / 150;
                }
              }
              loadControls();
            }
          }
        });
    for (EditText field : new EditText[] {width, height, pw, ph})
      field.setOnFocusChangeListener(
          (v, focus) -> {
            if (!focus && !loading)
              try {
                readFields();
              } catch (Exception ignored) {
              }
          });
    loadPage();
  }

  private EditText field(LinearLayout parent, String title) {
    LinearLayout column = new LinearLayout(activity);
    column.setOrientation(LinearLayout.VERTICAL);
    column.addView(label(title));
    EditText e = new EditText(activity);
    e.setSingleLine(true);
    e.setInputType(8194);
    column.addView(e);
    parent.addView(column, new LinearLayout.LayoutParams(0, -2, 1));
    return e;
  }

  private SeekBar slider(LinearLayout parent, String title, int max) {
    parent.addView(label(title));
    SeekBar bar = new SeekBar(activity);
    bar.setMax(max);
    bar.setOnSeekBarChangeListener(
        new SeekBar.OnSeekBarChangeListener() {
          public void onStartTrackingTouch(SeekBar b) {}

          public void onStopTrackingTouch(SeekBar b) {}

          public void onProgressChanged(SeekBar b, int value, boolean user) {
            if (loading || !user) return;
            LayoutSpec s = pages[index];
            if (b == zoom) s.scale = (value + 10) / 100f;
            else if (b == x) s.x = (value - 100) / 100f;
            else s.y = (value - 100) / 100f;
            preview.invalidate();
          }
        });
    parent.addView(bar);
    return bar;
  }

  private void readFields() {
    LayoutSpec s = pages[index];
    s.width = Float.parseFloat(width.getText().toString()) * 72 / 25.4f;
    s.height = Float.parseFloat(height.getText().toString()) * 72 / 25.4f;
    s.pixelsWide = Integer.parseInt(pw.getText().toString());
    s.pixelsHigh = Integer.parseInt(ph.getText().toString());
    if (!s.output.equals("PDF")) {
      s.width = s.pixelsWide * 72f / 150;
      s.height = s.pixelsHigh * 72f / 150;
    }
    s.validate();
    preview.invalidate();
  }

  private void invalid() {
    new I18n.Builder(activity)
        .setMessage("Ancho/alto: 4–1411 mm; imagen: 64–6000 px, máximo 24 megapíxeles.")
        .setPositiveButton("Entendido", null)
        .show();
  }

  // Alterna vertical/horizontal sin girar ni modificar la fotografía original.
  private void rotateSheet() {
    try {
      readFields();
      LayoutSpec s = pages[index];
      float previousWidth = s.width;
      s.width = s.height;
      s.height = previousWidth;
      int previousPixels = s.pixelsWide;
      s.pixelsWide = s.pixelsHigh;
      s.pixelsHigh = previousPixels;
      loadControls();
    } catch (Exception e) {
      invalid();
    }
  }

  // Cambia de página conservando los ajustes de la anterior.
  private void change(int delta) {
    int next = index + delta;
    if (next < 0 || next >= pages.length) return;
    try {
      readFields();
      index = next;
      loadPage();
    } catch (Exception e) {
      invalid();
    }
  }

  private void loadPage() {
    try {
      if (bitmap != null) bitmap.recycle();
      bitmap = PdfTools.decode(files[index]);
      loadControls();
    } catch (Exception e) {
      dismiss();
    }
  }

  private void loadControls() {
    loading = true;
    LayoutSpec s = pages[index];
    number.setText((index + 1) + " / " + pages.length);
    width.setText(String.format(java.util.Locale.ROOT, "%.2f", s.width * 25.4 / 72));
    height.setText(String.format(java.util.Locale.ROOT, "%.2f", s.height * 25.4 / 72));
    pw.setText("" + s.pixelsWide);
    ph.setText("" + s.pixelsHigh);
    zoom.setProgress(Math.round(s.scale * 100) - 10);
    x.setProgress(Math.round(s.x * 100) + 100);
    y.setProgress(Math.round(s.y * 100) + 100);
    int position = java.util.Arrays.asList(PageFormats.NAMES).indexOf(s.format);
    format.setSelection(position < 0 ? PageFormats.NAMES.length : position);
    output.setSelection(java.util.Arrays.asList("PDF", "JPG", "PNG").indexOf(s.output));
    loading = false;
    preview.invalidate();
  }

  @Override
  public void show() {
    super.show();
    getWindow().setLayout(-1, -1);
  }

  @Override
  public void dismiss() {
    if (bitmap != null) {
      bitmap.recycle();
      bitmap = null;
    }
    super.dismiss();
  }

  private final class Preview extends View {
    private float lastX, lastY, factor;

    Preview() {
      super(activity);
    }

    @Override
    protected void onDraw(Canvas canvas) {
      canvas.drawColor(Color.DKGRAY);
      if (bitmap == null) return;
      LayoutSpec s = pages[index];
      factor = Math.min((getWidth() - 20) / s.width, (getHeight() - 20) / s.height);
      canvas.save();
      canvas.translate((getWidth() - s.width * factor) / 2, (getHeight() - s.height * factor) / 2);
      canvas.scale(factor, factor);
      canvas.clipRect(0, 0, s.width, s.height);
      canvas.drawColor(Color.WHITE);
      float[] b = s.box(bitmap.getWidth(), bitmap.getHeight());
      canvas.drawBitmap(
          bitmap,
          null,
          new RectF(b[0], b[1], b[0] + b[2], b[1] + b[3]),
          new Paint(Paint.FILTER_BITMAP_FLAG));
      canvas.restore();
    }

    @Override
    public boolean onTouchEvent(MotionEvent e) {
      if (e.getAction() == MotionEvent.ACTION_DOWN) {
        lastX = e.getX();
        lastY = e.getY();
        getParent().requestDisallowInterceptTouchEvent(true);
        return true;
      }
      if (e.getAction() == MotionEvent.ACTION_MOVE && factor > 0) {
        LayoutSpec s = pages[index];
        s.x = Math.max(-1, Math.min(1, s.x + (e.getX() - lastX) / factor / s.width));
        s.y = Math.max(-1, Math.min(1, s.y + (e.getY() - lastY) / factor / s.height));
        lastX = e.getX();
        lastY = e.getY();
        invalidate();
        return true;
      }
      if (e.getAction() == MotionEvent.ACTION_UP) {
        performClick();
        loadControls();
      }
      return true;
    }

    @Override
    public boolean performClick() {
      super.performClick();
      return true;
    }
  }
}
