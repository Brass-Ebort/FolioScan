from pathlib import PureWindowsPath

a = Analysis(['launcher.py'], pathex=[], binaries=[], datas=[('scanner.png','.'),('translations.tsv','.'),('../LICENSE','legal'),('../NOTICE','legal'),('../THIRD_PARTY.md','legal'),('licenses','legal/dependencies')],
             hiddenimports=[], hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[], noarchive=False)
# These DLLs are part of supported Windows releases. Do not bundle unrelated
# copies found on PATH (e.g. Poppler ICU uses incompatible versioned exports).
system_dlls={'ucrtbase.dll','icu.dll','icuuc.dll','icuin.dll'}
a.binaries=[entry for entry in a.binaries if PureWindowsPath(entry[0]).name.lower() not in system_dlls
            and not PureWindowsPath(entry[0]).name.lower().startswith('api-ms-win-')]
pyz=PYZ(a.pure)
exe=EXE(pyz,a.scripts,a.binaries,a.datas,[],name='FolioScan-3.1',
        debug=False,bootloader_ignore_signals=False,strip=False,upx=False,
        console=False,disable_windowed_traceback=False,icon='scanner.png',version='version_info.txt')
