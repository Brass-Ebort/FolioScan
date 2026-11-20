# GitHub â€” FolioScan V3.2

**Windows se distribuye como un Ãºnico EXE portable, sin instalar dependencias.** Consulte INFORME_FINAL_PUBLICACION.md para los bloqueos cerrados y el alcance de las pruebas. No se ha creado ni modificado un repositorio remoto durante esta revisiÃ³n.

## Actualizar el repositorio

Descomprima FolioScan-V3.2-codigo.zip en una carpeta de trabajo. Su raÃ­z corresponde a la raÃ­z del repositorio. Conserve .git y su configuraciÃ³n local; sustituya los archivos del proyecto por los del ZIP. CAMBIOS_REPOSITORIO.txt enumera exactamente altas, cambios y rutas antiguas retiradas respecto al ZIP de cÃ³digo V3.2 anterior.

Actualice app/src (incluidos assets legales), app/build.gradle si difiere, desktop (fuentes, desktop.spec, scripts y licencias), scripts, shared, legal, README, THIRD_PARTY, AVISO_QT_LGPL y la documentaciÃ³n. Las guÃ­as que antes estaban directamente bajo docs se trasladan a docs/ESP; docs/ENG contiene las equivalentes inglesas. Retire las copias antiguas segÃºn la lista para no dejar instrucciones contradictorias de EXE Ãºnico. Mantenga LICENSE y NOTICE sin cambiar la licencia propia.

El ZIP incluye cÃ³digo, pruebas y wrappers; no necesita incorporar los binarios Android/Windows al Ã¡rbol Git. No suba la carpeta contenedora completa de FolioScan ni Â«herramientas de desarrolloÂ». No publique .folioscan, release.properties, almacenes PKCS12/JKS, contraseÃ±as, Datos, documentos personales, venv, SDK/JDK, cachÃ©s ni build/dist. No elimine su copia privada de firma: es necesaria para las prÃ³ximas actualizaciones.

## Adjuntos de la Release

- FolioScan-3.2.apk: Android con la firma de publicaciÃ³n conservada.
- FolioScan-3.2.exe y FolioScan-3.2-Windows-portable.zip: el mismo ejecutable autÃ³nomo; el ZIP aÃ±ade instrucciones. No necesita _internal externo ni instalar Visual C++. Datos contiene los documentos y preferencias del usuario.
- FolioScan-V3.2-codigo.zip: cÃ³digo propio, documentaciÃ³n ESP/ENG, pruebas y avisos; PolyForm Noncommercial 1.0.0 para cÃ³digo propio, licencias independientes para terceros.
- FolioScan-3.2-fuentes-bibliotecas.zip: fuentes originales exactas Qt/PySide/Shiboken y manifiesto de procedencia/hashes. Debe acompaÃ±ar al binario Windows, no ser una descarga privada ni solo una URL genÃ©rica.
- SHA256SUMS.txt y los documentos legales de acompaÃ±amiento preparados en esta carpeta. Los cierres incluyen evidencia tÃ©cnica del 18/11/2026.

Los ZIP de fuentes de Qt incluyen cÃ³digo de herramientas auxiliares sujeto a sus propias licencias. Eso no significa que esas herramientas se enlacen con FolioScan; no las relicencie como PolyForm. No publique las ruedas descargadas ni los duplicados de compilaciÃ³n, que solo sirvieron como evidencia local.

## Texto de presentaciÃ³n

Â«FolioScan: escÃ¡ner de documentos y herramientas PDF para Android y Windows, con procesamiento local y sin anuncios. CÃ³digo disponible para uso no comercial.Â»

Evite Â«open sourceÂ» en sentido OSI, Â«ningÃºn dato sale del telÃ©fonoÂ» y Â«cumplimiento certificadoÂ». Explique que ML Kit puede comunicar mÃ©tricas tÃ©cnicas y que sus documentos se procesan localmente. El EXE Windows funciona por sÃ­ solo; para trasladar documentos y preferencias, copiar tambiÃ©n Datos.

## Verificar antes de subir

Compruebe los SHA-256 de los paquetes que realmente adjuntarÃ¡. Si recompila o modifica un archivo, regenere los hashes. Compruebe los enlaces pÃºblicos a fuentes y avisos y utilice el EXE generado en esta entrega. Las pruebas automÃ¡ticas Windows han pasado; complete las pruebas manuales de webcam y en otro equipo. Redistribuya el EXE o ZIP original, sin incluir los documentos de Datos. Los distribuidores deben conservar los avisos y cumplir las condiciones de los componentes Microsoft incluidas.

Actualice desktop/requirements.txt junto con el resto del cÃ³digo para que Dependabot reevalÃºe las alertas. Esta revisiÃ³n no ha cerrado alertas remotas.
