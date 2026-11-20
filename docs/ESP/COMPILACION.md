# Compilar FolioScan 0.4.0

Los binarios y los fuentes se entregan por separado. Los comentarios y la guía de lectura no aumentan el tamaño del ejecutable; la mayor parte del tamaño de Windows son Qt, Python, PDFium y OpenCV.

## Android

Necesitas JDK 17, Android SDK con plataforma 35 y Build Tools 35.0.0, y conexión para resolver las dependencias la primera vez. Configura `JAVA_HOME` y `ANDROID_HOME` o crea `local.properties` con `sdk.dir`. El wrapper fija Gradle 8.11.1; el plugin Android está fijado en `build.gradle`.

Desde la raíz, en PowerShell:

```powershell
./Compilar.ps1
```

O con el wrapper directamente:

```powershell
./gradlew.bat :app:assembleRelease :app:testDebugUnitTest :app:lintDebug
```

Resultado: `app/build/outputs/apk/release/app-release.apk`. El empaquetado de publicación lo nombra `FolioScan-0.4.0.apk` en su carpeta de entrega.

### Firma y actualizaciones

Esta entrega usa una compilación release **no depurable** y una clave propia de publicación, conservada desde V3.1 corregida. No utiliza signingConfigs.debug.

Las credenciales se leen fuera del repositorio, en `~/.folioscan/signing/release.properties`, o desde la ruta indicada por `FOLIOSCAN_SIGNING_PROPERTIES`. El archivo privado debe contener `storeFile`, `storePassword`, `keyAlias` y `keyPassword`; `storeFile` puede ser relativo a ese archivo. El almacén es PKCS12. No se distribuyen la clave ni sus contraseñas. Si faltan, release falla explícitamente antes de compilar.

Respalda la carpeta privada completa en un soporte cifrado. Para un fork genera tu propia clave y usa otro applicationId. Las instalaciones anteriores firmadas con Android Debug no admiten actualización directa: exporta sus documentos antes de desinstalarlas. V3.1 corregida sí comparte la firma con V3.2.

## Windows

Entorno usado: Python 3.12 de 64 bits. En la carpeta `desktop`:

```powershell
py -3.12 -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
./.venv/Scripts/python.exe launcher.py
./Compilar-Windows.ps1
```

Resultado: `desktop/dist/FolioScan-0.4.0-portable.exe`. El script ejecuta las pruebas antes de PyInstaller. `desktop.spec` incluye icono y catálogo de idiomas y filtra DLL del sistema/ICU ajenas. Conserva ese filtro: una DLL ICU incompatible encontrada en PATH causó el fallo de QtCore en V2.

Para verificar el ejecutable sin mostrar ventanas:

```powershell
$folioExe = (Resolve-Path ./dist/FolioScan-0.4.0-portable.exe).Path
$folioReport = Join-Path $PWD 'autodiagnostico.json'
Start-Process -FilePath $folioExe -ArgumentList '--self-test', $folioReport -WindowStyle Hidden -Wait
Get-Content -LiteralPath $folioReport
```

El ejecutable no necesita Python instalado y no tiene firma Authenticode. El sistema puede mostrar su aviso habitual de editor desconocido. Extrae el portable en una carpeta escribible y conserva `Datos` al actualizar el EXE.

## Pruebas y documentación

```powershell
./gradlew.bat :app:testDebugUnitTest :app:lintDebug
cd desktop
./.venv/Scripts/python.exe -m unittest test_core test_ui test_v3 test_drop -v
```

Las pruebas usan imágenes y PDF sintéticos. Comprueban orden de páginas, preservación de texto, ZIP, geometría, recuperación, fallos, idiomas, tema y persistencia. Robolectric verifica Android sin un teléfono físico. El informe de entrega enumera qué se comprobó y qué necesita prueba en hardware.

Para sincronizar idiomas: `python scripts/sync_translations.py`. Para regenerar ambas guías sin modificar los fuentes: `python scripts/generate_bilingual_guide.py`. No son necesarios para ejecutar los binarios ya construidos.

## Publicación

El ZIP de fuentes se puede descomprimir en un repositorio GitHub. Los ZIP y la APK son candidatos; no deben publicarse mientras el informe final mantenga bloqueos. No se han subido automáticamente. Conserva LICENSE, NOTICE y licencias de terceros. No añadas claves, `Datos`, documentos reales, SDK, `.venv` ni cachés al repositorio. El paquete completo de distribución acompaña al ejecutable de sus avisos legales y documentación.

En el árbol reorganizado, los fuentes actuales están en `herramientas de desarrollo/codigo actual` y JDK/SDK/Gradle en `herramientas de desarrollo/herramientas`. Los scripts detectan esa disposición. Las versiones históricas se guardan en `Versiones` y la documentación de mantenimiento en `Registros`. Las compilaciones vuelven a generar cachés y temporales; se pueden limpiar después de archivar una entrega.

## Revisión de publicación

La entrega Windows es `desktop/dist/FolioScan-0.4.0-portable.exe`, un único archivo autónomo. La carpeta onedir solo sirve para auditoría de binarios. Bibliotecas permite reemplazos LGPL compatibles; consulta `../../AVISO_QT_LGPL.md`.

`python scripts/prepare_publication.py` prepara candidatos y hashes; no aprueba automáticamente su publicación. Consulta el informe final. `python scripts/generate_bilingual_guide.py` genera las guías ESP/ENG sin reescribir código.

## Runtime Windows
Para compilar se requiere Visual Studio Community 2026 con derechos de redistribución. Los scripts verifican libffi y toman el CRT release de VC/Redist. El usuario final no instala dependencias. Publica mediante scripts/prepare_publication.py.

Para compilar Windows se necesita una instalación estable de Visual Studio Community 2026 con derechos de redistribución del CRT. Los scripts preparan libffi y las DLL release verificadas. El usuario final no instala ese runtime. Antes de empaquetar ejecuta verify_portable.py, verify_lgpl_replacement.py y audit_windows_binary_inventory.py desde scripts; prepare_publication.py comprueba sus informes y genera la carpeta de entrega.
