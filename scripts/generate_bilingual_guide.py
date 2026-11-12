"""Regenerate ESP/ENG reading guides without inserting comments into source files."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
script=root/'scripts/document_source.py'
source=script.read_text('utf-8')
start=source.index('for path in files:');end=source.index('def explain(line):',start)
source=source[:start]+source[end:]
source=source.replace('Código comentado V3','Código comentado V3.2').replace('Código V3:','Código V3.2:')
exec(compile(source,str(script),'exec'),{'__file__':str(script),'__name__':'__main__'})
es=(root/'docs/ESP/CODIGO_COMENTADO.html').read_text('utf-8')
translations={
 'Separación visual entre bloques.':'Visual separation between blocks.',
 'Comentario o documentación del comportamiento.':'Comment or behavior documentation.',
 'Cierra el bloque o la expresión iniciados en líneas anteriores.':'Closes a block or expression started on earlier lines.',
 'Importa los tipos o funciones que se usan en este módulo.':'Imports types or functions used by this module.',
 'Identifica el paquete Android al que pertenece esta clase.':'Identifies the Android package of this class.',
 'Anotación o decorador que describe cómo se ejecuta el elemento siguiente.':'Annotation or decorator describing the following element.',
 'Selecciona la rama que corresponde a la condición o al caso indicado.':'Selects the branch for the condition or case.',
 'Recorre los elementos o repite la operación mientras se cumple la condición.':'Iterates through elements or repeats while the condition holds.',
 'Gestiona recursos y errores para cerrar archivos y conservar datos ante fallos.':'Manages resources and errors to close files and preserve data on failure.',
 'Devuelve el resultado o termina esta rama de la operación.':'Returns a result or ends this execution branch.',
 'Interrumpe la operación con un error explícito para que la interfaz lo comunique.':'Raises an explicit error for the interface to report.',
 'Conecta un evento del control con el comportamiento que debe ejecutarse.':'Connects a control event to its handler.',
 'Incorpora un control o grupo a la estructura visual.':'Adds a control or group to the visual structure.',
 'Calcula o conserva el valor indicado; el nombre de la izquierda identifica su destino.':'Computes or stores a value in the named destination.',
 'Declara o invoca la operación indicada; sus argumentos aparecen entre paréntesis.':'Declares or calls an operation with its arguments.',
 'Continúa la declaración o expresión del bloque que la contiene.':'Continues the enclosing declaration or expression.'}
en=es.replace('lang="es"','lang="en"').replace('Código comentado V3.2','Annotated source V3.2').replace('Código V3.2: guía línea por línea','V3.2 source: line-by-line reading guide')
en=re.sub(r'<p>.*?</p>','<p>English syntax notes accompany the original source, whose maintenance comments remain unchanged. These notes are reading aids; algorithm-specific comments take precedence.</p>',en,count=1,flags=re.S)
en=re.sub(r'</pre></td><td>(.*?)</td>',lambda m:'</pre></td><td>'+translations.get(m[1],m[1])+'</td>',en)
(root/'docs/ENG/CODE_GUIDE.html').write_text(en,'utf-8')
