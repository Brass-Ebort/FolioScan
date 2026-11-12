package es.folioscan.app;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.robolectric.RobolectricTestRunner;
import org.robolectric.RuntimeEnvironment;
import org.robolectric.annotation.Config;
import java.io.*;
import java.nio.file.*;
import com.tom_roush.pdfbox.android.PDFBoxResourceLoader;
import com.tom_roush.pdfbox.pdmodel.*;
import static org.junit.Assert.*;

/** Exercise replacement with real PDFs; an unsuccessful addition must lose no data. */
@RunWith(RobolectricTestRunner.class)
@Config(sdk=28)
public class DocumentOpsTest {
    @Test public void appendPreservesBackupAndOriginalOnFailure() throws Exception {
        PDFBoxResourceLoader.init(RuntimeEnvironment.getApplication());
        File root=Files.createTempDirectory("append-test").toFile();
        try {
            File original=new File(root,"original.pdf"),addition=new File(root,"addition.pdf");
            for(File file:new File[]{original,addition})try(PDDocument doc=new PDDocument()){doc.addPage(new PDPage());doc.save(file);}
            byte[] before=Files.readAllBytes(original.toPath());DocumentOps.append(original,addition);
            assertArrayEquals(before,Files.readAllBytes(new File(original+".recovery").toPath()));
            try(PDDocument doc=PDDocument.load(original)){assertEquals(2,doc.getNumberOfPages());}
            byte[] good=Files.readAllBytes(original.toPath());
            try{DocumentOps.append(original,new File(root,"missing.pdf"));fail();}catch(IOException expected){}
            assertArrayEquals(good,Files.readAllBytes(original.toPath()));
        }finally{DocumentOps.deleteTree(root);}
    }
    @Test public void layoutGeometryAndLimits(){
        LayoutSpec spec=new LayoutSpec();spec.width=200;spec.height=100;spec.scale=.5f;spec.x=.25f;
        assertArrayEquals(new float[]{125,25,50,50},spec.box(100,100),.01f);
        spec.pixelsWide=6000;spec.pixelsHigh=6000;
        try{spec.validate();fail();}catch(IllegalArgumentException expected){}
    }
    @Test public void allLanguagesLoad(){
        for(String language:I18n.CODES){RuntimeEnvironment.getApplication().getSharedPreferences("MainActivity",0).edit().putString("language",language).commit();I18n.load(RuntimeEnvironment.getApplication());assertFalse(I18n.t("Guardar").isEmpty());}
        RuntimeEnvironment.getApplication().getSharedPreferences("MainActivity",0).edit().putString("language","es").commit();I18n.load(RuntimeEnvironment.getApplication());
    }
}
