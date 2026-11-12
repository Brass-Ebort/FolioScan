# Validación FolioScan V3.1

12 de noviembre de 2026. Android: 11 pruebas, incluida selección oscura/clara en ambos temas y contraste de texto. Windows: 19 pruebas, incluidos eventos reales de arrastrar/soltar, importación de un PDF de dos páginas junto a una imagen, tipos por operación, rechazo de directorios/URL y recuperación tras lote defectuoso. Se mantienen las pruebas V3 de geometría, PDF, ZIP, tema e idiomas.

La APK 3.1 usa el paquete es.folioscan.app y versionCode 5; conserva la firma anterior. El EXE se verifica aislado de las carpetas de la distribución, con su autodiagnóstico y las nuevas rutas de importación. Los informes finales se guardan en Registros y la entrega incluye el informe del ejecutable.

No se ha probado una cámara física ni instalado en el CMF 2 Pro. Las pruebas de arrastre utilizan eventos Qt equivalentes a archivos locales; queda por comprobar el gesto desde el Explorador en el equipo del usuario. El gestor PDF no convierte documentos a imágenes salvo que esa operación se elija; importar PDF al escáner sí los rasteriza para editarlos como fotos.
