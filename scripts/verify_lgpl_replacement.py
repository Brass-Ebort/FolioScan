"""Replace a Qt DLL in an isolated portable copy and verify the loaded bytes.

Only the COFF timestamp is modified: no ABI or algorithm changes. This tests
the replacement mechanism, not arbitrary modified libraries or app features.
"""
from pathlib import Path
import tempfile,shutil,subprocess,struct,hashlib,json
root=Path(__file__).resolve().parents[1]
source=root/'desktop/dist/FolioScan-3.2'
scratch=root/'desktop/build'
scratch.mkdir(exist_ok=True)
folder=Path(tempfile.mkdtemp(prefix='lgpl-replacement-',dir=scratch)).resolve()
assert scratch.resolve() in folder.parents
try:
    target=folder/'FolioScan-3.2';shutil.copytree(source,target)
    report=folder/'baseline.json'
    exe=target/'FolioScan-3.2.exe'
    subprocess.run([str(exe),'--verify-libraries',str(report)],check=True,timeout=60)
    baseline=json.loads(report.read_text('utf-8'));assert baseline['ok']
    library=target/'_internal/PySide6/Qt6Core.dll'
    original=library.read_bytes();modified=bytearray(original)
    offset=struct.unpack_from('<I',modified,0x3c)[0]+8
    old=struct.unpack_from('<I',modified,offset)[0]
    struct.pack_into('<I',modified,offset,(old+1)&0xffffffff)
    library.write_bytes(modified)
    changed=hashlib.sha256(modified).hexdigest()
    assert changed!=hashlib.sha256(original).hexdigest()
    report=folder/'replacement.json'
    subprocess.run([str(exe),'--verify-libraries',str(report)],check=True,timeout=60)
    result=json.loads(report.read_text('utf-8'));assert result['ok']
    core=next(m for m in result['modules'] if m['module']=='Qt6Core.dll')
    assert core['sha256']==changed
    assert core['path']=='_internal/PySide6/Qt6Core.dll'
    output={'ok':True,'baseline':baseline,'replacement':result,
            'modification':'COFF timestamp incremented by one; exports/code unchanged.',
            'limitations':'Does not prove ABI compatibility of arbitrary source changes; no functional tests.',
            'original_distribution_unchanged':hashlib.sha256((source/'_internal/PySide6/Qt6Core.dll').read_bytes()).digest()==hashlib.sha256(original).digest()}
    (root/'legal/lgpl-replacement-verification.json').write_text(json.dumps(output,indent=2),'utf-8')
    print('Replacement verified: the portable executable loaded the modified Qt6Core DLL from its own folder.')
finally:
    assert scratch.resolve() in folder.parents and folder.name.startswith('lgpl-replacement-')
    shutil.rmtree(folder)
