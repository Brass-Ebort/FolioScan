"""Stage unmodified x64 CRT files from an installed, stable Visual Studio.

The builder must hold a valid license for that Visual Studio edition and comply
with its redistribution terms. Installing only the end-user VC runtime does not
satisfy this build prerequisite. No license is accepted by this script.
"""
from pathlib import Path
import os, subprocess, json, shutil, hashlib

root = Path(__file__).resolve().parents[1]
vswhere = Path(os.environ['ProgramFiles(x86)']) / 'Microsoft Visual Studio/Installer/vswhere.exe'
instances = json.loads(subprocess.check_output([str(vswhere), '-all', '-products', '*', '-utf8', '-format', 'json']).decode('utf-8-sig'))
instance = next(i for i in instances if i['isComplete'] and not i['isPrerelease']
                and i['productId'] == 'Microsoft.VisualStudio.Product.Community'
                and i['installationVersion'].startswith('18.'))
installation = Path(instance['installationPath'])
redist = installation / 'VC/Redist/MSVC'
versions = sorted((p for p in redist.iterdir() if p.name[0].isdigit()),
                  key=lambda p: tuple(map(int, p.name.split('.'))))
source = versions[-1] / 'x64/Microsoft.VC145.CRT'
target = root / 'desktop/build/verified-runtime/microsoft'
target.mkdir(parents=True, exist_ok=True)
files = []
for file in sorted(source.glob('*.dll')):
    shutil.copy2(file, target/file.name)
    files.append(dict(source_name=file.name, destination=file.name,
                      source_relative=file.relative_to(installation).as_posix(),
                      sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
assert {'msvcp140.dll', 'vcruntime140.dll', 'vcruntime140_1.dll'}.issubset({x['source_name'] for x in files})
alias = dict(next(x for x in files if x['source_name']=='msvcp140.dll'))
alias['destination'] = 'numpy.libs/msvcp140-a4c2229bdc2a2a630acdc095b4d86008.dll'
files.append(alias)  # Same bytes; only the import filename required by NumPy differs.
report = dict(product=instance['displayName'], version=instance['installationVersion'],
              stable_complete_installation=True, runtime_directory=versions[-1].name,
              source='Installed Visual Studio Community release CRT, not System32 or wheel copies',
              license_url='https://visualstudio.microsoft.com/license-terms/vs2026-ga-community/',
              redist_list='https://learn.microsoft.com/en-us/visualstudio/releases/2026/redistribution',
              files=files)
environment = os.environ.copy()
environment.pop('PSModulePath', None)
environment.pop('PSMODULEPATH', None)  # Windows PowerShell must not inherit PowerShell 7 modules.
environment['FOLIOSCAN_CRT_DIR'] = str(source)
command = "$ErrorActionPreference='Stop'; @(Get-ChildItem -LiteralPath $env:FOLIOSCAN_CRT_DIR -Filter *.dll | ForEach-Object { $s = Get-AuthenticodeSignature -LiteralPath $_.FullName; @{file=$_.Name;status=$s.Status.ToString();signer=$s.SignerCertificate.Subject} }) | ConvertTo-Json"
signatures = json.loads(subprocess.check_output(['powershell.exe','-NoProfile','-Command',command],env=environment).decode('utf-8-sig'))
assert len(signatures) == len(files)-1
assert all(s['status']=='Valid' and 'Microsoft Corporation' in s['signer'] for s in signatures)
report['signatures'] = signatures
(root/'legal/microsoft-runtime-provenance.json').write_text(json.dumps(report,indent=2),'utf-8')
print('Staged', len(files), 'unmodified release CRT entries from', instance['displayName'])
