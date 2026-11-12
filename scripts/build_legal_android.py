"""Build an offline legal page from audited runtime evidence and original notices."""
from pathlib import Path
import html,json,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1]
inventory=json.loads((root/'legal/android-license-inventory.json').read_text('utf-8'))
parts=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FolioScan — Licenses / Licencias</title><style>body{font:16px sans-serif;padding:16px;line-height:1.5}pre{white-space:pre-wrap;overflow-wrap:anywhere}h2{margin-top:2em}</style><h1>FolioScan V3.2 — Licenses / Licencias</h1>']
parts+=['<p>Document processing happens on-device. Google ML Kit may download components and send technical usage/performance metrics to Google; document inputs and outputs are not sent to Google for processing. / Los documentos se procesan en el dispositivo. Google ML Kit puede descargar componentes y comunicar métricas técnicas de uso y rendimiento; no envía las entradas y resultados a Google para procesarlos.</p>',
        '<p><a href="https://developers.google.com/ml-kit/terms">ML Kit terms and privacy</a> · <a href="https://developer.android.com/studio/terms">Google SDK terms</a> · <a href="https://developers.google.com/terms">Google API terms</a></p>']
def section(title,text):
    parts.append('<h2>'+html.escape(title)+'</h2><pre>'+html.escape(text)+'</pre>')
for name in ['LICENSE','NOTICE']:
    section(name,(root/name).read_text('utf-8'))
parts.append('<h2>Production dependencies / Dependencias de producción</h2><ul>')
for item in inventory:
    label='; '.join(x['name'] for x in item['licenses'])
    if item['id']=='com.google.guava:listenablefuture:1.0':label='Apache-2.0 (Guava parent 26.0-android POM)'
    parts.append('<li>'+html.escape(item['id']+' — '+label)+'</li>')
parts.append('</ul>')
for name in ['apache','pdfbox-license','pdfbox-notice','bouncycastle']:
    section(name,(root/f'legal/upstream/{name}.txt').read_text('utf-8'))
# Preserve the bundled Google OSS notices and all other extracted attributions.
for item in json.loads((root/'legal/android-notices/index.json').read_text('utf-8')):
    text=(root/'legal/android-notices'/item['file']).read_text('utf-8')
    if text.strip():section(item['origin'],text)
parts.append('</html>')
(root/'app/src/main/assets/legal.html').write_text('\n'.join(parts),'utf-8')
