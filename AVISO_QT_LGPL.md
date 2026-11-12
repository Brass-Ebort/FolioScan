# Qt / PySide6 / Shiboken6 — FolioScan V3.2

## Derechos y alcance

Qt y sus bibliotecas mantienen sus licencias independientes. Para los módulos utilizados se selecciona la opción LGPLv3 donde está disponible. La restricción no comercial de FolioScan no restringe la modificación, sustitución ni redistribución de esas bibliotecas bajo sus propias licencias. Se permite expresamente la ingeniería inversa de FolioScan en lo necesario para depurar modificaciones de las bibliotecas LGPL. No hay comprobaciones de firma o hash que impidan cargar una biblioteca compatible modificada.

Se incluyen los textos completos LGPLv3 y GPLv3, cotejados con GNU, los avisos de los paquetes y los extraídos de las fuentes oficiales 6.12.0. Los avisos de componentes solo presentes en los archivos fuente no significan que esos componentes se enlacen con FolioScan. El inventario real es `legal/windows-binary-inventory.json`.

## Procedencia y fuentes

Qt 6.12.0, PySide6_Essentials 6.12.0 y Shiboken6 6.12.0. Se compararon 240 DLL/PYD instalados con las ruedas oficiales descargadas de PyPI: ningún desajuste. Es una comprobación del entorno; el inventario final identifica el subconjunto distribuido. Los metadatos, hashes y URLs están en `legal/qt-wheel-provenance.json`.

`FolioScan-3.2-fuentes-bibliotecas.zip` debe acompañar a la descarga Windows en la misma Release. Contiene los archivos fuente oficiales íntegros de qtbase, qtsvg, qtimageformats y pyside-setup 6.12.0, incluidos sus scripts de construcción y avisos. `legal/qt-source-archives.json` documenta URLs y SHA-256. No se han modificado las bibliotecas de la distribución original. No se promete una reconstrucción binaria idéntica: la plataforma, compilador y opciones deben ser compatibles.

No sustituir estos archivos por un enlace genérico a Qt. Al publicar, mantener el paquete de fuentes accesible junto al binario, y conservar esa correspondencia en futuras versiones. No se ha publicado ni contratado alojamiento remoto durante esta revisión.

## Reemplazo compatible

1. Cierra FolioScan y conserva una copia de toda la carpeta y de Datos.
2. Usa compilaciones Windows x64 con ABI compatible. La entrega usa Qt 6.12.0 compartido, MSVC 2022 y bindings ABI3 de PySide/Shiboken. Para reconstruir bindings sigue las instrucciones de pyside-setup incluido; mantén coherentes Qt, PySide y Shiboken.
3. Sustituye en `_internal/PySide6` las DLL Qt, `pyside6.abi3.dll`, bindings `.pyd` y plugins afectados; sustituye también `_internal/shiboken6` cuando corresponda. Conserva los subdirectorios de plugins. No basta con renombrar una DLL incompatible. No reemplaces DLL Microsoft con bibliotecas Qt.
4. Ejecuta `FolioScan-3.2.exe --verify-libraries informe.json` desde una carpeta escribible. Este modo comprueba carga de bibliotecas y ciclo de eventos Qt, sin ejecutar operaciones con documentos. Verifica luego las funciones afectadas por tus modificaciones.
5. Si cambia la ABI, utiliza el código de FolioScan y `desktop/Compilar-Windows.ps1` para volver a empaquetar con tu conjunto compatible. No se requiere la clave Android para Windows.

La prueba efectuada está en `legal/lgpl-replacement-verification.json`: una copia aislada cargó Qt6Core.dll después de incrementar su marca temporal COFF; cambió el hash y se verificó la ruta del módulo efectivamente cargado. Se restauró/eliminó la copia de ensayo, no se distribuye la DLL alterada. Esta modificación no cambia algoritmos ni exportaciones: acredita el mecanismo, no la compatibilidad de cualquier modificación de código.

## Estado

La corrección de empaquetado y el acceso a fuentes Qt están preparados. El conjunto Windows **NO está autorizado por esta revisión para publicación** hasta cerrar la trazabilidad y los avisos del runtime nativo que detalla el informe final. Separar DLL o incluir LGPL no resuelve automáticamente las obligaciones de todos los componentes.

Referencias: https://www.qt.io/development/open-source-lgpl-obligations ; https://www.gnu.org/licenses/lgpl-3.0.html ; https://www.gnu.org/licenses/gpl-3.0.html .
