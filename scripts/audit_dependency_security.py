"""Record known PyPI advisories for the exact pinned build/runtime dependencies."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import date
import json
import urllib.request

root = Path(__file__).resolve().parents[1]
def check(line):
    name, version = line.split('==')
    url = f'https://pypi.org/pypi/{name}/{version}/json'
    with urllib.request.urlopen(url, timeout=30) as response:
        data = json.load(response)
    return dict(name=name, version=version, source=url,
                advisories=data.get('vulnerabilities', []))

lines = [s.strip() for s in (root/'desktop/requirements.txt').read_text().splitlines()
         if s.strip() and not s.startswith('#')]
with ThreadPoolExecutor(max_workers=6) as pool:
    packages = list(pool.map(check, lines))
report = dict(date=date.today().isoformat(),
              scope='Known PyPI advisories only; not a guarantee of absence of vulnerabilities',
              packages=packages)
(root/'legal/dependency-security-check.json').write_text(json.dumps(report, indent=2), 'utf-8')
if any(p['advisories'] for p in packages):
    raise SystemExit('Known advisories found; review the report before packaging.')
print('No known advisories returned for the pinned dependencies.')
