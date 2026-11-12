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

## Derechos sobre Qt/PySide y otras bibliotecas LGPL

Se permite expresamente modificar o sustituir las bibliotecas LGPL y realizar ingeniería inversa de FolioScan cuando sea necesario para depurar tales modificaciones, conforme a LGPL. Ninguna restricción no comercial del código propio reduce esos derechos sobre las bibliotecas.

La entrega de fuentes incluye los archivos necesarios para volver a empaquetar la aplicación con bibliotecas Qt/PySide modificadas. Crea el entorno, instala tu versión compatible de las bibliotecas y ejecuta `desktop/Compilar-Windows.ps1`; no hay verificación que impida sustituirlas. Para desarrollo puedes ejecutar directamente `desktop/launcher.py` sin empaquetar.

Fuentes originales: [Qt](https://code.qt.io/), [PySide / Shiboken](https://code.qt.io/cgit/pyside/pyside-setup.git/), [pypdfium2](https://github.com/pypdfium2-team/pypdfium2), [PDFium](https://pdfium.googlesource.com/pdfium/), [PDFBox Android](https://github.com/TomRoush/PdfBox-Android), [ML Kit](https://developers.google.com/ml-kit/vision/doc-scanner). Selecciona la etiqueta correspondiente a la versión indicada en los manifiestos. Los textos de licencia incluidos en las distribuciones son los aplicables a cada componente.
