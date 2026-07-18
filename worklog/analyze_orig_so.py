# Analyze original libJCC.so: where season-sensitive data lives
import re
import struct
from pathlib import Path

p = Path(r"D:\grok-cli\workspace\jcc-controller-work\extract\assets\emu\libJCC.so")
data = p.read_bytes()
print("size", len(data))

# 1) UTF-8 / ASCII strings of interest
pat = re.compile(rb"[\x20-\x7e]{4,100}")
strings = [(m.start(), m.group().decode("ascii", "ignore")) for m in pat.finditer(data)]
keys = (
    "iID",
    "iCost",
    "sName",
    "sHeroPaint",
    "heroId",
    "Offset",
    "offset",
    "SearchACG",
    "OnRefresh",
    "UnitData",
    "BuyHero",
    "PlayerModel",
    "0x10",
    "0x18",
    "0x60",
    "tabId",
    "GetMyPlayer",
    "OPPONENT",
    "牌库",
)
print("\n== interesting strings ==")
for off, s in strings:
    if any(k in s for k in keys) or (s.startswith("0x") and len(s) <= 6):
        print(f"  {off:08x}  {s}")

# 2) look for sequences of small offsets as uint32/uint64 arrays (common: 0x10,0x18,0x60,...)
# scan for 0x10, 0x18 nearby in little-endian uint32
print("\n== candidate offset clusters (u32 LE 0x10 then nearby 0x18/0x60/0xf8) ==")
hits = 0
for i in range(0, len(data) - 32, 4):
    v = struct.unpack_from("<I", data, i)[0]
    if v != 0x10:
        continue
    window = [struct.unpack_from("<I", data, i + j)[0] for j in range(0, 32, 4)]
    if 0x18 in window and (0x60 in window or 0x34 in window or 0xF8 in window):
        print(f"  @{i:08x}  {['0x%x'%x for x in window]}")
        hits += 1
        if hits >= 30:
            break
print("clusters", hits)

# 3) xref: after each field name string, show following 16 bytes (maybe offset immediates nearby in rodata only)
print("\n== bytes after field name C-strings ==")
for name in [b"iID\x00", b"iCost\x00", b"sName\x00", b"sHeroPaintSmall\x00", b"heroId\x00"]:
    idx = 0
    n = 0
    while n < 5:
        i = data.find(name, idx)
        if i < 0:
            break
        tail = data[i : i + 32]
        print(name, hex(i), tail.hex())
        idx = i + 1
        n += 1

out = Path(r"D:\grok-cli\workspace\jcc-controller-251\worklog\orig_so_strings.txt")
with out.open("w", encoding="utf-8") as f:
    for off, s in strings:
        if any(c.isalpha() for c in s):
            f.write(f"{off:08x}\t{s}\n")
print("wrote", out)
