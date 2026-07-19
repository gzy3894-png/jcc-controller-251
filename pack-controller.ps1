# 打包 Controller：替换 assets/emu/libJCC.so + 把 hybrid 内核嵌进 JCC.sh（真机注入用这个）
# 用法: .\pack-controller.ps1 -SoPath path\to\libJCC.so [-OutName xxx.apk]
param(
  [Parameter(Mandatory = $true)][string]$SoPath,
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
$Py = "C:\Users\dell\python312\python.exe"
$EmbedPy = Join-Path $Root "tools\embed_so_into_jcc_sh.py"

if (-not (Test-Path $Ks)) { throw "missing keystore $Ks" }
if (-not (Test-Path $Jar)) { throw "missing uber-apk-signer $Jar" }
if (-not (Test-Path $SoPath)) { throw "missing SO $SoPath" }
if (-not (Test-Path $OrigApk)) { throw "missing original apk $OrigApk" }

$soLen = (Get-Item $SoPath).Length
if ($soLen -lt 100000) { throw "SO too small ($soLen) — refuse empty kernel" }
Write-Host "SO in: $SoPath ($soLen bytes)"

# 1) 把 hybrid SO 嵌进原版 JCC.sh（真机一键启动只跑这个）
$jccHybrid = Join-Path $Root "dist\JCC.sh.hybrid"
if (-not (Test-Path $EmbedPy)) { throw "missing $EmbedPy" }
& $Py $EmbedPy --orig-apk $OrigApk --so $SoPath --out $jccHybrid
$jccLen = (Get-Item $jccHybrid).Length
if ($jccLen -lt 100000) { throw "JCC.sh.hybrid too small" }
Write-Host "JCC.sh.hybrid: $jccLen bytes"

# 2) 打开原版 APK 替换两个资源
$unsigned = Join-Path $Work "_pack_unsigned.apk"
Copy-Item $OrigApk $unsigned -Force
$z = [IO.Compression.ZipFile]::Open($unsigned, [IO.Compression.ZipArchiveMode]::Update)

$toDel = @($z.Entries | Where-Object {
    $_.FullName -match '^META-INF/.*\.(SF|RSA|DSA|EC)$' -or
    $_.FullName -eq 'META-INF/MANIFEST.MF' -or
    $_.FullName -match 'META-INF/ANDROID'
  })
foreach ($x in $toDel) { $x.Delete() }

function Set-ZipEntry([IO.Compression.ZipArchive]$zip, [string]$entryName, [string]$filePath) {
  $old = $zip.GetEntry($entryName)
  if ($old) { $old.Delete() }
  $ne = $zip.CreateEntry($entryName, [IO.Compression.CompressionLevel]::NoCompression)
  $in = [IO.File]::OpenRead((Resolve-Path $filePath))
  $out = $ne.Open()
  $in.CopyTo($out)
  $out.Close(); $in.Close()
}

Set-ZipEntry $z "assets/emu/libJCC.so" $SoPath
Set-ZipEntry $z "assets/JCC.sh" $jccHybrid
$z.Dispose()

# 3) 校验 zip 内大小
$z2 = [IO.Compression.ZipFile]::OpenRead($unsigned)
$eSo = $z2.GetEntry("assets/emu/libJCC.so")
$eSh = $z2.GetEntry("assets/JCC.sh")
Write-Host "zip libJCC.so=$($eSo.Length) JCC.sh=$($eSh.Length)"
if ($eSo.Length -lt 100000) { $z2.Dispose(); throw "zip libJCC.so broken" }
if ($eSh.Length -lt 100000) { $z2.Dispose(); throw "zip JCC.sh broken" }
$z2.Dispose()

# 4) 签名
$signOut = Join-Path $Work "_pack_signed"
Remove-Item $signOut -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $signOut | Out-Null
java -jar $Jar -a $unsigned -o $signOut --allowResign --ks $Ks --ksPass android --ksKeyPass android --ksAlias androiddebugkey
$signed = Get-ChildItem $signOut -Filter "*Signed*.apk" | Select-Object -First 1
if (-not $signed) { throw "sign failed" }

$dest = Join-Path $Root "dist\$OutName"
New-Item -ItemType Directory -Force -Path (Join-Path $Root "dist") | Out-Null
Copy-Item $signed.FullName $dest -Force

# 5) 最终校验
$z3 = [IO.Compression.ZipFile]::OpenRead($dest)
$e3 = $z3.GetEntry("assets/emu/libJCC.so")
$e4 = $z3.GetEntry("assets/JCC.sh")
Write-Host "OK -> $dest apk=$((Get-Item $dest).Length) so=$($e3.Length) jccsh=$($e4.Length)"
$z3.Dispose()
if ($e3.Length -lt 100000 -or $e4.Length -lt 100000) { throw "signed apk entries broken" }
java -jar $Jar -a $dest -y 2>&1 | Select-String "SHA256|verified"
