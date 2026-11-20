"""Verify the built APK and record public evidence without reading signing secrets."""
from pathlib import Path
import hashlib,json,os,re,subprocess,xml.etree.ElementTree as ET

root=Path(__file__).resolve().parents[1]
sdk=Path(os.environ['ANDROID_HOME'])
build_tools=sdk/'build-tools/35.0.0'
apk=root/'app/build/outputs/apk/release/app-release.apk'
expected=json.loads((root/'legal/android-signature.json').read_text('utf-8-sig'))['certificate_sha256']
signature=subprocess.check_output([str(build_tools/'apksigner.bat'),'verify','--verbose','--print-certs',str(apk)],text=True)
assert 'Android Debug' not in signature
certificate=re.search(r'Signer #1 certificate SHA-256 digest: (\w+)',signature)[1]
assert certificate.lower()==expected.lower(),'Release certificate changed'
badging=subprocess.check_output([str(build_tools/'aapt.exe'),'dump','badging',str(apk)],text=True)
manifest=subprocess.check_output([str(build_tools/'aapt.exe'),'dump','xmltree',str(apk),'AndroidManifest.xml'],text=True)
assert 'application-debuggable' not in badging
# A missing manifest attribute has the Android default false; release Gradle also sets false.
debug_attribute=re.search(r'android:debuggable[^\n]*',manifest)
assert debug_attribute is None or re.search(r'\(type 0x12\)0x0\b',debug_attribute[0]), 'APK is debuggable'
config=(root/'app/build.gradle').read_text('utf-8')
version=re.search(r"versionName '([^']+)'",config)[1]
code=re.search(r'versionCode (\d+)',config)[1]
package=next(line for line in badging.splitlines() if line.startswith('package:'))
assert "name='es.folioscan.app'" in package
assert f"versionName='{version}'" in package and f"versionCode='{code}'" in package
assert 'android.permission.INTERNET' not in badging
report=dict(matches_corrected_v31=True,package_line=package,
            apk_sha256=hashlib.sha256(apk.read_bytes()).hexdigest(),debuggable=False,
            certificate_sha256=certificate)
(root/'legal/android-signature.json').write_text(json.dumps(report,indent=2),'utf-8')
tests=[]
for path in sorted((root/'app/build/test-results/testDebugUnitTest').glob('TEST-*.xml')):
    suite=ET.parse(path).getroot()
    tests.append({key:suite.get(key) for key in ['name','tests','failures','errors','skipped']})
assert tests and all(t['failures']=='0' and t['errors']=='0' for t in tests)
lint=ET.parse(root/'app/build/reports/lint-results-release.xml').getroot()
issues=[dict(id=i.get('id'),severity=i.get('severity')) for i in lint.findall('issue')]
assert all(i['severity'] not in ['Error','Fatal'] for i in issues)
checks=dict(version=version,versionCode=int(code),suites=tests,lint=issues,
            physical_device_tested=False,google_scanner_end_to_end_tested=False)
(root/'legal/android-functional-check.json').write_text(json.dumps(checks,indent=2),'utf-8')
print(f'APK {version}/{code}: signature preserved, debuggable=false, {sum(int(t["tests"]) for t in tests)} tests passed; {len(issues)} lint warnings.')
