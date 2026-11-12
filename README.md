# FolioScan

**A free, straightforward document scanner and PDF toolkit for Android and Windows(portable). No ads. No subscriptions.**

**Languages:** [English](#english) · [Español](#español)

---

## English

### Why FolioScan?

I made FolioScan because scanning a document and saving it as a PDF shouldn't require watching ads, signing up, or paying a subscription. Other apps offer great, often more advanced features, and I respect the work behind them. **FolioScan is simply my attempt to make the basics easy and accessible.**

### Features

- **Android:** scan one or several pages with Google ML Kit Document Scanner (up to 50 per session); adjust borders, rotate and reorder pages.
- **Windows:** import photos or capture them with a camera; manually correct perspective, rotate, reorder, and drag and drop supported files.
- **Both:** export to PDF, JPG or PNG; merge PDFs, extract pages and convert between PDFs and images; adjust page size and layout; manage documents in a local library. Light/dark themes and multiple languages are available.

Features may work differently on each platform. Windows camera support has not been tested on every device.

### Privacy and transparency

**Document content is processed locally, without automatic uploads to FolioScan servers.** The app has no ads, accounts, subscriptions or built-in analytics of its own. A review of the available source code did not identify custom document-upload or telemetry mechanisms; this is **not** a certification or a complete security audit.

On Android, scanning uses **Google ML Kit via Google Play Services**. Google's documentation states that document images and scan results are processed on-device. Google Play Services can download necessary components and communicate technical usage, performance and diagnostic metrics to Google. These are distinct from the scanned document content. Files you choose to share through other apps are handled by those apps.

More information: [ML Kit Document Scanner](https://developers.google.com/ml-kit/vision/doc-scanner) · [ML Kit terms](https://developers.google.com/ml-kit/terms) · [Android data disclosure](https://developers.google.com/ml-kit/android-data-disclosure).

### Made with AI assistance

**FolioScan was vibe-coded**, using AI-assisted programming tools extensively. I'd rather be open about that. The source is available so anyone can inspect how the app works, review dependencies, report issues or suggest improvements. Public code makes independent review possible; it doesn't automatically make software secure.

### Availability and license

- **Android:** Android 8.0+ on compatible devices with the required Google services.
- **Windows:** portable x64 application, tested in a Windows 11 environment.
- **Downloads:** release packages will be added to this repository's **Releases** section when published. The repository is not evidence that an app-store release exists.

FolioScan's original code is available under **[PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0)**: you may inspect and use it subject to its noncommercial terms. Third-party libraries have their own licenses. This is **source-available**, not OSI-defined *open source*. The full `LICENSE` file should accompany the published code.

**Created by [Brass-Ebort](https://github.com/Brass-Ebort).**

---

## Español

### ¿Por qué FolioScan?

Creé FolioScan porque escanear un documento y guardarlo como PDF no debería exigir ver anuncios, registrarse o pagar una suscripción. Hay aplicaciones excelentes, a menudo con funciones mucho más avanzadas, y valoro el trabajo que hay detrás. **FolioScan es simplemente mi forma de hacer que lo esencial sea fácil y accesible.**

### Funciones

- **Android:** escanea una o varias páginas con Google ML Kit Document Scanner (hasta 50 por sesión); ajusta bordes, gira y reordena las páginas.
- **Windows:** importa fotografías o captúralas con una cámara; corrige manualmente la perspectiva, gira y ordena páginas, y arrastra archivos compatibles.
- **Ambas versiones:** exporta a PDF, JPG o PNG; une PDF, extrae páginas y convierte entre PDF e imágenes; ajusta tamaños y disposición de página; organiza documentos en una biblioteca local. Incluye temas claro/oscuro y varios idiomas.

Algunas funciones se realizan de forma diferente según la plataforma. La cámara de Windows no se ha probado en todos los dispositivos.

### Privacidad y transparencia

**El contenido de los documentos se procesa localmente, sin subidas automáticas a servidores de FolioScan.** La aplicación no tiene anuncios, cuentas, suscripciones ni analítica propia. En la revisión del código fuente disponible no se identificaron mecanismos propios para subir documentos ni de telemetría; esto **no** constituye una certificación ni una auditoría completa de seguridad.

En Android, el escaneo utiliza **Google ML Kit mediante Google Play Services**. Según la documentación de Google, las imágenes y los resultados del escaneo se procesan en el dispositivo. Google Play Services puede descargar componentes necesarios y comunicar a Google métricas técnicas de uso, rendimiento y diagnóstico, distintas del contenido escaneado. Los archivos que decidas compartir con otras aplicaciones pasarán a estar gestionados por ellas.

Más información: [ML Kit Document Scanner](https://developers.google.com/ml-kit/vision/doc-scanner) · [Condiciones de ML Kit](https://developers.google.com/ml-kit/terms) · [Información sobre datos en Android](https://developers.google.com/ml-kit/android-data-disclosure).

### Desarrollada con ayuda de IA

**FolioScan está desarrollada mediante *vibe coding***, con un uso amplio de herramientas de programación asistida por inteligencia artificial. Prefiero contarlo abiertamente. El código está disponible para que cualquiera pueda examinar cómo funciona, revisar sus dependencias, comunicar errores o proponer mejoras. Publicarlo facilita la revisión independiente, aunque no constituye por sí mismo una garantía de seguridad.

### Disponibilidad y licencia

- **Android:** Android 8.0 o posterior, en dispositivos compatibles con los servicios de Google necesarios.
- **Windows:** aplicación portable para x64, probada en un entorno Windows 11.
- **Descargas:** los paquetes se incorporarán al apartado **Releases** de este repositorio cuando se publiquen. La existencia del repositorio no implica que la aplicación esté publicada en una tienda.

El código original de FolioScan está disponible bajo **[PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0)**: puedes consultarlo y utilizarlo respetando sus condiciones de uso no comercial. Las bibliotecas de terceros conservan sus propias licencias. Es software de **código disponible**, no *código abierto* según la definición de la OSI. El archivo completo `LICENSE` debe acompañar al código publicado.

**Creada por [Brass-Ebort](https://github.com/Brass-Ebort).**
