package es.folioscan.app;

public final class PageFormats {
  public static final String[] NAMES = {
    "Original", "A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10"
  };
  private static final int[][] MM = {
    {841, 1189},
    {594, 841},
    {420, 594},
    {297, 420},
    {210, 297},
    {148, 210},
    {105, 148},
    {74, 105},
    {52, 74},
    {37, 52},
    {26, 37}
  };

  private PageFormats() {}

  public static int[] points(String format, boolean landscape) {
    for (int i = 1; i < NAMES.length; i++)
      if (NAMES[i].equals(format)) {
        int w = Math.round(MM[i - 1][0] * 72f / 25.4f), h = Math.round(MM[i - 1][1] * 72f / 25.4f);
        return landscape ? new int[] {h, w} : new int[] {w, h};
      }
    throw new IllegalArgumentException("Formato desconocido: " + format);
  }
}
