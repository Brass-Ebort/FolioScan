package es.folioscan.app;
import android.view.*;
import android.widget.TextView;
import android.util.TypedValue;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.robolectric.*;
import org.robolectric.android.controller.ActivityController;
import org.robolectric.annotation.Config;
import static org.junit.Assert.*;

@RunWith(RobolectricTestRunner.class)
@Config(sdk=28)
public class MainActivityTest {
    @Test @Config(qualifiers="fr-rFR") public void systemLanguageAndManualOverride() {
        android.content.Context context = RuntimeEnvironment.getApplication();
        android.content.SharedPreferences prefs = context.getSharedPreferences("MainActivity",0);
        prefs.edit().remove("language").commit();
        I18n.load(context);
        assertEquals("Scanner", I18n.t("Escáner"));
        assertEquals("Gestionnaire PDF", I18n.t("Gestor de PDF"));
        prefs.edit().putString("language","es").commit();
        I18n.load(context);
        assertEquals("Gestor de PDF", I18n.t("Gestor de PDF"));
    }

    @Test public void footerOnlyInSettingsAndNoManagerFormatSelector() {
        RuntimeEnvironment.getApplication().getSharedPreferences("MainActivity",0).edit().putString("language","es").commit();
        try(ActivityController<MainActivity> controller=Robolectric.buildActivity(MainActivity.class).setup()) {
            MainActivity activity=controller.get();
            View root=activity.getWindow().getDecorView();
            assertNull(find(root,"Gracias por descargar la aplicación."));
            find(root,"Gestor de PDF").performClick();
            root=activity.getWindow().getDecorView();
            assertNull(find(root,"Tamaño para imágenes → PDF"));
            assertNull(find(root,"Gracias por descargar la aplicación."));
            find(root,"⚙").performClick();
            android.app.Dialog drawer=org.robolectric.shadows.ShadowDialog.getLatestDialog();
            assertNotNull(find(drawer.getWindow().getDecorView(),"Gracias por descargar la aplicación."));
            drawer.dismiss();
        }
    }
    @Test public void selectedTabIsDarkerInBothThemes() {
        for(boolean dark:new boolean[]{false,true}){
            RuntimeEnvironment.getApplication().getSharedPreferences("MainActivity",0).edit().putBoolean("dark",dark).putString("language","es").commit();
            try(ActivityController<MainActivity> controller=Robolectric.buildActivity(MainActivity.class).setup()){
                MainActivity activity=controller.get();View root=activity.getWindow().getDecorView();
                View selected=find(root,"Escáner"),other=find(root,"Gestor de PDF");
                assertTrue(selected.isSelected());assertFalse(other.isSelected());
                int a=((android.graphics.drawable.GradientDrawable)selected.getBackground()).getColor().getDefaultColor();
                int b=((android.graphics.drawable.GradientDrawable)other.getBackground()).getColor().getDefaultColor();
                assertTrue(androidx.core.graphics.ColorUtils.calculateLuminance(a)<androidx.core.graphics.ColorUtils.calculateLuminance(b));
                assertTrue(androidx.core.graphics.ColorUtils.calculateContrast(android.graphics.Color.WHITE,a)>=4.5);
                other.performClick();assertTrue(find(activity.getWindow().getDecorView(),"Gestor de PDF").isSelected());
            }
        }
    }
    private View find(View view,String label) {
        if(view instanceof TextView && ((TextView)view).getText().toString().equals(label))return view;
        if(view instanceof ViewGroup)for(int i=0;i<((ViewGroup)view).getChildCount();i++){View result=find(((ViewGroup)view).getChildAt(i),label);if(result!=null)return result;}
        return null;
    }
    @Test public void darkPreferenceAndPdfTabSurviveRecreation() {
        RuntimeEnvironment.getApplication().getSharedPreferences("MainActivity",0).edit().putBoolean("dark",true).putString("language","es").putString("format","A3").commit();
        try(ActivityController<MainActivity> controller=Robolectric.buildActivity(MainActivity.class).setup()) {
            MainActivity activity=controller.get();
            assertTrue(activity.getPreferences(0).getBoolean("dark",false));
            TypedValue color=new TypedValue();activity.getTheme().resolveAttribute(android.R.attr.windowLightStatusBar,color,true);assertEquals(0,color.data);
            View tab=find(activity.getWindow().getDecorView(),"Gestor de PDF");assertNotNull(tab);tab.performClick();
            assertNotNull(find(activity.getWindow().getDecorView(),"Unir varios PDF"));
            controller.recreate();activity=controller.get();
            assertTrue(activity.getPreferences(0).getBoolean("dark",false));
            assertEquals("A3",activity.getPreferences(0).getString("format",""));
            assertNotNull(find(activity.getWindow().getDecorView(),"Unir varios PDF"));
        }
    }
}
