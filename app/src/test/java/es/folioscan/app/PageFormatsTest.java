package es.folioscan.app;
import org.junit.Test;
import static org.junit.Assert.*;
public class PageFormatsTest {
    @Test public void formatsHaveCorrectDimensionsAndOrientations() {
        assertArrayEquals(new int[]{595,842},PageFormats.points("A4",false));
        assertArrayEquals(new int[]{842,595},PageFormats.points("A4",true));
        assertArrayEquals(new int[]{2384,3370},PageFormats.points("A0",false));
        assertArrayEquals(new int[]{74,105},PageFormats.points("A10",false));
        for(int i=1;i<PageFormats.NAMES.length;i++) {
            int[] size=PageFormats.points(PageFormats.NAMES[i],false);
            float[] fit=PageFit.fit(2000,3000,size[0],size[1],Math.min(12,size[0]/20));
            assertTrue(fit[0]>=0 && fit[1]>=0 && fit[2]<=size[0] && fit[3]<=size[1]);
        }
    }
}
