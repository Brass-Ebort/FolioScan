package es.folioscan.app;
import org.junit.Test;
import static org.junit.Assert.*;
public class PageFitTest {
    @Test public void portraitPreservesAspectAndMargins() {
        float[] r = PageFit.fit(2100, 2970, 595, 842, 12);
        assertEquals(2100f / 2970, (r[2]-r[0]) / (r[3]-r[1]), 0.0001);
        assertTrue(r[0] >= 12 && r[1] >= 12 && r[2] <= 583 && r[3] <= 830);
        assertEquals(595, r[0]+r[2], 0.001);
    }
    @Test public void widePhotoIsNotCroppedOrStretched() {
        float[] r = PageFit.fit(4000, 1000, 842, 595, 12);
        assertEquals(4, (r[2]-r[0]) / (r[3]-r[1]), 0.0001);
        assertEquals(12, r[0], 0.001); assertTrue(r[1] > 12);
    }
    @Test(expected=IllegalArgumentException.class) public void rejectsInvalidImages() { PageFit.fit(0, 1, 595, 842, 12); }
}
