# Privacidad y permisos

FolioScan no incluye cuentas, publicidad, telemetría propia ni un servidor de documentos. PDF, conversiones, composición y búsqueda se ejecutan localmente.

Android usa el escáner de documentos de Google Play Services. Su primera preparación puede descargar componentes mediante Google Play; sus términos y funcionamiento pertenecen a Google. La APK propia no solicita permiso de Internet. El escáner gestiona su cámara mediante Google Play; los permisos del gestor de archivos son independientes.

Para buscar y administrar PDF del teléfono, Android 11 y posteriores solicitan «Acceso a todos los archivos» en el almacenamiento compartido. Android 8–10 utilizan permisos de lectura/escritura. No se accede a datos privados de otras aplicaciones. Se omiten Android/data y Android/obb. Si deniegas el acceso, puedes seguir escaneando y usando los selectores de archivos. La distribución en Google Play exigiría revisar sus políticas de acceso amplio a archivos; este paquete está preparado para instalación directa.

Compartir un documento entrega permisos de lectura a la aplicación elegida. Exportar a un proveedor en la nube desde el selector del sistema puede subirlo por decisión del usuario; FolioScan no controla ese proveedor.

Windows utiliza la webcam con permiso del sistema. Las fotos y PDF se conservan en `Datos` junto al ejecutable o en los destinos elegidos. No se cifran los archivos: quien tenga acceso a esas carpetas podrá leerlos. Los ficheros .recovery contienen la versión anterior del PDF.

La app Android desactiva la copia de seguridad automática de su biblioteca. Exporta antes de desinstalar. En Windows, conserva `Datos` para mantener sesión, biblioteca y ajustes. Elimina también copias y recuperaciones cuando quieras borrar definitivamente un documento.
