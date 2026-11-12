package es.folioscan.app;

/** Coordinates use a top-left origin on both platforms; PDF conversion flips Y. */
public class LayoutSpec {
  public String format = "A4", output = "PDF";
  public float width = 595, height = 842, scale = 1, x = 0, y = 0;
  public int pixelsWide = 1240, pixelsHigh = 1754;

  // Copia los valores de composición para mantener ajustes independientes por página.
  public LayoutSpec copy() {
    LayoutSpec s = new LayoutSpec();
    s.format = format;
    s.output = output;
    s.width = width;
    s.height = height;
    s.scale = scale;
    s.x = x;
    s.y = y;
    s.pixelsWide = pixelsWide;
    s.pixelsHigh = pixelsHigh;
    return s;
  }

  // Calcula el encaje proporcional y aplica escala y desplazamiento sin estirar la imagen.
  public float[] box(int imageWidth, int imageHeight) {
    float fit = Math.min(width / imageWidth, height / imageHeight) * scale;
    float w = imageWidth * fit, h = imageHeight * fit;
    return new float[] {(width - w) / 2 + x * width, (height - h) / 2 + y * height, w, h};
  }

  // Rechaza dimensiones o resoluciones fuera de los límites de memoria establecidos.
  public void validate() {
    if (width < 10
        || height < 10
        || width > 4000
        || height > 4000
        || scale < .1f
        || scale > 4
        || pixelsWide < 64
        || pixelsHigh < 64
        || pixelsWide > 6000
        || pixelsHigh > 6000
        || (long) pixelsWide * pixelsHigh > 24000000)
      throw new IllegalArgumentException("Invalid output dimensions");
  }
}
