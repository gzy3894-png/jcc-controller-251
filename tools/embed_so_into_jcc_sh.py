#!/usr/bin/env python3
import argparse
import struct
import zipfile
from pathlib import Path


def embedded_region(jcc_sh: bytes) -> tuple[int, int]:
    first = jcc_sh.find(b"\x7fELF")
    second = jcc_sh.find(b"\x7fELF", first + 1)
    if second < 0:
        raise SystemExit("no second elf")
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
    return second, max_end


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--orig-apk", required=True)
    ap.add_argument("--so", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    with zipfile.ZipFile(args.orig_apk) as z:
        jcc_sh = z.read("assets/JCC.sh")
    our = Path(args.so).read_bytes()
    second, region = embedded_region(jcc_sh)
    if len(our) > region:
        raise SystemExit("so too large")
    payload = our + b"\x00" * (region - len(our))
    out = bytearray(jcc_sh)
    out[second : second + region] = payload
    Path(args.out).write_bytes(out)


if __name__ == "__main__":
    main()
