# Building FolioScan V3.2

Read the final publication report before distributing binaries. The current publication review has unresolved native-runtime provenance/redistribution questions; successful compilation alone is not release approval.

## Android

Use JDK 17, Android SDK platform 35 and Build Tools 35.0.0. Set JAVA_HOME and ANDROID_HOME, or supply a local.properties file containing sdk.dir. Gradle dependencies require network access on their first resolution. The wrapper pins Gradle 8.11.1.

Run `./Compilar.ps1` in PowerShell. It builds release, runs the existing Android tests and lint, checks the signature and debug flag, then copies the APK into the source directory. To build without functional tests, run `./gradlew.bat :app:assembleRelease`; independently verify the APK before distributing it. During the publication review, functional tests were deliberately left to the owner.

Release credentials are external to the repository: `~/.folioscan/signing/release.properties`, or the file selected by FOLIOSCAN_SIGNING_PROPERTIES. Required fields are storeFile, storePassword, keyAlias and keyPassword. The PKCS12 store path may be relative to the properties file. Never commit either file. Missing credentials stop release compilation; debug signing is not a fallback. Keep encrypted offline backups of both the store and credentials. Forks should use their own applicationId and signing key.

The package remains es.folioscan.app, versionName 3.2, versionCode 7. Its publication certificate is the one used for corrected V3.1. Earlier Android Debug releases cannot be updated directly: export documents before uninstalling them, since uninstalling deletes the private library. A key or package change breaks the normal update path.

## Windows

The development environment uses Python 3.12 x64 and the exact dependencies in desktop/requirements.txt. Build the existing application; do not recreate the frontend.

```powershell
cd desktop
py -3.12 -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
./.venv/Scripts/python.exe launcher.py
./Compilar-Windows.ps1
```

`-SkipFunctionalTests` skips the application test suite when explicitly requested. The output is now `desktop/dist/FolioScan-3.2/`, containing the EXE and `_internal`. Keep the whole folder. It does not require Python to be installed on the user's PC. It is portable but no longer a standalone single-file EXE. Personal settings/documents go in Datos next to the EXE. The EXE has no Authenticode signature.

The spec excludes unrelated system/ICU DLLs found on PATH. It also excludes the unused FFmpeg video backend (the camera explicitly uses DirectShow) and the Mesa software OpenGL fallback (the interface uses raster QWidget controls). These exclusions do not establish hardware compatibility; the owner performs camera and functional testing.

## Legal inventory and library replacement

Run the Gradle audit init script to regenerate the production dependency inventory, then scripts/audit_android_licenses.py and scripts/build_legal_android.py. Cached Maven artifacts must be available. See the JSON evidence in legal/.

The Windows build produces replaceable DLLs. `scripts/audit_windows_binary_inventory.py` inventories the final folder, rather than assuming every package in the build environment is shipped. `scripts/verify_lgpl_replacement.py` makes an isolated copy, modifies only the PE/COFF timestamp of Qt6Core.dll, executes the portable loader check, confirms the loaded path/hash and removes its temporary copy. It does not test arbitrary ABI changes or scanner/PDF functionality. See ../../AVISO_QT_LGPL.md for compatible replacement and source availability.

## Documentation and packaging

`scripts/sync_translations.py` validates/copies the shared offline catalogue. `scripts/generate_bilingual_guide.py` regenerates documentation without changing application sources. `scripts/prepare_publication.py` prepares the public candidate folder and SHA-256 hashes; it does not approve a release or upload anything.

Do not publish SDK/JDK/Gradle downloads, build caches, virtual environments, Datos, personal files or signing material. Source comments and the separate reading guide do not increase the compiled application size significantly; most Windows size comes from its runtime libraries.
