"""Fetch the pinned PSF libffi build and its matching notice, verifying its bytes."""
from pathlib import Path
import hashlib
import json
import urllib.request

root = Path(__file__).resolve().parents[1]
commit = '94cb9a1c7feb608adf2b9f8fe2dbd6925ffbf90d'
base = f'https://raw.githubusercontent.com/python/cpython-bin-deps/{commit}/'
expected = 'eff52743773eb550fcc6ce3efc37c85724502233b6b002a35496d828bd7b280a'
binary = urllib.request.urlopen(base + 'amd64/libffi-8.dll', timeout=60).read()
assert hashlib.sha256(binary).hexdigest() == expected, 'Unexpected libffi download'
destination = root / 'desktop/build/verified-runtime'
destination.mkdir(parents=True, exist_ok=True)
(destination / 'libffi-8.dll').write_bytes(binary)
notice = urllib.request.urlopen(base + 'LICENSE', timeout=60).read()
(root / 'desktop/licenses/Native/libffi-3.4.4-LICENSE.txt').write_bytes(notice)
(root / 'legal/libffi-provenance.json').write_text(json.dumps({
    'component': 'libffi 3.4.4, CPython amd64 build',
    'commit': commit, 'binary_url': base + 'amd64/libffi-8.dll',
    'sha256': expected, 'license_url': base + 'LICENSE',
    'license_sha256': hashlib.sha256(notice).hexdigest(),
    'action': 'Replace the untraceable runtime copy in the distribution only; retain the build interpreter unchanged.'
}, indent=2), encoding='utf-8')
