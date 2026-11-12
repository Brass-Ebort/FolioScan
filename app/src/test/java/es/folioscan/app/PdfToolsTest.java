package es.folioscan.app;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.robolectric.RobolectricTestRunner;
import org.robolectric.RuntimeEnvironment;
import org.robolectric.annotation.Config;
import com.tom_roush.pdfbox.android.PDFBoxResourceLoader;
import com.tom_roush.pdfbox.pdmodel.*;
import com.tom_roush.pdfbox.pdmodel.common.PDRectangle;
import com.tom_roush.pdfbox.pdmodel.font.PDType1Font;
import com.tom_roush.pdfbox.text.PDFTextStripper;
import java.io.*;
import java.util.*;
import java.util.zip.*;
import static org.junit.Assert.*;

@RunWith(RobolectricTestRunner.class)
@Config(sdk=28)
public class PdfToolsTest {
    @Test public void mergeAndSplitPreservePagesDimensionsAndRotation() throws Exception {
        PdfTools.initialize(RuntimeEnvironment.getApplication());
        File root=new File(RuntimeEnvironment.getApplication().getCacheDir(),"test-"+UUID.randomUUID()); assertTrue(root.mkdir());
        File first=new File(root,"first.pdf"),second=new File(root,"second.pdf"),merged=new File(root,"merged.pdf"),split=new File(root,"split.zip");
        try(PDDocument pdf=new PDDocument()) { PDPage textPage=new PDPage(new PDRectangle(595,842));pdf.addPage(textPage);try(PDPageContentStream content=new PDPageContentStream(pdf,textPage)) {content.beginText();content.setFont(PDType1Font.HELVETICA,16);content.newLineAtOffset(40,700);content.showText("Texto seleccionable");content.endText();} PDPage p=new PDPage(new PDRectangle(300,400));p.setRotation(90);pdf.addPage(p);pdf.save(first); }
        try(PDDocument pdf=new PDDocument()) {pdf.addPage(new PDPage(new PDRectangle(200,500)));pdf.save(second);}
        PdfTools.merge(Arrays.asList(first,second),merged);
        try(PDDocument pdf=PDDocument.load(merged)) {assertEquals(3,pdf.getNumberOfPages());assertEquals(595,pdf.getPage(0).getMediaBox().getWidth(),.01);assertEquals(90,pdf.getPage(1).getRotation());assertEquals(200,pdf.getPage(2).getMediaBox().getWidth(),.01);}
        PdfTools.split(merged,split);
        try(ZipFile zip=new ZipFile(split)) {
            assertEquals(3,zip.size());
            for(int i=1;i<=3;i++) try(InputStream stream=zip.getInputStream(zip.getEntry(String.format(Locale.ROOT,"Pagina-%03d.pdf",i)));PDDocument pdf=PDDocument.load(stream)) {
                assertEquals(1,pdf.getNumberOfPages()); if(i==2)assertEquals(90,pdf.getPage(0).getRotation()); if(i==1)assertTrue(new PDFTextStripper().getText(pdf).contains("Texto seleccionable"));
            }
        }
    }
}
