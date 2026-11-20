# Validation scope — V3.2 publication review

The previous V3.2 sheet-rotation build passed 14 Android tests and 20 Windows tests. Those results are historical evidence for that earlier build, not new functional validation of the publication candidates.

Update 2026-11-20: 21 Windows tests pass, including consent/cancellation with synthetic test terms. The standalone EXE is checked with its smoke test, bundled DLL loading and Qt replacement test. Android is unchanged. Physical webcam and clean Windows tests remain outstanding.

The review does check release compilation, dependency inventories, legal text integrity, APK identity/signature/debug flag, public-file hashes and an isolated DLL-replacement procedure. The replacement check changes only a Qt6Core DLL COFF timestamp, then verifies that the packaged application loads that changed DLL and runs a Qt event loop. It does not prove compatibility of arbitrary modified library code.

The previous blockers are addressed by traceable libffi and unmodified release CRT from the installed Visual Studio Community, under its redistribution terms. The runtime is bundled; no end-user installation is needed. Tests are not legal certification.
