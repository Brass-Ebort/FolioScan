"""Copy only the onefile EXE to an empty folder and test it with a minimal PATH."""
from pathlib import Path
import hashlib, json, os, shutil, subprocess, tempfile

root = Path(__file__).resolve().parents[1]
source = root/'desktop/dist/FolioScan-3.2-portable.exe'
scratch = root/'desktop/build'
folder = Path(tempfile.mkdtemp(prefix='single-exe-check-',dir=scratch)).resolve()
assert scratch.resolve() in folder.parents
try:
    executable = folder/'FolioScan.exe'
    shutil.copy2(source, executable)
    assert len(list(folder.iterdir())) == 1
    environment = os.environ.copy()
    environment['PATH'] = str(Path(os.environ['SystemRoot'])/'System32')
    for key in list(environment):
        if key.startswith(('PYTHON', 'QT_')):
            environment.pop(key)
    for flag, name in [('--self-test','windows-functional-check.json'),
                       ('--verify-libraries','windows-portable-loader.json')]:
        destination = folder/name
        subprocess.run([str(executable),flag,str(destination)],env=environment,
                       cwd=folder,check=True,timeout=90)
        report = json.loads(destination.read_text('utf-8'))
        assert report['ok']
        report['exe_sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
        report['only_exe_copied'] = True
        report['minimal_path'] = True
        (root/'legal'/name).write_text(json.dumps(report,indent=2),'utf-8')
    loader = json.loads((root/'legal/windows-portable-loader.json').read_text('utf-8'))
    provenance = json.loads((root/'legal/microsoft-runtime-provenance.json').read_text('utf-8'))
    for name in ('msvcp140.dll','vcruntime140.dll','vcruntime140_1.dll'):
        module = next(m for m in loader['modules'] if m['module']==name)
        assert '/' not in module['path']  # Relative to the private extraction root.
        expected = next(f['sha256'] for f in provenance['files'] if f['destination']==name)
        assert module['sha256']==expected
    print('Standalone EXE: smoke test and local CRT/Qt/libffi loading verified.')
finally:
    assert scratch.resolve() in folder.parents and folder.name.startswith('single-exe-check-')
    shutil.rmtree(folder)
