#!/usr/bin/env python3
"""Pack Controller APK: hybrid SO into assets/emu/libJCC.so AND embed into assets/JCC.sh."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

def embedded_region(jcc_sh: bytes) -> tuple[int, int]:
    import struct

    first = jcc_sh.find(b"\x7fELF")
    second = jcc_sh.find(b"\x7fELF", first + 1)
    if second < 0:
        raise SystemExit("second ELF not found in JCC.sh")
    o = second
    e_phoff = struct.unpack_from("<Q", jcc_sh, o + 32)[0]
    e_phentsize = struct.unpack_from("<H", jcc_sh, o + 54)[0]
    e_phnum = struct.unpack_from("<H", jcc_sh, o + 56)[0]
    max_end = 0
    for i in range(e_phnum):
        off = o + e_phoff + i * e_phentsize
        p_type = struct.unpack_from("<I", jcc_sh, off)[0]
        p_offset = struct.unpack_from("<Q", jcc_sh, off + 8)[0]
        p_filesz = struct.unpack_from("<Q", jcc_sh, off + 32)[0]
        if p_type == 1:
            max_end = max(max_end, p_offset + p_filesz)
    if max_end < 100000:
        raise SystemExit(f"embedded region too small: {max_end}")
    return second, max_end


def replace_in_apk(src_apk: Path, dst_apk: Path, replacements: dict[str, bytes]) -> None:
    # read all, write new (zipfile update is fragile on Windows)
    with zipfile.ZipFile(src_apk, "r") as zin:
        infos = zin.infolist()
        blobs = {i.filename: zin.read(i.filename) for i in infos}

    for name, data in replacements.items():
        blobs[name] = data
        print(f"  set {name} = {len(data)} bytes")

    if dst_apk.exists():
        dst_apk.unlink()
    with zipfile.ZipFile(dst_apk, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for info in infos:
            name = info.filename
            # skip signatures
            if name.startswith("META-INF/") and (
                name.endswith(".SF")
                or name.endswith(".RSA")
                or name.endswith(".DSA")
                or name.endswith(".EC")
                or name == "META-INF/MANIFEST.MF"
                or "ANDROID" in name
            ):
                continue
            data = blobs.get(name, b"")
            # store SO/sh without recompress if we replaced
            if name in replacements:
                zi = zipfile.ZipInfo(filename=name)
                zi.compress_type = zipfile.ZIP_STORED
                zout.writestr(zi, data)
            else:
                zi = zipfile.ZipInfo(filename=name)
                zi.compress_type = info.compress_type
                zi.external_attr = info.external_attr
                zi.date_time = info.date_time
                zout.writestr(zi, data)
        # if replacement name was not in original (shouldn't happen)
        for name, data in replacements.items():
            if name not in {i.filename for i in infos}:
                zi = zipfile.ZipInfo(filename=name)
                zi.compress_type = zipfile.ZIP_STORED
                zout.writestr(zi, data)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--so", required=True)
    ap.add_argument("--orig-apk", default=r"D:\grok-cli\bin\JCC Controller.apk")
    ap.add_argument("--out", required=True)
    ap.add_argument("--ks", default=None)
    ap.add_argument("--signer-jar", default=None)
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]
    so_path = Path(args.so)
    orig = Path(args.orig_apk)
    out_apk = Path(args.out)
    ks = Path(args.ks or root / "signing/jcc-controller.release.keystore")
    jar = Path(args.signer_jar or root / "tools/uber-apk-signer.jar")

    our = so_path.read_bytes()
    if len(our) < 100000:
        print("SO too small", len(our), file=sys.stderr)
        return 1

    with zipfile.ZipFile(orig, "r") as z:
        jcc_sh = z.read("assets/JCC.sh")

    second, region = embedded_region(jcc_sh)
    if len(our) > region:
        print(f"SO {len(our)} > slot {region}", file=sys.stderr)
        return 1
    payload = our + b"\x00" * (region - len(our))
    new_sh = bytearray(jcc_sh)
    new_sh[second : second + region] = payload
    print(f"embedded hybrid SO at {second} slot={region}")

    unsigned = root / "_pack_unsigned.apk"
    replace_in_apk(
        orig,
        unsigned,
        {
            "assets/emu/libJCC.so": our,
            "assets/JCC.sh": bytes(new_sh),
        },
    )

    # verify
    with zipfile.ZipFile(unsigned, "r") as z:
        assert len(z.read("assets/emu/libJCC.so")) == len(our)
        assert len(z.read("assets/JCC.sh")) == len(new_sh)
        print("unsigned verify OK")

    sign_out = root / "_pack_signed"
    if sign_out.exists():
        shutil.rmtree(sign_out)
    sign_out.mkdir(parents=True)
    cmd = [
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
    subprocess.check_call(cmd)
    signed = next(sign_out.glob("*Signed*.apk"), None)
    if not signed:
        print("sign failed", file=sys.stderr)
        return 1
    out_apk.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(signed, out_apk)

    with zipfile.ZipFile(out_apk, "r") as z:
        so_l = len(z.read("assets/emu/libJCC.so"))
        sh_l = len(z.read("assets/JCC.sh"))
        sh = z.read("assets/JCC.sh")
        print(f"FINAL {out_apk} so={so_l} jccsh={sh_l} has_FULL={b'FULL-1.0.5' in sh}")
        if so_l < 100000 or sh_l < 100000:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
