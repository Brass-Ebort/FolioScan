package es.folioscan.app;

import android.content.*;
import android.database.Cursor;
import android.net.Uri;
import android.os.CancellationSignal;
import android.provider.DocumentsContract;
import android.provider.DocumentsContract.Document;
import java.io.*;
import java.util.*;

/** Scoped storage for Documents/FolioScan. No all-files permission is needed here. */
final class DocumentStore {
  static final String AUTHORITY="com.android.externalstorage.documents";
  static Uri initialFolder() {
    return DocumentsContract.buildDocumentUri(AUTHORITY,"primary:Documents");
  }
  static boolean allowedSelection(Uri uri) {
    if(uri==null || !AUTHORITY.equals(uri.getAuthority())) return false;
    try {
      String id=DocumentsContract.getTreeDocumentId(uri);
      return id.equals("primary:Documents") || id.equals("primary:Documents/FolioScan");
    } catch(IllegalArgumentException error) { return false; }
  }
  static Uri ensureFolder(ContentResolver resolver, Uri tree) throws IOException {
    if(!allowedSelection(tree)) throw new IOException("Elige Documentos del teléfono.");
    String id=DocumentsContract.getTreeDocumentId(tree);
    Uri parent=DocumentsContract.buildDocumentUriUsingTree(tree,id);
    if(id.endsWith("/FolioScan")) return parent;
    try(Cursor children=resolver.query(DocumentsContract.buildChildDocumentsUriUsingTree(tree,id),
        new String[]{Document.COLUMN_DOCUMENT_ID,Document.COLUMN_DISPLAY_NAME,Document.COLUMN_MIME_TYPE},null,null)) {
      if(children==null) throw new IOException("No se pudo abrir la carpeta.");
      while(children.moveToNext()) if("FolioScan".equals(children.getString(1))) {
        if(!Document.MIME_TYPE_DIR.equals(children.getString(2))) throw new IOException("FolioScan no es una carpeta.");
        return DocumentsContract.buildDocumentUriUsingTree(tree,children.getString(0));
      }
    }
    Uri folder=DocumentsContract.createDocument(resolver,parent,Document.MIME_TYPE_DIR,"FolioScan");
    if(folder==null) throw new IOException("No se pudo crear la carpeta FolioScan.");
    return folder;
  }
  static final class Discovery {
    final List<DeviceDocument> files=new ArrayList<>();
    boolean partial;
  }
  static Discovery discover(ContentResolver resolver,Uri folder,CancellationSignal cancellation)
      throws IOException {
    Discovery result=new Discovery();
    ArrayDeque<Uri> queue=new ArrayDeque<>();queue.add(folder);
    Set<String> seen=new HashSet<>();
    long start=System.nanoTime();int visited=0;
    while(!queue.isEmpty()) {
      cancellation.throwIfCanceled();
      if((System.nanoTime()-start)/1000000L>=10000) {result.partial=true;break;}
      Uri parent=queue.removeFirst();String id=DocumentsContract.getDocumentId(parent);
      if(!seen.add(id)) continue;
      try(Cursor children=resolver.query(DocumentsContract.buildChildDocumentsUriUsingTree(folder,id),
          new String[]{Document.COLUMN_DOCUMENT_ID,Document.COLUMN_DISPLAY_NAME,Document.COLUMN_MIME_TYPE},
          null,cancellation)) {
        if(children==null) throw new IOException("No se pudo abrir la carpeta.");
        while(children.moveToNext()) {
          cancellation.throwIfCanceled();
          if(++visited>20000 || (System.nanoTime()-start)/1000000L>=10000) {result.partial=true;return result;}
          Uri child=DocumentsContract.buildDocumentUriUsingTree(folder,children.getString(0));
          String name=children.getString(1),mime=children.getString(2);
          if(Document.MIME_TYPE_DIR.equals(mime)) queue.add(child);
          else if(name!=null && ("application/pdf".equals(mime) || name.toLowerCase(Locale.ROOT).endsWith(".pdf"))) {
            result.files.add(new DeviceDocument(child,parent,name,"Documentos/FolioScan"));
            if(result.files.size()>=200) {result.partial=true;return result;}
          }
        }
      }
    }
    result.files.sort(Comparator.comparing(d->d.name,String.CASE_INSENSITIVE_ORDER));
    return result;
  }
  static void rename(ContentResolver resolver,DeviceDocument entry,String name) throws IOException {
    if(name.isEmpty() || name.startsWith(".") || name.contains("/") || name.contains("\\")) throw new IOException("Nombre no válido");
    if(entry.file!=null) {
      File target=new File(entry.file.getParentFile(),name);
      if(target.exists() || !entry.file.renameTo(target)) throw new IOException("No se pudo cambiar el nombre");
      return;
    }
    // Check sibling names first: never ask a provider to replace an existing document.
    try(Cursor siblings=resolver.query(DocumentsContract.buildChildDocumentsUriUsingTree(entry.parent,
        DocumentsContract.getDocumentId(entry.parent)),new String[]{Document.COLUMN_DISPLAY_NAME},null,null)) {
      if(siblings==null) throw new IOException("No se pudo abrir la carpeta");
      while(siblings.moveToNext()) if(name.equalsIgnoreCase(siblings.getString(0))) throw new IOException("Ya existe ese nombre");
    }
    if(DocumentsContract.renameDocument(resolver,entry.document,name)==null) throw new IOException("No se pudo cambiar el nombre");
  }
  static void delete(ContentResolver resolver,DeviceDocument entry) throws IOException {
    boolean ok=entry.file!=null ? entry.file.delete() : DocumentsContract.deleteDocument(resolver,entry.document);
    if(!ok) throw new IOException("No se pudo eliminar el documento");
  }
  static void append(Context context,Uri target,Uri parent,File addition) throws IOException {
    File work=new File(context.getCacheDir(),"append-scoped-"+UUID.randomUUID());
    if(!work.mkdir()) throw new IOException("No se pudo crear el temporal");
    ContentResolver resolver=context.getContentResolver();
    File original=new File(work,"original.pdf"),merged=new File(work,"merged.pdf");
    try {
      try(InputStream in=resolver.openInputStream(target);OutputStream out=new FileOutputStream(original)) {ScanModel.copy(in,out);}
      PdfTools.merge(Arrays.asList(original,addition),merged);
      // SAF cannot promise an atomic replacement. Persist recovery beside the original first.
      Uri recovery=DocumentsContract.createDocument(resolver,parent,"application/pdf","Recuperacion-"+UUID.randomUUID()+".pdf");
      if(recovery==null) throw new IOException("No se pudo guardar la copia de recuperación");
      try(InputStream in=new FileInputStream(original);OutputStream out=resolver.openOutputStream(recovery,"wt")) {ScanModel.copy(in,out);}
      try(InputStream in=new FileInputStream(merged);OutputStream out=resolver.openOutputStream(target,"wt")) {ScanModel.copy(in,out);}
      catch(IOException | RuntimeException failure) {
        try(InputStream in=new FileInputStream(original);OutputStream out=resolver.openOutputStream(target,"wt")) {ScanModel.copy(in,out);}
        catch(IOException | RuntimeException restore) {failure.addSuppressed(restore);}
        throw new IOException("No se pudo reemplazar el PDF. Conserva la copia de recuperación de la carpeta.",failure);
      }
    } finally {DocumentOps.deleteTree(work);}
  }
}
