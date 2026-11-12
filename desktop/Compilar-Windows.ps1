param([switch]$SkipFunctionalTests)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (!$SkipFunctionalTests) {
    & .\.venv\Scripts\python.exe -m unittest test_core test_ui test_v3 test_drop -v
    if ($LASTEXITCODE -ne 0) { throw 'Han fallado las pruebas.' }
}
& .\.venv\Scripts\python.exe -m PyInstaller --noconfirm desktop.spec
if ($LASTEXITCODE -ne 0) { throw 'Ha fallado el empaquetado.' }
