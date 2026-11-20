package es.folioscan.app;

import static org.junit.Assert.*;
import java.io.*;
import java.nio.file.*;
import java.util.concurrent.*;
import java.time.Duration;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.robolectric.*;
import org.robolectric.annotation.Config;

@RunWith(RobolectricTestRunner.class)
@Config(sdk=28)
public class DiscoveryTest {
  @Test public void capsResultsAndTraversal() throws Exception {
    File root = Files.createTempDirectory("discovery").toFile();
    try {
      for (int i=0;i<8;i++) new File(root,i+".pdf").createNewFile();
      DocumentOps.Discovery result = DocumentOps.discover(root,3,100,10000);
      assertEquals(3,result.files.size()); assertTrue(result.partial);
      result = DocumentOps.discover(root,20,2,10000);
      assertTrue(result.partial); assertTrue(result.files.size()<=2);
      result = DocumentOps.discover(root,20,100,10000);
      assertEquals(8,result.files.size()); assertFalse(result.partial);
    } finally { DocumentOps.deleteTree(root); }
  }

  @Test public void inaccessibleRootFailsInsteadOfPretendingItIsEmpty() throws Exception {
    File root=Files.createTempDirectory("discovery-missing").toFile();
    root.delete();
    try { DocumentOps.discover(root); fail(); } catch (IOException expected) { }
  }

  @Test public void cancellationAndTimeoutReleaseBusyAndIgnoreLateCompletion() throws Exception {
    for (boolean timeout : new boolean[]{false,true}) {
      File directory=Files.createTempDirectory("search-late").toFile();
      CountDownLatch entered=new CountDownLatch(1),release=new CountDownLatch(1);
      File stalled=new File(directory.getPath()) {
        @Override public boolean isDirectory() {
          entered.countDown();
          boolean done=false;
          while(!done) try { release.await(); done=true; } catch(InterruptedException ignored) { }
          return true;
        }
      };
      ScanModel model=new ScanModel(RuntimeEnvironment.getApplication());
      try {
        model.discover(stalled);
        assertTrue(entered.await(2,TimeUnit.SECONDS)); assertTrue(model.busy);
        if(timeout) Shadows.shadowOf(android.os.Looper.getMainLooper()).idleFor(Duration.ofSeconds(15));
        else model.cancelSearch();
        assertFalse(model.busy); assertFalse(model.searching);
        assertEquals(timeout ? "La búsqueda ha agotado el tiempo. Vuelve a intentarlo." : "Búsqueda cancelada",model.status.getValue());
        model.status.setValue("Guardado");
        release.countDown();
        java.lang.reflect.Field field=ScanModel.class.getDeclaredField("searchWorker");field.setAccessible(true);
        ((ExecutorService)field.get(model)).submit(()->{}).get(2,TimeUnit.SECONDS);
        Shadows.shadowOf(android.os.Looper.getMainLooper()).idle();
        assertEquals("Guardado",model.status.getValue());
      } finally { release.countDown(); model.onCleared(); DocumentOps.deleteTree(directory); }
    }
  }
}
