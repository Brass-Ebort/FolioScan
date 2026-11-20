from pathlib import Path, PureWindowsPath
import json

a = Analysis(['launcher.py'], pathex=[], binaries=[], datas=[('arrow-dark.png','.'),('arrow-light.png','.'),('scanner.png','.'),('translations.tsv','.'),('../LICENSE','legal'),('../NOTICE','legal'),('../THIRD_PARTY.md','legal'),('../AVISO_QT_LGPL.md','legal'),('licenses','legal/dependencies')],
             hiddenimports=[], hookspath=[], hooksconfig={}, runtime_hooks=['runtime_prerequisites.py'], excludes=[], noarchive=False)
# These DLLs are part of supported Windows releases. Do not bundle unrelated
# copies found on PATH (e.g. Poppler ICU uses incompatible versioned exports).
system_dlls={'ucrtbase.dll','icu.dll','icuuc.dll','icuin.dll','icudt78.dll'}
a.binaries=[entry for entry in a.binaries if PureWindowsPath(entry[0]).name.lower() not in system_dlls
            and not PureWindowsPath(entry[0]).name.lower().startswith('api-ms-win-')
            # Interfaz QWidget raster: no hay widgets OpenGL ni necesidad de Mesa/LLVM.
            and PureWindowsPath(entry[0]).name.lower() != 'opengl32sw.dll'
            # La cÃ¡mara utiliza CAP_DSHOW; no se abren vÃ­deos mediante FFmpeg.
            and not PureWindowsPath(entry[0]).name.lower().startswith('opencv_videoio_ffmpeg')
            # Replace wheel runtime copies with the licensed Visual Studio release CRT.
            and not PureWindowsPath(entry[0]).name.lower().startswith(('msvcp', 'vcruntime', 'concrt'))
            and PureWindowsPath(entry[0]).name.lower() != 'libffi-8.dll']
a.binaries.append(('libffi-8.dll', 'build/verified-runtime/libffi-8.dll', 'BINARY'))
# Only release CRT bytes sourced from the installed Visual Studio redist folder.
runtime = json.loads(Path('../legal/microsoft-runtime-provenance.json').read_text('utf-8'))
for item in runtime['files']:
    a.binaries.append((item['destination'], str(Path('build/verified-runtime/microsoft') / item['source_name']), 'BINARY'))
pyz=PYZ(a.pure)
exe=EXE(pyz,a.scripts,[],exclude_binaries=True,name='FolioScan-0.4.0',
        debug=False,bootloader_ignore_signals=False,strip=False,upx=False,
        console=False,disable_windowed_traceback=False,icon='scanner.png',version='version_info.txt')
collect=COLLECT(exe,a.binaries,a.datas,strip=False,upx=False,name='FolioScan-0.4.0')
# Single movable executable. The onedir build above is retained only for audits.
portable=EXE(pyz,a.scripts,a.binaries,a.datas,[],name='FolioScan-0.4.0-portable',
        debug=False,bootloader_ignore_signals=False,strip=False,upx=False,
        console=False,disable_windowed_traceback=False,icon='scanner.png',version='version_info.txt')
