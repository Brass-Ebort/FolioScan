# GitHub — FolioScan V3.2

**No publique todavía la Release completa:** consulte INFORME_FINAL_PUBLICACION.md y cierre sus dos bloqueos de runtime. No se ha creado ni modificado un repositorio remoto durante esta revisión.

## Actualizar el repositorio

Descomprima FolioScan-V3.2-codigo.zip en una carpeta de trabajo. Su raíz corresponde a la raíz del repositorio. Conserve .git y su configuración local; sustituya los archivos del proyecto por los del ZIP. CAMBIOS_REPOSITORIO.txt enumera exactamente altas, cambios y rutas antiguas retiradas respecto al ZIP de código V3.2 anterior.

Actualice app/src (incluidos assets legales), app/build.gradle si difiere, desktop (fuentes, desktop.spec, scripts y licencias), scripts, shared, legal, README, THIRD_PARTY, AVISO_QT_LGPL y la documentación. Las guías que antes estaban directamente bajo docs se trasladan a docs/ESP; docs/ENG contiene las equivalentes inglesas. Retire las copias antiguas según la lista para no dejar instrucciones contradictorias de EXE único. Mantenga LICENSE y NOTICE sin cambiar la licencia propia.

El ZIP incluye código, pruebas y wrappers; no necesita incorporar los binarios Android/Windows al árbol Git. No suba la carpeta contenedora completa de FolioScan ni «herramientas de desarrollo». No publique .folioscan, release.properties, almacenes PKCS12/JKS, contraseñas, Datos, documentos personales, venv, SDK/JDK, cachés ni build/dist. No elimine su copia privada de firma: es necesaria para las próximas actualizaciones.

## Adjuntos de la Release, solo después del cierre

- FolioScan-3.2.apk: Android con la firma de publicación conservada.
- FolioScan-3.2-Windows-portable.zip: carpeta completa; el EXE necesita _internal. Para conservar datos, trasladar también Datos.
- FolioScan-V3.2-codigo.zip: código propio, documentación ESP/ENG, pruebas y avisos; PolyForm Noncommercial 1.0.0 para código propio, licencias independientes para terceros.
- FolioScan-3.2-fuentes-bibliotecas.zip: fuentes originales exactas Qt/PySide/Shiboken y manifiesto de procedencia/hashes. Debe acompañar al binario Windows, no ser una descarga privada ni solo una URL genérica.
- SHA256SUMS.txt y los documentos legales de acompañamiento preparados en esta carpeta. El informe final debe actualizarse con evidencia real al cerrar los bloqueos; no quitar simplemente la advertencia.

Los ZIP de fuentes de Qt incluyen código de herramientas auxiliares sujeto a sus propias licencias. Eso no significa que esas herramientas se enlacen con FolioScan; no las relicencie como PolyForm. No publique las ruedas descargadas ni los duplicados de compilación, que solo sirvieron como evidencia local.

## Texto de presentación

«FolioScan: escáner de documentos y herramientas PDF para Android y Windows, con procesamiento local y sin anuncios. Código disponible para uso no comercial.»

Evite «open source» en sentido OSI, «ningún dato sale del teléfono» y «cumplimiento certificado». Explique que ML Kit puede comunicar métricas técnicas y que sus documentos se procesan localmente. No indique que el EXE Windows funciona separado de su carpeta.

## Verificar antes de subir

Compruebe los SHA-256 de los paquetes que realmente adjuntará. Si recompila o modifica un archivo, regenere los hashes. Compruebe que los enlaces a fuentes y avisos funcionan desde la Release pública, que la documentación no conserva pendientes ya resueltos sin evidencia, y que no adjunta el EXE antiguo onefile por error. Complete las pruebas funcionales que ha reservado para usted.
