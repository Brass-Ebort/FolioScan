# Alcance de la revisión de publicación

Las pruebas funcionales descritas más abajo pertenecen a la entrega anterior V3.2. Por petición del titular, no se vuelven a ejecutar en la revisión legal. El titular comprobará las funciones y el hardware. Aquí se verifican compilación, firma/manifiesto, archivos públicos y carga con una DLL Qt modificada solo en su marca temporal COFF. Esa prueba limitada no certifica modificaciones arbitrarias ni conformidad jurídica. Consulta el informe final de publicación.

# Validación FolioScan V3.2

12 de noviembre de 2026. Android: 14 pruebas superadas. Windows: 20 pruebas superadas. Se comprueban las operaciones PDF y de imagen, el idioma del sistema y la preferencia manual, la visibilidad contextual del formato de papel y la ubicación del agradecimiento. Las pruebas Windows incluyen eventos simulados de arrastrar y soltar.

Paquete Android es.folioscan.app, versión 3.2, versionCode 7. La firma de publicación corresponde a V3.1 corregida; no es Android Debug. La configuración release desactiva la depuración. El autodiagnóstico del ejecutable distribuido queda registrado en desktop/qa/packaged-v32.json y Registros/Validacion.

No se han probado una cámara física ni la instalación en el CMF 2 Pro. No hay certificación de compatibilidad universal. Se revisaron capturas de la interfaz Windows; Android se comprobó mediante Robolectric, sin afirmar una revisión visual en un móvil físico.

La prueba de giro verifica orientación horizontal/vertical, conservación al navegar, independencia de páginas, escala/desplazamiento y dimensiones PNG intercambiadas.
