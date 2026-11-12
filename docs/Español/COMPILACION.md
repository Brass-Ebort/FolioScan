# Compilar FolioScan V3.1

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

Resultado: `app/build/outputs/apk/release/app-release.apk`; el script también lo copia como `FolioScan-3.1.apk`.

### Firma y actualizaciones

Esta entrega usa una compilación release **no depurable**, firmada con la misma clave local utilizada en V2 para conservar compatibilidad de actualización. La configuración de ejemplo usa `signingConfigs.debug` como origen de esa clave; no convierte la aplicación en depurable. No es una clave de publicación de Google Play.

La clave privada no se incluye en el ZIP ni debe subirse a GitHub. El titular debe respaldar de forma privada la clave local existente de Android antes de mover el entorno. Si otra persona compila desde cero, Gradle generará su propia clave de desarrollo: su APK no podrá actualizar la entrega firmada por el titular. Para publicar un fork usa otro applicationId y tu propia configuración de firma; para futuras actualizaciones oficiales conserva paquete y certificado. No cambies de clave sin planificar la migración.

## Windows

Entorno usado: Python 3.12 de 64 bits. En la carpeta `desktop`:

```powershell
py -3.12 -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
./.venv/Scripts/python.exe launcher.py
./Compilar-Windows.ps1
```

Resultado: `desktop/dist/FolioScan-3.1.exe`. El script ejecuta las pruebas antes de PyInstaller. `desktop.spec` incluye icono y catálogo de idiomas y filtra DLL del sistema/ICU ajenas. Conserva ese filtro: una DLL ICU incompatible encontrada en PATH causó el fallo de QtCore en V2.

Para verificar el ejecutable sin mostrar ventanas:

```powershell
$folioExe = (Resolve-Path ./dist/FolioScan-3.1.exe).Path
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

Para sincronizar idiomas: `python scripts/sync_translations.py`. Para regenerar la guía de comentarios: `python scripts/document_source.py`. No son necesarios para ejecutar los binarios ya construidos.

## Publicación

El ZIP de fuentes se puede descomprimir en un repositorio GitHub. Los ZIP de distribución y la APK están preparados como adjuntos de una release V3; no se han subido automáticamente. Conserva LICENSE, NOTICE y licencias de terceros. No añadas claves, `Datos`, documentos reales, SDK, `.venv` ni cachés al repositorio. El paquete completo de distribución acompaña al ejecutable de sus avisos legales y documentación.

En el árbol reorganizado, los fuentes actuales están en `herramientas de desarrollo/codigo actual` y JDK/SDK/Gradle en `herramientas de desarrollo/herramientas`. Los scripts detectan esa disposición. Las versiones históricas se guardan en `Versiones` y la documentación de mantenimiento en `Registros`. Las compilaciones vuelven a generar cachés y temporales; se pueden limpiar después de archivar una entrega.
