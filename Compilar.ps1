$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
# Admite el entorno portátil local y una instalación estándar de JDK/SDK.
$folioTools = Join-Path $PSScriptRoot 'tools'
if (!(Test-Path -LiteralPath $folioTools)) { $folioTools = Join-Path (Split-Path $PSScriptRoot -Parent) 'herramientas' }
if (Test-Path -LiteralPath $folioTools) {
    $folioJdk = Get-ChildItem -LiteralPath $folioTools -Directory -Filter 'jdk-17*' | Select-Object -First 1
    if ($folioJdk) { $env:JAVA_HOME = $folioJdk.FullName }
}
if (Test-Path -LiteralPath "$folioTools\android-sdk") { $env:ANDROID_HOME = "$folioTools\android-sdk" }
if (!$env:JAVA_HOME) { throw 'Configura JAVA_HOME con un JDK 17.' }
if (!$env:ANDROID_HOME -and !(Test-Path -LiteralPath "$PSScriptRoot\local.properties")) { throw 'Configura ANDROID_HOME con el SDK Android.' }
$folioGradle = "$PSScriptRoot\gradlew.bat"
if (!(Test-Path -LiteralPath $folioGradle)) { $folioGradle = "$folioTools\gradle-8.11.1\bin\gradle.bat" }
& $folioGradle :app:assembleRelease :app:testDebugUnitTest :app:lintDebug --console=plain
if ($LASTEXITCODE -ne 0) { throw 'La compilación o las comprobaciones han fallado.' }
# Verifica el artefacto antes de copiarlo; no publica APK sin firma válida o depurable.
$folioApk = "$PSScriptRoot\app\build\outputs\apk\release\app-release.apk"
$folioSdk = $env:ANDROID_HOME
if (!$folioSdk) {
    $folioSdkLine = Get-Content -LiteralPath "$PSScriptRoot\local.properties" | Where-Object { $_ -match '^sdk.dir=' } | Select-Object -First 1
    if ($folioSdkLine) { $folioSdk = $folioSdkLine.Substring(8).Replace('\:', ':').Replace('\\', '\') }
}
$folioBuildTools = Get-ChildItem -LiteralPath "$folioSdk\build-tools" -Directory |
    Where-Object { $_.Name -match '^\d+\.\d+\.\d+$' } |
    Sort-Object { [version]$_.Name } -Descending | Select-Object -First 1
if (!$folioBuildTools) { throw 'No se encontraron Android SDK Build Tools para verificar el APK.' }
$folioSignature = & "$($folioBuildTools.FullName)\apksigner.bat" verify --verbose --print-certs $folioApk 2>&1
if ($LASTEXITCODE -ne 0) { throw 'La verificación criptográfica del APK ha fallado.' }
if (($folioSignature -join "`n") -match '(?i)CN=Android Debug') { throw 'El APK utiliza un certificado Android Debug.' }
$folioBadging = & "$($folioBuildTools.FullName)\aapt.exe" dump badging $folioApk 2>&1
if ($LASTEXITCODE -ne 0) { throw 'No se pudo inspeccionar el manifiesto del APK.' }
if (($folioBadging -join "`n") -match 'application-debuggable') { throw 'El APK tiene la depuración activada.' }
Copy-Item -LiteralPath "$PSScriptRoot\app\build\outputs\apk\release\app-release.apk" -Destination "$PSScriptRoot\FolioScan-3.1.apk" -Force
