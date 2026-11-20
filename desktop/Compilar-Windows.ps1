param([switch]$SkipFunctionalTests)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
& .\.venv\Scripts\python.exe ..\scripts\prepare_windows_runtime.py
if ($LASTEXITCODE -ne 0) { throw 'No se pudo verificar libffi.' }
& .\.venv\Scripts\python.exe ..\scripts\prepare_microsoft_runtime.py
if ($LASTEXITCODE -ne 0) { throw 'Se requiere Visual Studio con derechos de redistribuciÃƒÂ³n.' }
if (!$SkipFunctionalTests) {
    & .\.venv\Scripts\python.exe -m unittest test_core test_ui test_v3 test_drop test_runtime_terms -v
    if ($LASTEXITCODE -ne 0) { throw 'Han fallado las pruebas.' }
}
& .\.venv\Scripts\python.exe -m PyInstaller --noconfirm desktop.spec
if ($LASTEXITCODE -ne 0) { throw 'Ha fallado el empaquetado.' }
if (!$SkipFunctionalTests) {
    $report = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../legal/windows-functional-check.json'))
    $check = Start-Process -FilePath (Join-Path $PSScriptRoot 'dist/FolioScan-3.2-portable.exe') -ArgumentList @('--self-test', ('"' + $report + '"')) -WindowStyle Hidden -Wait -PassThru
    if ($check.ExitCode -ne 0) { throw 'Ha fallado la autoprueba del ejecutable.' }
}
