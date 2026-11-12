# Arquitectura y decisiones

## Android

- `MainActivity.java`: presentación, pestañas, ajustes, permisos, selectores y confirmaciones. El identificador de paquete se mantiene para actualizar V2.
- `ScanModel.java`: biblioteca y operaciones secuenciales en un ExecutorService. Publica resultados mediante LiveData y evita escrituras simultáneas.
- `PdfTools.java`: PDFBox para unión/separación y PDF; PdfRenderer para imágenes; orientación EXIF para fotos.
- `LayoutSpec.java`: dimensiones en puntos, escala uniforme y posición relativa. `LayoutDialog.java` presenta la vista previa; `DocumentOps.layout` exporta la misma geometría.
- `DocumentOps.java`: reemplazos y recuperación, búsqueda de PDF, selección del conjunto de fotos renderizadas.
- `I18n.java`: catálogo local compartido, sin servicio de traducción remoto.

## Windows

- `launcher.py`: punto de entrada; captura errores del autodiagnóstico sin abrir ventanas de fallo.
- `app.py`: controles reutilizables, cámara, recorte por perspectiva, estilo y trabajador Qt. `main` arranca `WindowV3`.
- `v3.py`: interfaz vigente, biblioteca persistente, gestión del dispositivo y confirmación de ampliaciones. `Datos/preferencias.ini` sustituye al registro como almacenamiento de ajustes de V3.
- `layout_editor.py`: composición por página; `core.py`: operaciones PDF, imagen y transacciones, comprobables sin interfaz.
- `i18n.py`: traducciones locales. Conserva el texto fuente de los controles para que cambiar de idioma sea reversible.
- `desktop.spec`: empaquetado PyInstaller. Excluye DLL del sistema y las ICU ajenas encontradas en PATH que causaron el error QtCore de V2.

## Geometría

El modelo utiliza origen arriba a la izquierda, puntos PDF y desplazamientos como fracción de la página. El encaje es `min(anchoPágina/anchoImagen, altoPágina/altoImagen) × escala`. Se centra y después se desplaza. PDF invierte el eje Y al escribir. Se recorta lo que queda fuera del lienzo, sin alterar la proporción de la imagen. Para JPG/PNG, el lienzo adopta la proporción de los píxeles solicitados. Límite: 6000 píxeles por lado y 24 megapíxeles en total.

## Integridad de archivos

Al ampliar, se construye el PDF completo en un temporal del mismo directorio. Se verifica que el original no haya cambiado de tamaño o fecha durante la operación. Después se crea `.recovery` y se sustituye el original. Una copia de recuperación falla antes de reemplazar, no después. El sistema de archivos puede impedir la operación por permisos o falta de espacio; en ese caso se informa del error.

La marca `.exported` solo se escribe tras completar la exportación. `.extended` evita ofrecer el subconjunto antiguo de imágenes como si representase el PDF ampliado. Las firmas digitales quedan invalidadas al modificar el PDF. Es una biblioteca local sencilla, no una base de datos multiusuario ni un sistema de control de versiones.

## Comentarios

Los fuentes contienen comentarios sobre métodos, geometría, permisos, ciclo de vida y transacciones. `CODIGO_COMENTADO.html` añade una explicación de **cada línea**, incluidas líneas estructurales, sin llenar los archivos compilables de comentarios repetitivos. Se abre sin conexión en cualquier navegador. Los comentarios de Java no se incorporan como texto al APK; los comentarios Python se omiten al compilar bytecode. La guía se entrega con el código, separada del ejecutable.
