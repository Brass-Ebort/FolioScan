# Privacidad y permisos

FolioScan no incluye cuentas, publicidad, telemetría propia ni un servidor de documentos. PDF, conversiones, composición y búsqueda se ejecutan localmente.

Android usa el escáner de documentos de Google Play Services. Su primera preparación puede descargar componentes mediante Google Play; sus términos y funcionamiento pertenecen a Google. La APK propia no solicita permiso de Internet. El escáner gestiona su cámara mediante Google Play; los permisos del gestor de archivos son independientes.

Desde 0.4.0, la búsqueda normal usa solo Documentos/FolioScan y sus subcarpetas, mediante el selector de carpetas Android. Se pide autorizar Documentos (o directamente FolioScan) una vez y se conserva ese permiso; la aplicación limita su búsqueda a FolioScan. No necesita acceso general al dispositivo. Configuración permite activar el modo de dispositivo completo tras un aviso: Android 11 o posterior pide Acceso a todos los archivos; Android 8–10 pide lectura/escritura. La búsqueda está limitada y se puede cancelar. Desactivar el modo evita usar ese acceso, pero para revocar el permiso de Android debes hacerlo en los ajustes del sistema. No se accede a datos privados de otras aplicaciones. Se omiten Android/data y Android/obb. Google Play requeriría una revisión independiente de sus políticas; esta distribución es para instalación directa.

Compartir un documento entrega permisos de lectura a la aplicación elegida. Exportar a un proveedor en la nube desde el selector del sistema puede subirlo por decisión del usuario; FolioScan no controla ese proveedor.

Windows utiliza la webcam con permiso del sistema. Las fotos y PDF se conservan en `Datos` junto al ejecutable o en los destinos elegidos. No se cifran los archivos: quien tenga acceso a esas carpetas podrá leerlos. Los ficheros .recovery contienen la versión anterior del PDF.

La app Android desactiva la copia de seguridad automática de su biblioteca. Exporta antes de desinstalar. En Windows, conserva `Datos` para mantener sesión, biblioteca y ajustes. Elimina también copias y recuperaciones cuando quieras borrar definitivamente un documento.

Google ML Kit puede comunicar a Google métricas de utilización y rendimiento y descargar correcciones o modelos. Google indica que las imágenes de entrada y los resultados se procesan en el dispositivo y no se envían a sus servidores para procesarlos. La ausencia de permiso INTERNET de FolioScan no impide las comunicaciones de Google Play Services. Consulta https://developers.google.com/ml-kit/terms y https://developers.google.com/ml-kit/android-data-disclosure .
