"""Archiva la entrega actual sin SDK, entornos virtuales ni documentos personales."""
from pathlib import Path
import hashlib
import shutil
import zipfile
import json
import re
import xml.etree.ElementTree as ET

root=Path(__file__).resolve().parents[1]
project=root.parents[1] if root.name=='codigo actual' else root
version=re.search(r"versionName '([^']+)'",(root/'app/build.gradle').read_text('utf-8'))[1]
release=project/'Versiones'/('V'+version)
source_dir=release/'Codigo';docs_dir=release/'Fuentes'
android=release/'Distribucion/Android';windows=release/'Distribucion/Windows'
for folder in [source_dir,docs_dir,android,windows]:folder.mkdir(parents=True,exist_ok=True)
report=root/'desktop/qa/packaged-v32.json'
assert json.loads(report.read_text('utf-8-sig'))['ok']
reports=list((root/'app/build/test-results/testDebugUnitTest').glob('TEST-*.xml'))
assert reports
for file in reports:
    result=ET.parse(file).getroot();assert int(result.attrib['failures'])==0 and int(result.attrib['errors'])==0

for source,destination in [(root/f'FolioScan-{version}.apk',android/f'FolioScan-{version}.apk'),(root/f'desktop/dist/FolioScan-{version}.exe',windows/f'FolioScan-{version}.exe')]:
    shutil.copy2(source,destination)
    assert hashlib.sha256(source.read_bytes()).digest()==hashlib.sha256(destination.read_bytes()).digest()
docs=['README.md','LICENSE','NOTICE','THIRD_PARTY.md','CHANGELOG.md','CONTRIBUTING.md']
for name in docs:shutil.copy2(root/name,docs_dir/name)
shutil.copytree(root/'docs',docs_dir/'docs',dirs_exist_ok=True)
shutil.copytree(root/'desktop/licenses',docs_dir/'licencias',dirs_exist_ok=True)
shutil.copy2(root/'desktop/scanner.png',docs_dir/'icono.png')
entries=[(root/name,name) for name in docs]
for directory in ['app/src','gradle','docs','desktop/licenses']:
    entries += [(path,path.relative_to(root).as_posix()) for path in (root/directory).rglob('*') if path.is_file()]
for name in ['.gitignore','build.gradle','settings.gradle','gradle.properties','app/build.gradle','Compilar.ps1','gradlew','gradlew.bat','shared/translations.tsv','scripts/sync_translations.py','scripts/document_source.py','scripts/package_current.py']:
    entries.append((root/name,name))
entries += [(path,'desktop/'+path.name) for path in (root/'desktop').glob('*.py')]
for name in ['arrow-dark.png','arrow-light.png','requirements.txt','scanner.png','desktop.spec','version_info.txt','Compilar-Windows.ps1','translations.tsv']:
    entries.append((root/'desktop'/name,'desktop/'+name))
for name in ['foto.png','v3-claro.png','v3-oscuro.png','v3-editor.png','packaged-v32.json','v32-imagenes.png','v32-gestor.png','v32-informacion.png']:
    path=root/'desktop/qa'/name
    if path.is_file():entries.append((path,'desktop/qa/'+name))
archive=source_dir/f'FolioScan-V{version}-codigo.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as package:
    for path,name in sorted(entries,key=lambda item:item[1]):
        assert not any(part in name.split('/') for part in ['Datos','.venv','__pycache__','.gradle','build'])
        package.write(path,name)
with zipfile.ZipFile(archive) as package:assert package.testzip() is None
files=[archive,android/f'FolioScan-{version}.apk',windows/f'FolioScan-{version}.exe']
(release/'SHA256SUMS.txt').write_text('\n'.join(hashlib.sha256(path.read_bytes()).hexdigest()+'  '+path.relative_to(release).as_posix() for path in files)+'\n','utf-8')
print(json.dumps({'release':str(release),'files':[str(path) for path in files]},ensure_ascii=False))
