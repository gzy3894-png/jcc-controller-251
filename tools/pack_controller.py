#!/usr/bin/env python3
from __future__ import annotations

import argparse
import io
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

SHELL = r"""#!/system/bin/sh
export PATH=/system/bin:/system/xbin:$PATH
T=/data/local/tmp
PKG=com.tencent.jkchess
# app private dir is executable; /data/local/tmp often noexec
APP=/data/user/0/$PKG
LOG=$APP/files/log.txt
ME="$0"

log() {
  mkdir -p "$APP/files" 2>/dev/null
  echo "[wrap] $*" >> "$LOG" 2>/dev/null
}

N=$(grep -n '^__END__$' "$ME" | head -1 | cut -d: -f1)
if [ -z "$N" ]; then log "no payload"; exit 1; fi
N=$((N + 1))
rm -rf "$APP/jcc_pay" "$T/jcc_pay"
mkdir -p "$APP/jcc_pay" "$APP/files"
tail -n +$N "$ME" > "$APP/jcc_payload.tar" 2>/dev/null
tar -xf "$APP/jcc_payload.tar" -C "$APP/jcc_pay" 2>/dev/null
INJ="$APP/jcc_pay/jcc_inject"
SO="$APP/jcc_pay/libJCC.so"
if [ ! -f "$INJ" ] || [ ! -f "$SO" ]; then
  # fallback extract to tmp then copy
  mkdir -p "$T/jcc_pay"
  tail -n +$N "$ME" > "$T/jcc_payload.tar" 2>/dev/null
  tar -xf "$T/jcc_payload.tar" -C "$T/jcc_pay" 2>/dev/null
  cp -f "$T/jcc_pay/jcc_inject" "$INJ" 2>/dev/null
  cp -f "$T/jcc_pay/libJCC.so" "$SO" 2>/dev/null
fi
if [ ! -f "$INJ" ] || [ ! -f "$SO" ]; then log "extract fail"; exit 1; fi
chmod 755 "$INJ" "$SO"
# clear noexec / seandroid
chcon u:object_r:system_file:s0 "$INJ" 2>/dev/null
chcon u:object_r:app_data_file:s0 "$INJ" 2>/dev/null

PID=""
i=0
while [ $i -lt 90 ]; do
  PID=$(pidof "$PKG" 2>/dev/null)
  if [ -n "$PID" ]; then break; fi
  PID=$(ps -A 2>/dev/null | grep -F "$PKG" | grep -v grep | head -1 | awk '{print $2}')
  if [ -n "$PID" ]; then break; fi
  i=$((i + 1))
  sleep 1
done
if [ -z "$PID" ]; then log "no pid"; exit 1; fi
log "pid=$PID"
sleep 2

cp -f "$SO" "$APP/libJCC.so" 2>/dev/null
cp -f "$SO" /data/data/$PKG/libJCC.so 2>/dev/null
cp -f "$SO" "$T/libJCC.so" 2>/dev/null
chmod 755 "$APP/libJCC.so" "$T/libJCC.so" 2>/dev/null

setenforce 0 2>/dev/null
EC=1
# 1) direct exec from app dir
if [ -x "$INJ" ]; then
  "$INJ" "$PID" "$SO" >> "$LOG" 2>&1
  EC=$?
  log "direct inject=$EC"
fi
# 2) linker64 (works when 'not executable: 64-bit ELF')
if [ "$EC" -ne 0 ] && [ -x /system/bin/linker64 ]; then
  /system/bin/linker64 "$INJ" "$PID" "$SO" >> "$LOG" 2>&1
  EC=$?
  log "linker64 inject=$EC"
fi
# 3) copy to /data/local and try again
if [ "$EC" -ne 0 ]; then
  cp -f "$INJ" "$T/jcc_inject" 2>/dev/null
  chmod 755 "$T/jcc_inject" 2>/dev/null
  if [ -x /system/bin/linker64 ]; then
    /system/bin/linker64 "$T/jcc_inject" "$PID" "$SO" >> "$LOG" 2>&1
    EC=$?
    log "tmp+linker64 inject=$EC"
  else
    "$T/jcc_inject" "$PID" "$SO" >> "$LOG" 2>&1
    EC=$?
    log "tmp inject=$EC"
  fi
fi

sleep 2
if [ $EC -eq 0 ]; then
  echo "[+] OK"
  log "ok"
else
  echo "[-] FAIL"
  log "fail=$EC"
fi
exit $EC
__END__
"""


def make_jcc_sh(inject_bin: bytes, so_bin: bytes) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tar:

        def add(name: str, data: bytes, mode: int = 0o755):
            info = tarfile.TarInfo(name=name)
            info.size = len(data)
            info.mode = mode
            tar.addfile(info, io.BytesIO(data))

        add("jcc_inject", inject_bin, 0o755)
        add("libJCC.so", so_bin, 0o755)
    script = SHELL.encode("utf-8")
    if not script.endswith(b"\n"):
        script += b"\n"
    return script + buf.getvalue()


def replace_in_apk(src_apk: Path, dst_apk: Path, replacements: dict[str, bytes]) -> None:
    with zipfile.ZipFile(src_apk, "r") as zin:
        infos = zin.infolist()
        blobs = {i.filename: zin.read(i.filename) for i in infos}
    for name, data in replacements.items():
        blobs[name] = data
    if dst_apk.exists():
        dst_apk.unlink()
    with zipfile.ZipFile(dst_apk, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        seen = set()
        for info in infos:
            name = info.filename
            if name.startswith("META-INF/") and (
                name.endswith((".SF", ".RSA", ".DSA", ".EC"))
                or name == "META-INF/MANIFEST.MF"
                or "ANDROID" in name
            ):
                continue
            data = blobs[name]
            seen.add(name)
            zi = zipfile.ZipInfo(filename=name)
            zi.date_time = info.date_time
            zi.external_attr = info.external_attr
            zi.compress_type = (
                zipfile.ZIP_STORED if name in replacements else info.compress_type
            )
            zout.writestr(zi, data)
        for name, data in replacements.items():
            if name not in seen:
                zi = zipfile.ZipInfo(filename=name)
                zi.compress_type = zipfile.ZIP_STORED
                zout.writestr(zi, data)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--so", required=True)
    ap.add_argument("--inject", required=True)
    ap.add_argument("--orig-apk", default=r"D:\grok-cli\bin\JCC Controller.apk")
    ap.add_argument("--out", required=True)
    ap.add_argument("--ks", default=None)
    ap.add_argument("--signer-jar", default=None)
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]
    so = Path(args.so).read_bytes()
    inj = Path(args.inject).read_bytes()
    if len(so) < 100000 or len(inj) < 1000:
        print("bad inputs", file=sys.stderr)
        return 1

    jcc_sh = make_jcc_sh(inj, so)
    unsigned = root / "_pack_unsigned.apk"
    replace_in_apk(
        Path(args.orig_apk),
        unsigned,
        {"assets/JCC.sh": jcc_sh, "assets/emu/libJCC.so": so},
    )

    ks = Path(args.ks or root / "signing/jcc-controller.release.keystore")
    jar = Path(args.signer_jar or root / "tools/uber-apk-signer.jar")
    sign_out = root / "_pack_signed"
    if sign_out.exists():
        shutil.rmtree(sign_out)
    sign_out.mkdir(parents=True)
    subprocess.check_call(
        [
            "java",
            "-jar",
            str(jar),
            "-a",
            str(unsigned),
            "-o",
            str(sign_out),
            "--allowResign",
            "--ks",
            str(ks),
            "--ksPass",
            "android",
            "--ksKeyPass",
            "android",
            "--ksAlias",
            "androiddebugkey",
        ]
    )
    signed = next(sign_out.glob("*Signed*.apk"), None)
    if not signed:
        return 1
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(signed, out)
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
