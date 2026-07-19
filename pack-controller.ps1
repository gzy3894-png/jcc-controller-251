param(
  [Parameter(Mandatory = $true)][string]$SoPath,
  [string]$InjectPath = "",
  [string]$OrigApk = "D:\grok-cli\bin\JCC Controller.apk",
  [string]$OutName = "JCC-Controller.apk"
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Py = "C:\Users\dell\python312\python.exe"
$Pack = Join-Path $Root "tools\pack_controller.py"
if (-not $InjectPath) { throw "need -InjectPath jcc_inject" }
& $Py $Pack --so $SoPath --inject $InjectPath --orig-apk $OrigApk --out (Join-Path $Root "dist\$OutName")
if ($LASTEXITCODE -ne 0) { throw "pack failed" }
