package es.folioscan.app;

import android.widget.EditText;
import android.widget.Spinner;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.robolectric.*;
import org.robolectric.annotation.Config;
import java.io.*;
import java.nio.file.*;
import java.lang.reflect.*;
import static org.junit.Assert.*;

@RunWith(RobolectricTestRunner.class)
@Config(sdk=28)
public class LayoutDialogTest {
    @Test public void sheetRotationSurvivesNavigationAndSwapsImagePixels() throws Exception {
        File directory=Files.createTempDirectory("rotate-sheet").toFile();
        for(String name:new String[]{"1.jpg","2.jpg"})try(InputStream source=getClass().getResourceAsStream("/page.jpg")){Files.copy(source,new File(directory,name).toPath());}
        try(var controller=Robolectric.buildActivity(MainActivity.class).setup()){
            LayoutDialog dialog=new LayoutDialog(controller.get(),directory,pages->{});
            dialog.show();Shadows.shadowOf(android.os.Looper.getMainLooper()).idle();
            Method rotate=LayoutDialog.class.getDeclaredMethod("rotateSheet");rotate.setAccessible(true);
            Method change=LayoutDialog.class.getDeclaredMethod("change",int.class);change.setAccessible(true);
            LayoutSpec[] pages=(LayoutSpec[])field(dialog,"pages");
            pages[0].scale=1.25f;pages[0].x=.2f;
            rotate.invoke(dialog);Shadows.shadowOf(android.os.Looper.getMainLooper()).idle();
            assertTrue(pages[0].width>pages[0].height);
            assertEquals(1.25f,pages[0].scale,.001f);assertEquals(.2f,pages[0].x,.001f);
            assertTrue(pages[1].width<pages[1].height);
            change.invoke(dialog,1);Shadows.shadowOf(android.os.Looper.getMainLooper()).idle();
            change.invoke(dialog,-1);Shadows.shadowOf(android.os.Looper.getMainLooper()).idle();
            assertTrue(pages[0].width>pages[0].height);
            rotate.invoke(dialog);assertTrue(pages[0].width<pages[0].height);
            ((Spinner)field(dialog,"output")).setSelection(2);Shadows.shadowOf(android.os.Looper.getMainLooper()).idle();
            ((EditText)field(dialog,"pw")).setText("800");((EditText)field(dialog,"ph")).setText("400");
            rotate.invoke(dialog);Shadows.shadowOf(android.os.Looper.getMainLooper()).idle();
            assertEquals(400,pages[0].pixelsWide);assertEquals(800,pages[0].pixelsHigh);
            assertEquals(.5f,pages[0].width/pages[0].height,.001f);
            dialog.dismiss();
        }finally{DocumentOps.deleteTree(directory);}
    }
    private Object field(Object object,String name)throws Exception{Field f=object.getClass().getDeclaredField(name);f.setAccessible(true);return f.get(object);}
    @Test public void editedImageDimensionsSurviveNavigation()throws Exception{
        File directory=Files.createTempDirectory("layout-test").toFile();
        for(String name:new String[]{"1.jpg","2.jpg"})try(InputStream source=getClass().getResourceAsStream("/page.jpg")){Files.copy(source,new File(directory,name).toPath());}
        try(var controller=Robolectric.buildActivity(MainActivity.class).setup()){
            LayoutDialog dialog=new LayoutDialog(controller.get(),directory,pages->{});dialog.show();Shadows.shadowOf(android.os.Looper.getMainLooper()).idle();
            ((Spinner)field(dialog,"output")).setSelection(2);Shadows.shadowOf(android.os.Looper.getMainLooper()).idle();
            ((EditText)field(dialog,"pw")).setText("800");((EditText)field(dialog,"ph")).setText("400");
            Method read=LayoutDialog.class.getDeclaredMethod("readFields");read.setAccessible(true);read.invoke(dialog);
            LayoutSpec[] pages=(LayoutSpec[])field(dialog,"pages");assertEquals(2,pages[0].width/pages[0].height,.001);
            Method change=LayoutDialog.class.getDeclaredMethod("change",int.class);change.setAccessible(true);change.invoke(dialog,1);Shadows.shadowOf(android.os.Looper.getMainLooper()).idle();change.invoke(dialog,-1);Shadows.shadowOf(android.os.Looper.getMainLooper()).idle();
            assertEquals(800,pages[0].pixelsWide);assertEquals(400,pages[0].pixelsHigh);assertEquals(2,pages[0].width/pages[0].height,.001);dialog.dismiss();
        }finally{DocumentOps.deleteTree(directory);}
    }
}
