"""Inventory the final onedir binaries, preserving relative paths and SHA-256."""
from pathlib import Path
import hashlib,json,importlib.metadata as metadata,pefile
root=Path(__file__).resolve().parents[1]
package=root/'desktop/dist/FolioScan-3.2'
records=[]
for p in sorted(package.rglob('*')):
    if not p.is_file() or p.suffix.lower() not in ['.dll','.pyd','.exe']:continue
    rel=p.relative_to(package).as_posix();lower=rel.lower()
    if 'shiboken6' in lower and p.name.lower() not in ['msvcp140.dll','vcruntime140.dll','vcruntime140_1.dll']:
        component='Shiboken6 6.12.0';basis='LGPL-3.0 option; pyside-setup 6.12.0 sources and notices'
    elif 'pyside6' in lower and p.name.lower().startswith(('msvcp','vcruntime')):
        component='Microsoft Visual C++ runtime';basis='Microsoft redistributable terms; bundled by upstream wheel'
    elif 'pyside6' in lower:
        if p.name.lower().startswith(('qt6svg','qsvg')):module='qtsvg'
        elif p.name.lower() in ['qtiff.dll','qwebp.dll','qtga.dll','qwbmp.dll','qicns.dll']:module='qtimageformats'
        elif p.suffix.lower()=='.pyd' or p.name.lower().startswith('pyside6'):module='pyside-setup'
        else:module='qtbase'
        component=module+' 6.12.0';basis='LGPL-3.0 option; component source archive and its bundled third-party licenses'
    elif 'cv2' in lower:component='OpenCV 5.0.0.93';basis='Apache-2.0 plus cv2/LICENSE-3RD-PARTY.txt; FFmpeg DLL excluded'
    elif '/pil/' in lower:component='Pillow 13.0.0';basis='HPND and bundled Pillow third-party licenses'
    elif 'charset_normalizer' in lower:component='charset-normalizer 3.5.2';basis='MIT; bundled package license'
    elif p.name.lower().startswith(('msvcp','vcruntime')):component='Microsoft Visual C++ runtime';basis='Microsoft redistribution terms; includes wheel-renamed runtime copies'
    elif 'numpy' in lower:component='NumPy 2.5.4 / OpenBLAS';basis='NumPy wheel bundled license texts (BSD and third parties)'
    elif 'pdfium' in lower:component='PDFium build 8076 / pypdfium2 5.14.0';basis='PDFium/pypdfium2 bundled third-party notices'
    elif p.name.lower().startswith(('msvcp','vcruntime')):component='Microsoft Visual C++ runtime';basis='Microsoft redistributable terms; bundled by upstream distribution'
    elif p.name.lower().startswith(('libssl','libcrypto')):component='OpenSSL';basis='Apache-2.0; exact bundled library version in PE inventory'
    elif 'libffi' in lower:component='libffi (exact build unconfirmed)';basis='MIT reference included; exact binary provenance/copyright still requires verification'
    elif p.name.startswith('FolioScan'):component='FolioScan / PyInstaller bootloader';basis='PolyForm Noncommercial / PyInstaller GPL with bootloader exception'
    else:component='Python runtime or extension';basis='Python PSF and extension package notices; review per file'
    pe=pefile.PE(str(p));details={}
    for group in getattr(pe,'FileInfo',[]):
        for info in group:
            for table in getattr(info,'StringTable',[]):
                for k,v in table.entries.items():
                    key=k.decode(errors='replace')
                    if key in ['FileVersion','ProductVersion','LegalCopyright','CompanyName']:
                        details[key]=v.decode(errors='replace')
    pe.close()
    records.append(dict(file=rel,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),component=component,license_basis=basis,metadata=details))
(root/'legal/windows-binary-inventory.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),'utf-8')
packages=[]
for d in metadata.distributions():
    packages.append(dict(name=d.metadata['Name'],version=d.version,license=d.metadata.get('License-Expression') or d.metadata.get('License')))
(root/'legal/windows-environment.json').write_text(json.dumps(packages,ensure_ascii=False,indent=2),'utf-8')
print(f'{len(records)} final binary files inventoried. The environment list includes build tools; it is not a runtime SBOM.')
