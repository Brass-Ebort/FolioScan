package es.folioscan.app;

public final class PageFit {
  private PageFit() {}

  public static float[] fit(
      int imageWidth, int imageHeight, int pageWidth, int pageHeight, int margin) {
    if (imageWidth <= 0
        || imageHeight <= 0
        || pageWidth <= 2 * margin
        || pageHeight <= 2 * margin
        || margin < 0) throw new IllegalArgumentException("Dimensiones no válidas");
    float scale =
        Math.min((pageWidth - 2f * margin) / imageWidth, (pageHeight - 2f * margin) / imageHeight);
    float width = imageWidth * scale, height = imageHeight * scale;
    return new float[] {
      (pageWidth - width) / 2,
      (pageHeight - height) / 2,
      (pageWidth + width) / 2,
      (pageHeight + height) / 2
    };
  }
}
