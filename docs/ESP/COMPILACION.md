# Compilar FolioScan V3.2

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

Resultado: `app/build/outputs/apk/release/app-release.apk`; el script también lo copia como `FolioScan-3.2.apk`.

### Firma y actualizaciones

Esta entrega usa una compilación release **no depurable** y una clave propia de publicación, conservada desde V3.1 corregida. No utiliza signingConfigs.debug.

Las credenciales se leen fuera del repositorio, en `~/.folioscan/signing/release.properties`, o desde la ruta indicada por `FOLIOSCAN_SIGNING_PROPERTIES`. El archivo privado debe contener `storeFile`, `storePassword`, `keyAlias` y `keyPassword`; `storeFile` puede ser relativo a ese archivo. El almacén es PKCS12. No se distribuyen la clave ni sus contraseñas. Si faltan, release falla explícitamente antes de compilar.

Respalda la carpeta privada completa en un soporte cifrado. Para un fork genera tu propia clave y usa otro applicationId. Las instalaciones anteriores firmadas con Android Debug no admiten actualización directa: exporta sus documentos antes de desinstalarlas. V3.1 corregida sí comparte la firma con V3.2.

## Windows

Entorno usado: Python 3.22 de 64 bits. En la carpeta `desktop`:

```powershell
py -3.22 -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
./.venv/Scripts/python.exe launcher.py
./Compilar-Windows.ps1
```

Resultado: `desktop/dist/FolioScan-3.2/FolioScan-3.2.exe`. El script ejecuta las pruebas antes de PyInstaller. `desktop.spec` incluye icono y catálogo de idiomas y filtra DLL del sistema/ICU ajenas. Conserva ese filtro: una DLL ICU incompatible encontrada en PATH causó el fallo de QtCore en V2.

Para verificar el ejecutable sin mostrar ventanas:

```powershell
$folioExe = (Resolve-Path ./dist/FolioScan-3.2/FolioScan-3.2.exe).Path
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

La entrega Windows pasa a onedir: distribuye toda la carpeta `desktop/dist/FolioScan-3.2`, incluido `_internal`, en un ZIP. Los avisos se abren desde Información adicional. Las DLL pueden reemplazarse sin reconstruir FolioScan, respetando ABI, arquitectura y versiones compatibles. Consulta `../../AVISO_QT_LGPL.md`. `Compilar-Windows.ps1 -SkipFunctionalTests` omite las pruebas funcionales cuando el titular las realiza por separado.

`python scripts/prepare_publication.py` prepara candidatos y hashes; no aprueba automáticamente su publicación. Consulta el informe final. `python scripts/generate_bilingual_guide.py` genera las guías ESP/ENG sin reescribir código.
