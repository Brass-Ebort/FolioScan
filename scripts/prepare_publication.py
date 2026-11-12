"""Prepare review candidates without modifying historical releases or publishing online."""
from pathlib import Path
import hashlib,json,re,shutil,zipfile
root=Path(__file__).resolve().parents[1]
project=root.parents[1] if root.name=='codigo actual' else root
version=re.search(r"versionName '([^']+)'",(root/'app/build.gradle').read_text('utf-8'))[1]
output=project/f'PUBLICAR_FOLIOSCAN_V{version}'
output.mkdir(exist_ok=True)
windows=root/f'desktop/dist/FolioScan-{version}'
apk=root/'app/build/outputs/apk/release/app-release.apk'
assert windows.is_dir() and apk.is_file()
signature=json.loads((root/'legal/android-signature.json').read_text('utf-8-sig'))
assert signature['matches_corrected_v31'] and not signature['debuggable']
assert signature['apk_sha256'].lower()==hashlib.sha256(apk.read_bytes()).hexdigest()
assert json.loads((root/'legal/lgpl-replacement-verification.json').read_text('utf-8'))['ok']

# External legal files are accessible through the application and the file manager.
legal=windows/'_internal/legal'
for name in ['LICENSE','NOTICE','THIRD_PARTY.md','AVISO_QT_LGPL.md']:
    shutil.copy2(root/name,legal/name)
shutil.copytree(root/'desktop/licenses',legal/'dependencies',dirs_exist_ok=True)
shutil.copytree(root/'legal',legal/'audit',dirs_exist_ok=True)
shutil.copy2(root/'INFORME_FINAL_PUBLICACION.md',legal/'INFORME_FINAL_PUBLICACION.md')
(windows/'LEEME.txt').write_text('FolioScan '+version+' — candidato pendiente de revisión legal.\nConserve toda la carpeta, incluido _internal. Abra FolioScan-'+version+'.exe.\nDatos contiene sus documentos y preferencias. Avisos: _internal/legal.\nConsulte INFORME_FINAL_PUBLICACION.md antes de redistribuir.\n','utf-8')
shutil.copy2(apk,output/f'FolioScan-{version}.apk')
with zipfile.ZipFile(output/f'FolioScan-{version}-Windows-portable.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(windows.rglob('*')):
        if p.is_file():
            assert 'Datos' not in p.relative_to(windows).parts
            z.write(p,windows.name+'/'+p.relative_to(windows).as_posix())

# Exact upstream source archives accompany the Windows binary, not wheel duplicates.
source_manifest=json.loads((root/'legal/qt-source-archives.json').read_text('utf-8'))
cache=root.parent/'herramientas/fuentes-licencias'
with zipfile.ZipFile(output/f'FolioScan-{version}-fuentes-bibliotecas.zip','w',zipfile.ZIP_STORED) as z:
    z.write(root/'legal/qt-source-archives.json','MANIFEST.json')
    z.write(root/'AVISO_QT_LGPL.md','AVISO_QT_LGPL.md')
    for item in source_manifest:
        p=cache/item['file']
        assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']
        z.write(p,p.name)

top=['.gitignore','LICENSE','NOTICE','README.md','THIRD_PARTY.md','AVISO_QT_LGPL.md',
     'INFORME_FINAL_PUBLICACION.md','INSTRUCCIONES_GITHUB.md','CONTRIBUTING.md','CHANGELOG.md',
     'build.gradle','settings.gradle','gradle.properties','Compilar.ps1','gradlew','gradlew.bat']
entries={name:root/name for name in top}
for directory in ['app/src','gradle','shared','docs','legal','scripts','desktop/licenses']:
    for p in (root/directory).rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:
            entries[p.relative_to(root).as_posix()]=p
entries['app/build.gradle']=root/'app/build.gradle'
for p in (root/'desktop').iterdir():
    if p.is_file() and p.suffix.lower() in ['.py','.png','.spec','.ps1','.tsv','.txt']:
        entries[p.relative_to(root).as_posix()]=p
# Never publish caches, real documents, credentials or build output as source.
assert not any(any(x in name.split('/') for x in ['Datos','.venv','.gradle']) for name in entries)
assert not any(name.startswith(('build/','dist/','app/build/','desktop/build/','desktop/dist/')) for name in entries)
assert not any(Path(name).suffix.lower() in ['.p12','.pfx','.jks','.keystore'] for name in entries)
archive=output/f'FolioScan-V{version}-codigo.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for name,p in sorted(entries.items()):z.write(p,name)

# Exact replacement list for GitHub; compare without altering the archived version.
baseline=project/f'Versiones/V{version}/Codigo/FolioScan-V{version}-codigo.zip'
changes=[]
if baseline.exists():
    with zipfile.ZipFile(baseline) as old:
        old_names=set(old.namelist())
        for name,p in sorted(entries.items()):
            if name not in old_names:changes.append('AÑADIR '+name)
            elif hashlib.sha256(old.read(name)).digest()!=hashlib.sha256(p.read_bytes()).digest():changes.append('ACTUALIZAR '+name)
        changes+=['RETIRAR DEL REPOSITORIO (no del archivo histórico) '+name for name in sorted(old_names-set(entries))]
(output/'CAMBIOS_REPOSITORIO.txt').write_text('\n'.join(changes)+'\n','utf-8')
for name in ['README.md','LICENSE','NOTICE','THIRD_PARTY.md','AVISO_QT_LGPL.md',
             'INFORME_FINAL_PUBLICACION.md','INSTRUCCIONES_GITHUB.md']:
    shutil.copy2(root/name,output/name)

for p in output.glob('*.zip'):
    with zipfile.ZipFile(p) as z:assert z.testzip() is None
(output/'SHA256SUMS.txt').write_text('\n'.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name
    for p in sorted(output.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt')+'\n','utf-8')
print(json.dumps({'folder':str(output),'status':'NO LISTO PARA PUBLICAR','source_files':len(entries)},ensure_ascii=False))
