package es.folioscan.app;

import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** Shared, offline translations. Stable Spanish source text is the catalogue key. */
public final class I18n {
  public static final String[] CODES = {
    "es", "en", "fr", "it", "pt", "nl", "uk", "ru", "sv", "pl", "cs"
  };
  public static final String[] NAMES = {
    "Español",
    "English",
    "Français",
    "Italiano",
    "Português",
    "Nederlands",
    "Українська",
    "Русский",
    "Svenska",
    "Polski",
    "Čeština"
  };
  private static final Map<String, String[]> ROWS = new HashMap<>();
  private static int language;

  // Lee el catálogo de idiomas una vez y selecciona la preferencia persistida.
  public static void load(Context context) {
    language =
        Math.max(
            0,
            Arrays.asList(CODES)
                .indexOf(
                    context.getSharedPreferences("MainActivity", 0).getString("language", "es")));
    if (!ROWS.isEmpty()) return;
    try (BufferedReader reader =
        new BufferedReader(
            new InputStreamReader(
                context.getAssets().open("translations.tsv"), StandardCharsets.UTF_8))) {
      String line;
      reader.readLine();
      while ((line = reader.readLine()) != null) {
        String[] values = line.split("\t", -1);
        if (values.length == CODES.length) {
          for (int i = 0; i < values.length; i++) values[i] = values[i].replace("\\n", "\n");
          ROWS.put(values[0], values);
        }
      }
    } catch (IOException error) {
      throw new IllegalStateException("Translation catalogue missing", error);
    }
  }

  // Busca el texto traducido localmente; las cadenas desconocidas conservan su valor original.
  public static String t(String source) {
    if (source == null) return "";
    String[] row = ROWS.get(source);
    if (row != null) return row[language];
    // Keep decorative symbols outside translatable strings.
    for (String prefix : new String[] {"⚙  ", "☀  ", "☾  ", "＋  ", "↑ ", "↓ "})
      if (source.startsWith(prefix)) return prefix + t(source.substring(prefix.length()));
    return source;
  }

  /** Covers titles, actions and menus as well as the main activity's labels. */
  public static class Builder extends AlertDialog.Builder {
    public Builder(Context context) {
      super(context);
    }

    @Override
    public Builder setTitle(CharSequence value) {
      super.setTitle(t(value.toString()));
      return this;
    }

    @Override
    public Builder setMessage(CharSequence value) {
      super.setMessage(t(value.toString()));
      return this;
    }

    @Override
    public Builder setPositiveButton(CharSequence value, DialogInterface.OnClickListener click) {
      super.setPositiveButton(t(value.toString()), click);
      return this;
    }

    @Override
    public Builder setNegativeButton(CharSequence value, DialogInterface.OnClickListener click) {
      super.setNegativeButton(t(value.toString()), click);
      return this;
    }

    @Override
    public Builder setItems(CharSequence[] values, DialogInterface.OnClickListener click) {
      String[] translated = new String[values.length];
      for (int i = 0; i < values.length; i++) translated[i] = t(values[i].toString());
      super.setItems(translated, click);
      return this;
    }
  }
}
