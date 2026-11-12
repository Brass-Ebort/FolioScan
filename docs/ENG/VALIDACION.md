# FolioScan V3.2 Validation

November 12, 2026. Android: 14 tests passed. Windows: 20 tests passed. Tests cover PDF and image operations, system language and manual language preference, contextual visibility of the paper-format setting, and placement of the acknowledgment. The Windows tests include simulated drag-and-drop events.

Android package: `es.folioscan.app`, version 3.2, `versionCode` 7. The release signing certificate matches the corrected V3.1; it is not Android Debug. The release configuration disables debugging. The distributed executable's self-test results are recorded in `desktop/qa/packaged-v32.json` and `Registros/Validacion`.

Neither a physical camera nor installation on the CMF 2 Pro has been tested. Universal compatibility is not certified. Screenshots of the Windows interface were reviewed; Android was tested using Robolectric, without claiming a visual review on a physical phone.

The rotation test checks landscape/portrait orientation, retention when navigating, independence of pages, scaling/offsets, and swapped PNG dimensions.
