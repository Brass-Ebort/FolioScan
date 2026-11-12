from pathlib import PureWindowsPath

a = Analysis(['launcher.py'], pathex=[], binaries=[], datas=[('arrow-dark.png','.'),('arrow-light.png','.'),('scanner.png','.'),('translations.tsv','.'),('../LICENSE','legal'),('../NOTICE','legal'),('../THIRD_PARTY.md','legal'),('../AVISO_QT_LGPL.md','legal'),('../legal','legal/audit'),('licenses','legal/dependencies')],
             hiddenimports=[], hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[], noarchive=False)
# These DLLs are part of supported Windows releases. Do not bundle unrelated
# copies found on PATH (e.g. Poppler ICU uses incompatible versioned exports).
system_dlls={'ucrtbase.dll','icu.dll','icuuc.dll','icuin.dll','icudt78.dll'}
a.binaries=[entry for entry in a.binaries if PureWindowsPath(entry[0]).name.lower() not in system_dlls
            and not PureWindowsPath(entry[0]).name.lower().startswith('api-ms-win-')
            # Interfaz QWidget raster: no hay widgets OpenGL ni necesidad de Mesa/LLVM.
            and PureWindowsPath(entry[0]).name.lower() != 'opengl32sw.dll'
            # La cámara utiliza CAP_DSHOW; no se abren vídeos mediante FFmpeg.
            and not PureWindowsPath(entry[0]).name.lower().startswith('opencv_videoio_ffmpeg')]
pyz=PYZ(a.pure)
exe=EXE(pyz,a.scripts,[],exclude_binaries=True,name='FolioScan-3.2',
        debug=False,bootloader_ignore_signals=False,strip=False,upx=False,
        console=False,disable_windowed_traceback=False,icon='scanner.png',version='version_info.txt')
collect=COLLECT(exe,a.binaries,a.datas,strip=False,upx=False,name='FolioScan-3.2')
