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
