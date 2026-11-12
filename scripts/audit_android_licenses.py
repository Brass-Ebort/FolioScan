"""Collect runtime POM evidence and embedded notices without publishing cache paths."""
from pathlib import Path
import json, zipfile, io, html, hashlib, xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
cache = Path.home() / '.gradle/caches/modules-2/files-2.1'
items = json.loads((root/'legal/android-dependencies.json').read_text('utf-8'))
notices = {}
def inspect(data, origin, depth=0):
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for name in archive.namelist():
            basename = Path(name).name.lower()
            if not name.endswith('/') and any(k in basename for k in ['license', 'notice', 'copying', 'copyright']):
                value = archive.read(name)
                if b'\x00' not in value:
                    notices[origin+' / '+name] = value.decode('utf-8', errors='replace')
            elif name.endswith('.jar') and depth < 2:
                inspect(archive.read(name), origin+' / '+name, depth+1)

for item in items:
    group, artifact, version = item['id'].split(':')
    folder = cache/group/artifact/version
    poms = list(folder.glob('*/*.pom'))
    item['licenses'] = []
    if poms:
        tree = ET.parse(poms[0])
        item['pom_sha256'] = hashlib.sha256(poms[0].read_bytes()).hexdigest()
        item['licenses'] = [dict(name=n.findtext('{*}name'), url=n.findtext('{*}url'))
                            for n in tree.findall('.//{*}licenses/{*}license')]
        target=root/'legal/android-poms'/f'{group}.{artifact}-{version}.pom'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(poms[0].read_bytes())
    for candidate in folder.glob('*/'+item['file']):
        if candidate.suffix in ['.aar', '.jar']:
            inspect(candidate.read_bytes(), item['id'])
    if not item['licenses']:
        item['review_required'] = 'POM has no license; consult embedded notice/upstream parent.'

(root/'legal/android-license-inventory.json').write_text(json.dumps(items, ensure_ascii=False, indent=2), 'utf-8')
directory=root/'legal/android-notices';directory.mkdir(parents=True,exist_ok=True)
index=[]
for n,(origin,content) in enumerate(sorted(notices.items()),1):
    filename=f'{n:03}.txt';(directory/filename).write_text(content,'utf-8')
    index.append(dict(origin=origin,file=filename,sha256=hashlib.sha256((directory/filename).read_bytes()).hexdigest()))
(directory/'index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),'utf-8')
print(f'{len(items)} runtime artifacts; {len(notices)} embedded notices; '+
      str([i['id'] for i in items if not i['licenses']]))
