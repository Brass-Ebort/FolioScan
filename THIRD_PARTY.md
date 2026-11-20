# Componentes de terceros

La licencia no comercial de FolioScan solo abarca su código y los materiales que el titular pueda licenciar. No sustituye ni restringe licencias de terceros. Los textos recogidos de los paquetes se distribuyen en `licenses/` dentro de las descargas y en `desktop/licenses/` dentro del código.

| Componente | Uso | Licencia / origen |
|---|---|---|
| AndroidX y PDFBox Android | Interfaz, EXIF y PDF | Apache-2.0; repositorios oficiales AndroidX y Tom Roush/PdfBox-Android |
| Google ML Kit Document Scanner / Play Services | Captura Android | Términos de Google; componente externo, no código propio de FolioScan |
| Qt / PySide6 / Shiboken6 | Interfaz Windows | LGPL-3.0, GPL y licencias de componentes según los avisos incluidos |
| pypdf | Unión y separación PDF | BSD-3-Clause |
| PDFium / pypdfium2 | Renderizado PDF | Licencias BSD/Apache y avisos de terceros incluidos en el paquete |
| Pillow | Imágenes | HPND y avisos incluidos |
| ReportLab | Generación PDF | BSD y avisos incluidos |
| OpenCV / NumPy | Cámara y corrección de perspectiva | Apache/BSD y avisos incluidos |
| Python | Intérprete de la versión Windows | PSF y avisos de su distribución |
| PyInstaller | Empaquetado | GPL con excepción para ejecutables distribuidos |

Las versiones exactas de Windows constan en `desktop/requirements.txt`; las de Android en `app/build.gradle`. No se empaquetan fuentes de Windows: se utilizan las disponibles en el sistema.

## Estado de la revisión V3.2

Los textos LGPLv3/GPLv3 del parche fueron cotejados con GNU; LICENSE coincide con el texto oficial de PolyForm Noncommercial 1.0.0 sin cambiar sus términos. Se conservaron los avisos originales de los paquetes, incluso el aviso comercial de Qt, y se añadieron los textos y avisos de la opción LGPL extraídos de fuentes oficiales. No se afirma que cualquier módulo de Qt pueda usarse bajo LGPL: el inventario limita la distribución a los módulos identificados.

Windows se entrega como un único EXE portable. Los avisos integrados se extraen temporalmente y se abren desde Información adicional. Consulte [AVISO_QT_LGPL.md](AVISO_QT_LGPL.md) para fuentes y sustitución mediante la carpeta opcional Bibliotecas.

El inventario nativo final y sus hashes están en `legal/windows-binary-inventory.json`. Los metadatos del entorno incluyen herramientas de compilación que no necesariamente se distribuyen. Los 240 binarios Qt/PySide/Shiboken comparados corresponden al entorno de las ruedas originales, no a 240 binarios dentro de la entrega.

Se excluyen FFmpeg (la webcam usa DirectShow), Mesa/OpenGL software (la aplicación usa QWidget raster) y una DLL de datos ICU huérfana de las ICU ajenas previamente excluidas. No se distribuyen estos componentes sin utilizar. No se alteró el código de captura ni el procesamiento de documentos.

Android: 63 artefactos de ejecución correspondientes a 60 coordenadas únicas, resueltos por Gradle. `legal/android-license-inventory.json` y los POM originales documentan las licencias. Se conservaron 22 avisos integrados y se añadieron LICENSE/NOTICE oficiales PDFBox Android v2.0.27.0 (incluidos recursos Adobe), licencia Bouncy Castle r1rv72 y Apache-2.0. Guava ListenableFuture hereda Apache-2.0 de guava-parent 26.0-android. ML Kit y Play Services mantienen sus términos Google; sus enlaces y el aviso de métricas están en la página legal integrada y accesible sin conexión. No se presentan las dependencias Google como código propio ni como código abierto.

## Comprobaciones no cerradas

libffi 3.4.4 amd64 procede del repositorio oficial python/cpython-bin-deps, commit 94cb9a1c7feb608adf2b9f8fe2dbd6925ffbf90d. Se incluye el LICENSE exacto de ese commit: copyright 1996–2022 Anthony Green, Red Hat, Inc and others, permiso MIT. URL y SHA-256 en legal/libffi-provenance.json. La copia anterior de origen no acreditado no se distribuye.

Se incluyen DLL release de Microsoft Visual C++ obtenidas del directorio VC/Redist de la instalación estable Visual Studio Community 2026 del titular. Se verifican firmas y bytes; no se incluyen debug_nonredist ni componentes preview. Véase legal/microsoft-runtime-provenance.json y los términos originales en desktop/licenses/Native. Se usan los derechos de la licencia Community para el desarrollo individual de esta aplicación y la lista oficial: https://learn.microsoft.com/en-us/visualstudio/releases/2026/redistribution . Los usuarios aceptan las condiciones del runtime al primer inicio. Los distribuidores deben mantener esas protecciones, avisos y condiciones y distribuirlos solo como parte de la aplicación. FolioScan aporta la funcionalidad principal. No se aplica PolyForm ni LGPL a las DLL Microsoft, ni se modifican sus bytes. El nombre alternativo de NumPy conserva exactamente el mismo contenido.
