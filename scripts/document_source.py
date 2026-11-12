"""Add Spanish maintenance notes and produce a navigable line-by-line source guide.

This generator never changes executable statements. The guide also explains
structural lines, which would be noisy as repeated comments in the source itself.
"""
import ast
import html
import re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
notes={
 'main':'Arranca la aplicación o ejecuta el autodiagnóstico sin ventanas.',
 'configure_fonts':'Carga fuentes locales para mostrar los mismos glifos en la interfaz y las pruebas.',
 'append_pdf':'Construye un PDF nuevo, comprueba cambios externos y conserva el original como .recovery antes de reemplazarlo.',
 'append':'Une las páginas en un temporal; el aviso de sobrescritura se gestiona en la interfaz.',
 'layout_box':'Calcula el rectángulo de la imagen conservando proporciones; x e y son fracciones del tamaño de página.',
 'box':'Calcula el encaje proporcional y aplica escala y desplazamiento sin estirar la imagen.',
 'layout_pdf':'Genera cada página con sus dimensiones y convierte el eje vertical de pantalla al de PDF.',
 'layout_images':'Rasteriza solo el lienzo final para limitar memoria incluso con ampliaciones grandes.',
 'discover_pdfs':'Recorre las carpetas elegidas sin seguir enlaces simbólicos; omite directorios ocultos.',
 'discover':'Busca PDF accesibles; la interfaz obtiene los permisos antes de llamar a esta operación.',
 'page_size':'Convierte milímetros a puntos PDF (72 por pulgada) y adapta la orientación.',
 'fit_box':'Encaja la imagen dentro de los márgenes sin deformarla.',
 'atomic_output':'Escribe en un temporal del mismo directorio y publica el resultado solo cuando se completa.',
 'reader':'Abre el PDF y rechaza documentos vacíos o protegidos antes de procesarlos.',
 'merge_pdfs':'Concatena páginas conservando texto y recursos del PDF, sin convertirlo en fotografías.',
 'split_pdf':'Escribe un PDF por página dentro de un ZIP; conserva el orden del original.',
 'pdf_to_images':'Renderiza cada página y añade su imagen al ZIP de salida.',
 'normalized_image':'Aplica orientación EXIF y compone transparencias sobre blanco antes del procesamiento.',
 'images_to_pdf':'Convierte imágenes ordenadas a páginas PDF con el formato solicitado.',
 'export_photos':'Crea fotos individuales en el destino elegido sin modificar las imágenes de origen.',
 'detect_corners':'Propone cuatro bordes a partir de contornos; el usuario puede corregirlos manualmente.',
 'rectify_image':'Valida las cuatro esquinas y aplica una homografía; no reconstruye texto oculto por pliegues.',
 'scanner_tab':'Construye los controles de captura, previsualización y edición del escáner.',
 'pdf_tab':'Construye el gestor de PDF y conecta las cuatro operaciones disponibles.',
 'operation_changed':'Vacía la selección anterior para no mezclar tipos de archivo entre operaciones.',
 'persist_session':'Actualiza el manifiesto de páginas con reemplazo atómico para poder reabrir la sesión.',
 'import_scan':'Normaliza las fotos importadas y las incorpora a la lista de páginas.',
 'camera':'Abre la captura de cámara y añade las fotos obtenidas a la sesión.',
 'crop':'Abre el editor de cuatro esquinas y conserva el resultado como una nueva imagen.',
 'rotate':'Gira la imagen seleccionada 90 grados y actualiza su previsualización.',
 'move':'Cambia el orden de una página; el orden visible será el orden exportado.',
 'save_scan_pdf':'Abre la composición posterior al escaneo y prepara una copia en la biblioteca local.',
 'refresh_library':'Muestra únicamente documentos completos que aún no tienen marca de exportación.',
 'export_draft':'Pregunta el destino y marca como exportado solamente después de guardar con éxito.',
 'roots':'Recupera las carpetas de búsqueda configuradas para este equipo.',
 'remember_root':'Añade una carpeta a la búsqueda sin duplicar entradas existentes.',
 'choose_root':'Pide al usuario una carpeta accesible y actualiza los resultados.',
 'search_device':'Busca PDF fuera del hilo gráfico para que la ventana siga respondiendo.',
 'library_menu':'Ofrece acciones sobre la ruta del documento seleccionado, no sobre su etiqueta visible.',
 'rename_document':'Valida el nombre y evita reemplazar otro archivo al renombrar.',
 'delete_document':'Pide confirmación; limita el borrado recursivo a una carpeta propia de la biblioteca.',
 'append_menu':'Permite elegir entre añadir PDF existentes o las páginas actuales del escáner.',
 'append_from_pdf':'Selecciona los documentos que se añadirán al PDF original.',
 'append_from_scan':'Compone primero las nuevas páginas; solo después solicita reemplazar el original.',
 'confirm_append':'Presenta la advertencia explícita de sobrescritura antes de ejecutar la transacción.',
 'run_job':'Deshabilita acciones mientras trabaja el hilo y entrega resultados cuando este termina.',
 'settings_menu':'Despliega tema, permisos, idioma y ayuda sin un botón redundante de cierre.',
 'choose_language':'Persiste el idioma seleccionado y actualiza la interfaz con el catálogo local.',
 'closeEvent':'Impide cerrar durante una escritura y conserva preferencias y sesión.',
 'paintEvent':'Dibuja la previsualización usando la misma geometría que la exportación.',
 'mousePressEvent':'Registra el punto inicial del arrastre en coordenadas del control.',
 'mouseMoveEvent':'Convierte el movimiento del puntero a coordenadas normalizadas de la hoja.',
 'mouseReleaseEvent':'Termina el arrastre y sincroniza los valores de los controles.',
 'number_field':'Crea una entrada numérica con límites explícitos para evitar tamaños inválidos.',
 'load_page':'Carga la imagen de la página activa y presenta sus ajustes independientes.',
 'load_controls':'Sincroniza controles sin disparar cambios que sobrescriban el modelo.',
 'changed':'Pasa los valores de los controles al modelo y redibuja el resultado.',
 'paper_changed':'Actualiza el papel seleccionado y calcula una resolución inicial acotada.',
 'center':'Restablece el encaje proporcional centrado de la imagen.',
 'all_pages':'Copia los ajustes actuales a todas las páginas sin compartir objetos mutables.',
 'change':'Cambia de página conservando los ajustes de la anterior.',
 'accept':'Valida el tamaño final antes de confirmar el editor.',
 'preview_scan':'Actualiza la miniatura sin cambiar el archivo ni su resolución original.',
 'destination':'Usa el diálogo nativo para elegir carpeta y nombre en cada exportación.',
 'need_images':'Detiene la operación y explica cómo añadir páginas cuando la sesión está vacía.',
 'add_tools':'Selecciona PDF o imágenes según la operación activa.',
 'process_tools':'Despacha la operación elegida después de pedir un destino.',
 'completed':'Notifica el resultado e incluye una acción para abrir su carpeta.',
 'failed':'Muestra el error sin simular que la operación se ha completado.',
 'finish_job':'Vuelve a habilitar las acciones después de finalizar el trabajo.',
 'toggle_theme':'Invierte la preferencia de tema y la guarda para la próxima apertura.',
 'apply_theme':'Aplica una paleta coherente a fondos, texto, botones y selección.',
 'help':'Muestra instrucciones y límites reales del escaneo y la exportación.',
 'start':'Abre la cámara disponible y comienza la actualización periódica de la imagen.',
 'tick':'Obtiene un fotograma y lo convierte al formato de visualización de Qt.',
 'take':'Guarda el fotograma actual y lo añade a las capturas de esta sesión.',
 'done':'Detiene el temporizador y libera el dispositivo de cámara.',
 'apply':'Aplica el recorte solicitado o muestra el error si las esquinas no son válidas.',
 'onCreate':'Restaura preferencias, registra resultados del sistema y construye la interfaz.',
 'onSaveInstanceState':'Conserva selecciones y operaciones pendientes durante una recreación de Android.',
 'buildUi':'Construye la pantalla con pestañas compactas, respetando tema y márgenes del sistema.',
 'startScan':'Solicita la interfaz de escaneo de Google Play y limita la sesión a 50 páginas.',
 'refresh':'Reconstruye la lista de documentos visibles según la pestaña de biblioteca.',
 'options':'Abre las acciones del documento interno seleccionado.',
 'openPdf':'Entrega al visor externo un URI temporal con permiso de lectura.',
 'share':'Comparte únicamente los archivos elegidos mediante permisos de lectura limitados.',
 'rename':'Valida el nombre antes de cambiar la carpeta del documento.',
 'delete':'Pide confirmación antes de borrar los archivos internos del documento.',
 'settings':'Abre el panel lateral de ajustes; tocar fuera o volver lo cierra.',
 'searchDevice':'Solicita permisos si faltan y busca en el almacenamiento compartido accesible.',
 'refreshDevice':'Muestra los PDF encontrados con su carpeta para distinguir nombres repetidos.',
 'deviceMenu':'Gestiona un PDF del almacenamiento compartido sin importarlo a la biblioteca.',
 'addPages':'Recuerda el PDF de destino y permite añadir un nuevo escaneo o archivos PDF.',
 'editLayout':'Abre el editor posterior al escaneo y entrega sus ajustes al trabajador.',
 'confirmAppend':'Requiere confirmación explícita antes de sustituir el PDF seleccionado.',
 'prepareAppend':'Copia los URI seleccionados al caché y prepara las páginas adicionales.',
 'chooseLanguage':'Guarda uno de los once idiomas y recrea la interfaz con la nueva selección.',
 'addFooter':'Añade el agradecimiento y el enlace al perfil indicado por el autor.',
 'showInfo':'Explica uso, privacidad, recuperación y límites del reconocimiento de documentos.',
 'replace':'Crea la copia de recuperación y reemplaza el archivo con el resultado ya completo.',
 'layout':'Genera PDF e imágenes con la misma geometría empleada por la previsualización.',
 'exportImages':'Resuelve el conjunto de imágenes renderizadas; recurre a las originales si no hay otro.',
 'validate':'Rechaza dimensiones o resoluciones fuera de los límites de memoria establecidos.',
 'copy':'Copia los valores de composición para mantener ajustes independientes por página.',
 'processPdf':'Procesa la herramienta elegida en segundo plano y publica el resultado pendiente de guardar.',
 'save':'Copia los resultados del escáner a almacenamiento privado antes de ofrecer su edición.',
 'export':'Escribe el archivo seleccionado en el URI de destino concedido por Android.',
 'exportPhotos':'Crea una imagen por hoja en la carpeta autorizada y marca el documento al finalizar.',
 'initialize':'Inicializa los recursos de PDFBox y configura su directorio temporal.',
 'process':'Copia las entradas a caché y ejecuta la conversión sin modificar los originales.',
 'merge':'Concatena las páginas PDF conservando recursos y texto.',
 'split':'Introduce un PDF independiente por página dentro del ZIP de salida.',
 'render':'Convierte cada página a imagen con resolución acotada para controlar la memoria.',
 'decode':'Lee una imagen con muestreo de resolución y corrige su orientación EXIF.',
 'imagesToPdf':'Convierte la lista de imágenes en un documento PDF ordenado.',
 't':'Busca el texto traducido localmente; las cadenas desconocidas conservan su valor original.',
 'load':'Lee el catálogo de idiomas una vez y selecciona la preferencia persistida.',
}
files=list((root/'desktop').glob('*.py'))+list((root/'app/src/main/java').rglob('*.java'))
for path in files:
    if path.name.startswith('test_'):continue
    text=path.read_text('utf-8');lines=text.splitlines();insert={}
    if path.suffix=='.py':
        for node in ast.walk(ast.parse(text)):
            if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name in notes:
                insert[node.lineno-1]=' '*node.col_offset+'# '+notes[node.name]
    else:
        for i,line in enumerate(lines):
            match=re.match(r'\s*(?:public|private|protected|static|final|synchronized|void|File|int|float|boolean|String|Bitmap|List<[^>]+>)[\w\s<>,\[\]]*\s+(\w+)\(',line)
            if match and match[1] in notes:insert[i]=' '* (len(line)-len(line.lstrip()))+'// '+notes[match[1]]
    for i in sorted(insert,reverse=True):
        if i==0 or lines[i-1].strip()!=insert[i].strip():lines.insert(i,insert[i])
    path.write_text('\n'.join(lines)+'\n','utf-8')

def explain(line):
    """Explain syntax as a reading aid; algorithm comments above remain authoritative."""
    s=line.strip()
    if not s:return 'Separación visual entre bloques.'
    if s.startswith(('#','//','/*','*','"""')):return 'Comentario o documentación del comportamiento.'
    if s in ('}',');',')',']','};'):return 'Cierra el bloque o la expresión iniciados en líneas anteriores.'
    if s.startswith(('import ','from ')):return 'Importa los tipos o funciones que se usan en este módulo.'
    if s.startswith('package '):return 'Identifica el paquete Android al que pertenece esta clase.'
    if s.startswith('@'):return 'Anotación o decorador que describe cómo se ejecuta el elemento siguiente.'
    if re.search(r'\b(if|else|elif|switch|case)\b',s):return 'Selecciona la rama que corresponde a la condición o al caso indicado.'
    if re.search(r'\b(for|while)\b',s):return 'Recorre los elementos o repite la operación mientras se cumple la condición.'
    if s.startswith(('try','except','catch','finally','with')):return 'Gestiona recursos y errores para cerrar archivos y conservar datos ante fallos.'
    if re.search(r'\b(return|yield)\b',s):return 'Devuelve el resultado o termina esta rama de la operación.'
    if re.search(r'\b(throw|raise)\b',s):return 'Interrumpe la operación con un error explícito para que la interfaz lo comunique.'
    if '.connect(' in s or 'setOn' in s:return 'Conecta un evento del control con el comportamiento que debe ejecutarse.'
    if re.search(r'(addWidget|addView|addLayout|setContentView)',s):return 'Incorpora un control o grupo a la estructura visual.'
    if '=' in s:return 'Calcula o conserva el valor indicado; el nombre de la izquierda identifica su destino.'
    if '(' in s:return 'Declara o invoca la operación indicada; sus argumentos aparecen entre paréntesis.'
    return 'Continúa la declaración o expresión del bloque que la contiene.'

out=root/'docs';out.mkdir(exist_ok=True)
parts=['<!doctype html><html lang="es"><meta charset="utf-8"><title>Código comentado V3</title><style>body{font:15px system-ui;margin:30px}table{border-collapse:collapse;width:100%}td{padding:5px;border-bottom:1px solid #ddd;vertical-align:top}pre{margin:0;white-space:pre-wrap}summary{font-size:20px;margin:24px 0;cursor:pointer}td:first-child{color:#777;width:45px}td:last-child{width:32%}</style><h1>Código V3: guía línea por línea</h1><p>El código contiene comentarios de mantenimiento en español. Esta vista añade una explicación sintáctica de cada línea, incluidos cierres de bloque. Las notas junto a los algoritmos describen sus decisiones y tienen prioridad sobre la descripción sintáctica general.</p>']
for path in files:
    parts.append('<details><summary>'+html.escape(str(path.relative_to(root)))+'</summary><table>')
    for n,line in enumerate(path.read_text('utf-8').splitlines(),1):parts.append(f'<tr><td>{n}</td><td><pre>{html.escape(line)}</pre></td><td>{html.escape(explain(line))}</td></tr>')
    parts.append('</table></details>')
parts.append('</html>');(out/'CODIGO_COMENTADO.html').write_text('\n'.join(parts),'utf-8')
