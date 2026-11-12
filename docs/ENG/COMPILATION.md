# Building FolioScan V3.2

Binaries and source files are distributed separately. Comments and the reading guide do not increase the executable size; most of the Windows executable's size comes from Qt, Python, PDFium, and OpenCV.

## Android

You need JDK 17, the Android SDK with platform 35 and Build Tools 35.0.0, and an internet connection to resolve dependencies the first time. Set `JAVA_HOME` and `ANDROID_HOME`, or create `local.properties` with `sdk.dir`. The wrapper pins Gradle 8.11.1; the Android plugin version is pinned in `build.gradle`.

From the project root, in PowerShell:

```powershell
./Compilar.ps1
```

Or directly with the wrapper:

```powershell
./gradlew.bat :app:assembleRelease :app:testDebugUnitTest :app:lintDebug
```

Output: `app/build/outputs/apk/release/app-release.apk`; the script also copies it as `FolioScan-3.2.apk`.

### Signing and Updates

This distribution uses a **non-debuggable** release build and its own release signing key, retained from the corrected V3.1. It does not use `signingConfigs.debug`.

Credentials are read from outside the repository, at `~/.folioscan/signing/release.properties`, or from the path specified by `FOLIOSCAN_SIGNING_PROPERTIES`. The private file must contain `storeFile`, `storePassword`, `keyAlias`, and `keyPassword`; `storeFile` may be relative to that file. The keystore uses PKCS12. Neither the key nor its passwords are distributed. If credentials are missing, the release build fails explicitly before compilation.

Back up the entire private folder to encrypted storage. For a fork, generate your own key and use a different `applicationId`. Previous installations signed with Android Debug cannot be updated directly: export their documents before uninstalling. The corrected V3.1 does share its signing key with V3.2.

## Windows

Environment used: 64-bit Python 3.22. In the `desktop` directory:

```powershell
py -3.22 -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
./.venv/Scripts/python.exe launcher.py
./Compilar-Windows.ps1
```

Output: `desktop/dist/FolioScan-3.2.exe`. The script runs tests before PyInstaller. `desktop.spec` includes the icon and language catalog and filters out unrelated system DLLs/ICU libraries. Keep this filter: an incompatible ICU DLL found on PATH caused the QtCore failure in V2.

To verify the executable without displaying windows:

```powershell
$folioExe = (Resolve-Path ./dist/FolioScan-3.2.exe).Path
$folioReport = Join-Path $PWD 'autodiagnostico.json'
Start-Process -FilePath $folioExe -ArgumentList '--self-test', $folioReport -WindowStyle Hidden -Wait
Get-Content -LiteralPath $folioReport
```

The executable does not require Python to be installed and is not Authenticode-signed. The system may display its usual unknown-publisher warning. Extract the portable application into a writable folder and keep `Datos` when updating the EXE.

## Tests and Documentation

```powershell
./gradlew.bat :app:testDebugUnitTest :app:lintDebug
cd desktop
./.venv/Scripts/python.exe -m unittest test_core test_ui test_v3 test_drop -v
```

Tests use synthetic images and PDFs. They check page order, text preservation, ZIP archives, geometry, recovery, failures, languages, themes, and persistence. Robolectric tests Android without a physical phone. The delivery report lists what was checked and what still requires hardware testing.

To synchronize languages: `python scripts/sync_translations.py`. To regenerate the commented-code guide: `python scripts/document_source.py`. Neither is required to run the prebuilt binaries.

## Publishing

The source ZIP can be extracted into a GitHub repository. The distribution ZIPs and APK are prepared as attachments for a V3 release; they have not been uploaded automatically. Keep LICENSE, NOTICE, and third-party licenses. Do not add keys, `Datos`, real documents, the SDK, `.venv`, or caches to the repository. The complete distribution package includes legal notices and documentation alongside the executable.

In the reorganized directory tree, the current sources are in `herramientas de desarrollo/codigo actual` and JDK/SDK/Gradle are in `herramientas de desarrollo/herramientas`. The scripts detect this layout. Historical versions are kept in `Versiones` and maintenance documentation in `Registros`. Builds regenerate caches and temporary files; these can be cleaned after archiving a release.
