# Validation scope — V3.2 publication review

The previous V3.2 sheet-rotation build passed 14 Android tests and 20 Windows tests. Those results are historical evidence for that earlier build, not new functional validation of the publication candidates.

At the owner's request, no application functional test suite or physical camera test is run during this licensing review. The owner will verify scanning, PDF operations, UI, translations, saving and installation.

The review does check release compilation, dependency inventories, legal text integrity, APK identity/signature/debug flag, public-file hashes and an isolated DLL-replacement procedure. The replacement check changes only a Qt6Core DLL COFF timestamp, then verifies that the packaged application loads that changed DLL and runs a Qt event loop. It does not prove compatibility of arbitrary modified library code.

No claim is made that the APK was installed on the Nothing CMF 2 Pro or that a real webcam was tested. The final publication report lists unresolved legal/provenance checks separately from functional checks. A completed build or a passing loader check must not be treated as legal clearance.
