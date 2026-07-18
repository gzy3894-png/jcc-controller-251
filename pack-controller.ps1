# 打包 Controller 大包（固定签名）
# 用法: .\pack-controller.ps1 -SoPath path\to\libJCC.so [-OutName JCC-Controller-2.5.3.apk]
param(
  [Parameter(Mandatory=$true)][string]$SoPath,
  [string]$OrigApk = "D:\grok-cli\bin\JCC Controller.apk",
  [string]$OutName = "JCC-Controller-next.apk"
)
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Work = $Root
$Ks = Join-Path $Root "signing\jcc-controller.release.keystore"
$Jar = Join-Path $Root "tools\uber-apk-signer.jar"
if (-not (Test-Path $Ks)) { throw "missing keystore $Ks" }
if (-not (Test-Path $Jar)) { throw "missing uber-apk-signer $Jar" }
if (-not (Test-Path $SoPath)) { throw "missing SO $SoPath" }
if (-not (Test-Path $OrigApk)) { throw "missing original apk $OrigApk" }

$unsigned = Join-Path $Work "_pack_unsigned.apk"
Copy-Item $OrigApk $unsigned -Force
$z = [IO.Compression.ZipFile]::Open($unsigned, [IO.Compression.ZipArchiveMode]::Update)
$toDel = @($z.Entries | Where-Object {
  $_.FullName -match '^META-INF/.*\.(SF|RSA|DSA|EC)$' -or $_.FullName -eq 'META-INF/MANIFEST.MF' -or $_.FullName -match 'META-INF/ANDROID'
})
foreach ($x in $toDel) { $x.Delete() }
$old = $z.GetEntry("assets/emu/libJCC.so"); if ($old) { $old.Delete() }
$ne = $z.CreateEntry("assets/emu/libJCC.so", [IO.Compression.CompressionLevel]::NoCompression)
$in = [IO.File]::OpenRead((Resolve-Path $SoPath)); $out = $ne.Open(); $in.CopyTo($out); $out.Close(); $in.Close()
$z.Dispose()

$signOut = Join-Path $Work "_pack_signed"
Remove-Item $signOut -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $signOut | Out-Null
java -jar $Jar -a $unsigned -o $signOut --allowResign --ks $Ks --ksPass android --ksKeyPass android --ksAlias androiddebugkey
$signed = Get-ChildItem $signOut -Filter "*Signed*.apk" | Select-Object -First 1
if (-not $signed) { throw "sign failed" }
$dest = Join-Path $Root "dist\$OutName"
New-Item -ItemType Directory -Force -Path (Join-Path $Root "dist") | Out-Null
Copy-Item $signed.FullName $dest -Force
Write-Host "OK -> $dest size=$((Get-Item $dest).Length)"
java -jar $Jar -a $dest -y 2>&1 | Select-String "SHA256|verified"
