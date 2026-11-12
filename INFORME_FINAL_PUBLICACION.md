# Revisión final FolioScan V3.2 — 12 de noviembre de 2026

## Conclusión: NO LISTO PARA PUBLICAR

Los candidatos están preparados, pero la revisión no cierra la procedencia exacta de libffi ni la base documental de redistribución de los runtimes Microsoft. No publique la Release completa hasta resolver esos puntos. No se ha publicado ni enviado ningún archivo a GitHub.

## Cambios realizados

- Integrado el parche de licencias después de examinar sus 12 entradas. README conserva las novedades V3.2 y el giro de hoja. LICENSE/PolyForm y NOTICE se conservan; los textos PolyForm, LGPLv3 y GPLv3 coinciden con los oficiales al normalizar espacios y saltos de línea.
- Windows cambia de onefile a onedir: EXE y DLL accesibles, conservando Datos junto al EXE. Se añade acceso a avisos desde Información adicional. No se puede trasladar solamente el EXE.
- Descargadas las fuentes oficiales completas de qtbase, qtsvg, qtimageformats y pyside-setup 6.12.0, con URL/SHA-256. Se ofrecen en un paquete separado para acompañar al ZIP Windows en la misma Release.
- Comparados 240 binarios DLL/PYD del entorno PySide/Shiboken con sus ruedas originales de PyPI: ningún desajuste. El paquete final contiene un subconjunto, inventariado por ruta y hash; no se confunde el entorno de construcción con lo realmente distribuido.
- Excluidos del paquete el backend FFmpeg sin uso (captura por DirectShow), el fallback Mesa/OpenGL sin uso y datos ICU huérfanos. No se cambia el código de cámara ni el procesamiento de documentos. Los demás componentes mantienen sus avisos originales, incluidos avisos de terceros incorporados en las fuentes Qt y en las ruedas.
- Inventario Gradle: 63 artefactos de producción, 60 coordenadas únicas. Conservados POM y 22 avisos integrados; añadidos los textos oficiales PDFBox Android v2.0.27.0, Bouncy Castle r1rv72 y Apache-2.0. ListenableFuture se resuelve mediante el POM padre Guava 26.0-android.
- Android incorpora una página local de licencias, accesible en Configuración, con JavaScript desactivado. Incluye aviso de las métricas técnicas de ML Kit y enlaces a las condiciones Google. La apertura de referencias externas corresponde a una acción del usuario.
- Documentación agrupada en docs/ESP y docs/ENG, con guías de compilación, arquitectura, privacidad, validación y lectura del código. Los comentarios del código original se conservan; las explicaciones de la guía se ofrecen en ambos idiomas. Los textos jurídicos originales no se sustituyen por traducciones.
- Modificaciones permanentes en el código y scripts de compilación/empaquetado. Las versiones históricas y los archivos personales no se han modificado. No se regenera ninguna clave.

## Verificaciones técnicas

La revisión ejecuta compilación release Android y empaquetado Windows, no las pruebas funcionales que el titular ha reservado para sí. Los 14 tests Android y 20 Windows de la entrega anterior son antecedentes; no se presentan como resultados de estos candidatos.

La prueba LGPL trabaja sobre una copia aislada. Incrementa únicamente la marca temporal COFF de Qt6Core.dll, manteniendo código y exportaciones. El EXE vuelve a cargar Qt, crea un QWidget y procesa eventos; se comprueban la ruta efectiva y el hash de la DLL cargada. El resultado demuestra sustitución de un binario compatible con hash distinto, no compatibilidad de cualquier modificación ni compilación desde fuentes de una variante funcionalmente distinta. Las bibliotecas originales del paquete permanecen sin modificar. Véase legal/lgpl-replacement-verification.json y el procedimiento reproducible.

El APK conserva es.folioscan.app, versionName 3.2 y versionCode 7. El informe de firma documenta la coincidencia con V3.1 corregida, ausencia de Android Debug y depuración desactivada. La actualización directa exige firma coincidente: las APK antiguas de debug siguen siendo incompatibles. Las nuevas licencias no cambian la identidad de la aplicación.

Los hashes de publicación se calculan después de preparar los paquetes. El código público se selecciona mediante lista de rutas permitidas: sin venv, SDK/JDK/Gradle descargados, build/dist, Datos, claves ni documentos de usuario. El único fixture JPG Android conservado es una imagen blanca sintética. Los informes de QA históricos y sus documentos se excluyen. Se comprueban ausencia de la contraseña de firma, de almacenes privados y de rutas personales propias en archivos de texto públicos; no se muestran credenciales. Los binarios de terceros pueden conservar sus cadenas de compilación originales, que no se modifican para ocultarlas.

## Bloqueos concretos y cómo cerrarlos

1. **libffi-8.dll:** no contiene una versión verificable ni se encontró un manifiesto del runtime Python de desarrollo que atribuya ese binario a un paquete fuente concreto. El nombre DLL no acredita versión ni avisos. La licencia MIT de referencia incluida no sustituye esa prueba. Obtener del proveedor el manifiesto/build y sus avisos exactos, o compilar/obtener un runtime Python/libffi trazable; reemplazarlo de forma compatible, volver a empaquetar y verificar hashes/carga. La URL de una supuesta distribución embebible oficial Python 3.12.14 devolvió 404: no se inventa equivalencia con ella.
2. **Microsoft Visual C++:** se identifican las DLL y su origen en ruedas/runtime, pero no se ha archivado la licencia concreta que respalde su redistribución por el titular ni confirmado todos sus requisitos. Obtener los términos aplicables y cotejar cada DLL (incluida la copia renombrada en numpy.libs) con la lista redistribuible. Si no existe autorización, obtener una distribución autorizada o elegir otra estrategia de runtime. No quitar DLL necesarias ni imponerles PolyForm/LGPL. Referencia oficial: https://learn.microsoft.com/en-us/visualstudio/releases/2022/redistribution .

Estos son pendientes de licencia/procedencia, no pruebas manuales de cámara; por eso la conclusión no es «listo con comprobaciones manuales pendientes». El inventario no demuestra por sí mismo conformidad de todos los binarios. El titular debe además confirmar los derechos del icono aportado antes de publicarlo.

## Comprobaciones del titular

Tras cerrar los bloqueos: instalar/actualizar el APK firmado, probar captura real, giro de hoja, formatos PDF/JPG/PNG, combinación/separación, guardado y permisos; probar Windows y webcam, portabilidad de la carpeta completa y Datos, y acceso a avisos. No se ha instalado en el CMF 2 Pro ni probado una cámara física. No se ha hecho una auditoría de seguridad ni una certificación jurídica.

## Fuentes y evidencias

- Evidencias locales: legal/*.json, POM y avisos originales; scripts de inventario y sustitución en el ZIP de código.
- Qt: https://www.qt.io/development/open-source-lgpl-obligations y archivos de fuentes exactos listados en legal/qt-source-archives.json.
- GNU: https://www.gnu.org/licenses/lgpl-3.0.txt y https://www.gnu.org/licenses/gpl-3.0.txt .
- PolyForm: https://polyformproject.org/licenses/noncommercial/1.0.0.txt .
- Google: https://developers.google.com/ml-kit/terms y https://developer.android.com/studio/terms .
- PDFBox: https://github.com/TomRoush/PdfBox-Android/tree/v2.0.27.0 .
- Bouncy Castle: https://github.com/bcgit/bc-java/blob/r1rv72/LICENSE.html .

Las licencias se conservan; no se promete ausencia de obligaciones fuera del alcance verificado. Los materiales quedan como candidatos revisados, no como autorización para publicar los binarios Windows.
