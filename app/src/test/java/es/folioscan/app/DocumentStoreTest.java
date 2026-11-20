package es.folioscan.app;

import static org.junit.Assert.*;
import android.content.*;
import android.database.*;
import android.net.Uri;
import android.os.*;
import android.provider.DocumentsContract;
import android.provider.DocumentsContract.Document;
import android.provider.DocumentsProvider;
import java.io.*;
import java.util.*;
import org.junit.*;
import org.junit.runner.RunWith;
import org.robolectric.*;
import org.robolectric.annotation.Config;
import org.robolectric.shadows.ShadowContentResolver;
import com.tom_roush.pdfbox.pdmodel.*;

/** Exercise SAF operations against a local document provider, without broad permissions. */
@RunWith(RobolectricTestRunner.class) @Config(sdk=28)
public class DocumentStoreTest {
  Provider provider;
  ContentResolver resolver;
  Uri tree = DocumentsContract.buildTreeDocumentUri(DocumentStore.AUTHORITY,"primary:Documents");
  @Before public void setup() throws Exception {
    provider = new Provider();
    provider.root=java.nio.file.Files.createTempDirectory("scoped-documents").toFile();
    android.content.pm.ProviderInfo info=new android.content.pm.ProviderInfo();
    info.authority=DocumentStore.AUTHORITY;info.exported=true;info.grantUriPermissions=true;
    info.readPermission="android.permission.MANAGE_DOCUMENTS";info.writePermission=info.readPermission;
    provider.attachInfo(RuntimeEnvironment.getApplication(),info);
    ShadowContentResolver.registerProviderInternal(DocumentStore.AUTHORITY,provider);
    resolver=RuntimeEnvironment.getApplication().getContentResolver();
    com.tom_roush.pdfbox.android.PDFBoxResourceLoader.init(RuntimeEnvironment.getApplication());
  }
  @After public void cleanup() { DocumentOps.deleteTree(provider.root); }
  @Test public void createsFolderOnceAndSearchDoesNotIncludeSiblingPdf() throws Exception {
    new File(provider.root,"outside.pdf").createNewFile();
    Uri folder=DocumentStore.ensureFolder(resolver,tree);
    assertEquals(folder,DocumentStore.ensureFolder(resolver,tree));
    new File(provider.root,"FolioScan/inside.pdf").createNewFile();
    DocumentStore.Discovery result=DocumentStore.discover(resolver,folder,new CancellationSignal());
    assertEquals(1,result.files.size());assertEquals("inside.pdf",result.files.get(0).name);
    assertFalse(DocumentStore.allowedSelection(DocumentsContract.buildTreeDocumentUri(DocumentStore.AUTHORITY,"primary:")));
    assertFalse(DocumentStore.allowedSelection(DocumentsContract.buildTreeDocumentUri("cloud","primary:Documents")));
    assertTrue(DocumentStore.allowedSelection(DocumentsContract.buildTreeDocumentUri(DocumentStore.AUTHORITY,"primary:Documents/FolioScan")));
  }
  @Test public void capsSearchAndHonorsCancellation() throws Exception {
    Uri folder=DocumentStore.ensureFolder(resolver,tree);
    for(int i=0;i<205;i++) new File(provider.root,"FolioScan/"+i+".pdf").createNewFile();
    DocumentStore.Discovery result=DocumentStore.discover(resolver,folder,new CancellationSignal());
    assertEquals(200,result.files.size());assertTrue(result.partial);
    CancellationSignal cancelled=new CancellationSignal();cancelled.cancel();
    try {DocumentStore.discover(resolver,folder,cancelled);fail();} catch(OperationCanceledException expected) { }
  }
  @Test public void renameRefusesOverwriteAndDeleteTargetsSelectedFile() throws Exception {
    Uri folder=DocumentStore.ensureFolder(resolver,tree);
    new File(provider.root,"FolioScan/a.pdf").createNewFile();new File(provider.root,"FolioScan/b.pdf").createNewFile();
    DeviceDocument entry=DocumentStore.discover(resolver,folder,new CancellationSignal()).files.get(0);
    try { DocumentStore.rename(resolver,entry,"b.pdf");fail(); } catch(IOException expected) { }
    DocumentStore.rename(resolver,entry,"c.pdf");
    assertTrue(new File(provider.root,"FolioScan/c.pdf").exists());
    entry=DocumentStore.discover(resolver,folder,new CancellationSignal()).files.get(0);
    DocumentStore.delete(resolver,entry);
    assertFalse(new File(provider.root,"FolioScan/b.pdf").exists());
    assertTrue(new File(provider.root,"FolioScan/c.pdf").exists());
  }
  @Test public void appendKeepsOriginalRecoveryAndAddsPages() throws Exception {
    Uri folder=DocumentStore.ensureFolder(resolver,tree);
    File original=new File(provider.root,"FolioScan/a.pdf"),addition=new File(provider.root,"add.pdf");
    for(File file:Arrays.asList(original,addition)) try(PDDocument pdf=new PDDocument()) {pdf.addPage(new PDPage());pdf.save(file);}
    byte[] before=java.nio.file.Files.readAllBytes(original.toPath());
    DeviceDocument entry=DocumentStore.discover(resolver,folder,new CancellationSignal()).files.get(0);
    DocumentStore.append(RuntimeEnvironment.getApplication(),entry.document,entry.parent,addition);
    try(PDDocument pdf=PDDocument.load(original)) {assertEquals(2,pdf.getNumberOfPages());}
    File[] recovery=original.getParentFile().listFiles(f->f.getName().startsWith("Recuperacion-"));
    assertEquals(1,recovery.length);assertArrayEquals(before,java.nio.file.Files.readAllBytes(recovery[0].toPath()));
  }
  public static class Provider extends DocumentsProvider {
    File root;
    public boolean onCreate(){return true;}
    File file(String id){return new File(root,id.equals("primary:Documents") ? "" : id.substring("primary:Documents/".length()));}
    String id(File file){String relative=root.toPath().relativize(file.toPath()).toString().replace('\\','/');return "primary:Documents"+(relative.isEmpty()?"":"/"+relative);}
    public Cursor queryRoots(String[] projection){return new MatrixCursor(new String[]{"root_id"});}
    MatrixCursor cursor(String[] projection){return new MatrixCursor(projection==null ? new String[]{Document.COLUMN_DOCUMENT_ID,Document.COLUMN_DISPLAY_NAME,Document.COLUMN_MIME_TYPE}:projection);}
    void row(MatrixCursor cursor,File file){Object[] values=new Object[cursor.getColumnCount()];String[] cols=cursor.getColumnNames();for(int i=0;i<cols.length;i++) {if(cols[i].equals(Document.COLUMN_DOCUMENT_ID))values[i]=id(file);if(cols[i].equals(Document.COLUMN_DISPLAY_NAME))values[i]=file.getName();if(cols[i].equals(Document.COLUMN_MIME_TYPE))values[i]=file.isDirectory()?Document.MIME_TYPE_DIR:"application/pdf";}cursor.addRow(values);}
    public Cursor queryDocument(String id,String[] projection){MatrixCursor c=cursor(projection);row(c,file(id));return c;}
    public Cursor queryChildDocuments(String id,String[] projection,String sort){MatrixCursor c=cursor(projection);File[] children=file(id).listFiles();if(children!=null)for(File child:children)row(c,child);return c;}
    public ParcelFileDescriptor openDocument(String id,String mode,CancellationSignal signal)throws FileNotFoundException{return ParcelFileDescriptor.open(file(id),ParcelFileDescriptor.parseMode(mode));}
    public String createDocument(String parent,String mime,String name)throws FileNotFoundException{File f=new File(file(parent),name);try{if(Document.MIME_TYPE_DIR.equals(mime))f.mkdir();else f.createNewFile();return id(f);}catch(IOException e){throw new FileNotFoundException(e.toString());}}
    public String renameDocument(String id,String name)throws FileNotFoundException{File old=file(id),next=new File(old.getParentFile(),name);if(!old.renameTo(next))throw new FileNotFoundException();return id(next);}
    public void deleteDocument(String id)throws FileNotFoundException{if(!file(id).delete())throw new FileNotFoundException();}
    public boolean isChildDocument(String parent,String child){return child.startsWith(parent+"/");}
  }
}
