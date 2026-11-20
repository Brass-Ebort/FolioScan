package es.folioscan.app;

import android.content.Context;
import android.net.Uri;
import androidx.core.content.FileProvider;
import java.io.File;

/** One device PDF, accessed either through a granted folder URI or explicit all-files mode. */
final class DeviceDocument {
  final File file;
  final Uri document, parent;
  final String name, location;
  DeviceDocument(File file) {
    this.file=file; document=null; parent=null;
    name=file.getName(); location=file.getParent();
  }
  DeviceDocument(Uri document, Uri parent, String name, String location) {
    file=null; this.document=document; this.parent=parent; this.name=name; this.location=location;
  }
  Uri uri(Context context) {
    return file==null ? document : FileProvider.getUriForFile(context,context.getPackageName()+".files",file);
  }
}
