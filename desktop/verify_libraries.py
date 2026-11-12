"""Limited loader check for LGPL replacement; no document/camera functional tests."""
def run(destination):
    import os, sys, json, ctypes, hashlib
    from pathlib import Path
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    result = {'ok': False}
    try:
        from PySide6 import QtCore, QtGui, QtWidgets
        import shiboken6
        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        widget = QtWidgets.QWidget()
        widget.resize(20, 20)
        widget.show()
        app.processEvents()
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.GetModuleHandleW.argtypes = [ctypes.c_wchar_p]
        kernel.GetModuleHandleW.restype = ctypes.c_void_p
        kernel.GetModuleFileNameW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint]
        paths = []
        base = Path(sys.executable).parent
        for name in ['Qt6Core.dll','Qt6Gui.dll','Qt6Widgets.dll','pyside6.abi3.dll','shiboken6.abi3.dll']:
            handle=kernel.GetModuleHandleW(name)
            if not handle: raise RuntimeError('Module not loaded: '+name)
            buffer=ctypes.create_unicode_buffer(32768)
            if not kernel.GetModuleFileNameW(handle,buffer,len(buffer)): raise ctypes.WinError()
            p=Path(buffer.value)
            paths.append({'module':name,'path':p.relative_to(base).as_posix(),
                          'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        widget.close()
        result={'ok':True,'qt':QtCore.qVersion(),'modules':paths,
                'scope':'DLL loading and Qt event loop only; no functional tests.'}
    except Exception as error:
        result['error']=str(error)
    Path(destination).write_text(json.dumps(result,indent=2),'utf-8')
    if not result['ok']: raise SystemExit(1)
