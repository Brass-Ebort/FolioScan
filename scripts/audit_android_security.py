"""Query OSV for the exact resolved Android runtime coordinates, recording scope."""
from pathlib import Path
from datetime import date
import json, urllib.request

root=Path(__file__).resolve().parents[1]
artifacts=json.loads((root/'legal/android-dependencies.json').read_text('utf-8-sig'))
coordinates=sorted({item['id'] for item in artifacts})
queries=[]
for coordinate in coordinates:
    group,artifact,version=coordinate.split(':')
    queries.append({'package':{'ecosystem':'Maven','name':group+':'+artifact},'version':version})
request=urllib.request.Request('https://api.osv.dev/v1/querybatch',
    data=json.dumps({'queries':queries}).encode(),headers={'Content-Type':'application/json'})
with urllib.request.urlopen(request,timeout=60) as response:
    results=json.load(response)['results']
assert len(results)==len(coordinates)
packages=[{'coordinate':c,'advisories':r.get('vulns',[])} for c,r in zip(coordinates,results)]
report={'date':date.today().isoformat(),'source':'https://api.osv.dev/v1/querybatch',
        'scope':'Known advisories indexed for the resolved Maven coordinates; not exhaustive source auditing or a guarantee against unknown vulnerabilities.',
        'packages':packages}
(root/'legal/android-security-check.json').write_text(json.dumps(report,indent=2),'utf-8')
affected=[p for p in packages if p['advisories']]
if affected:
    print(json.dumps(affected,indent=2))
    raise SystemExit('Review the remaining Android dependency advisories before release.')
print('No indexed OSV advisories for',len(packages),'resolved Android coordinates.')
