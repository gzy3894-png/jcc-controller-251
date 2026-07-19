#!/usr/bin/env python3
"""Enumerate all class_get_method_from_name resolve sites (bl 0x77e94) and verify vs IDMAP."""
from __future__ import annotations

import re
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM64, CS_MODE_ARM, Cs

SO = Path(r"D:\grok-cli\workspace\jcc-controller-251\dist\libJCC.patched.so")
if not SO.exists():
    SO = Path(r"D:\grok-cli\workspace\jcc-controller-work\extract\assets\emu\libJCC.so")
DUMP = Path(r"D:\grok-cli\workspace\jcc-game-dump\il2cpp-out\dump.cs")
OUT = Path(r"D:\grok-cli\workspace\jcc-controller-251\worklog\RESOLVE-AUDIT.md")

RESOLVE_BL = 0x77E94  # bl target for resolve helper


def read_cstr(data: bytes, va: int) -> str:
    if va < 0 or va >= len(data):
        return "?"
    return data[va:].split(b"\x00", 1)[0].decode("utf-8", "replace")


def decode_adrp(word: int, pc: int) -> tuple[int, int]:
    rd = word & 0x1F
    immlo = (word >> 29) & 3
    immhi = (word >> 5) & 0x7FFFF
    imm = (immhi << 2) | immlo
    if imm & (1 << 20):
        imm -= 1 << 21
    return rd, (pc & ~0xFFF) + (imm << 12)


def decode_add(word: int) -> tuple[int, int, int]:
    return word & 0x1F, (word >> 5) & 0x1F, (word >> 10) & 0xFFF


def main():
    data = SO.read_bytes()
    dump = DUMP.read_text(encoding="utf-8", errors="ignore")
    idmaps = set(re.findall(r"public const IDMAP\d+\s+(\S+)\s*=", dump))

    md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    text = data[0x77BB0 : 0x77BB0 + 0x94F28]
    insns = list(md.disasm(text, 0x77BB0))

    # index by address
    by_addr = {i.address: i for i in insns}

    results = []
    for insn in insns:
        if insn.mnemonic != "bl":
            continue
        # bl #0x77e94
        m = re.match(r"#?(0x[0-9a-fA-F]+)", insn.op_str)
        if not m or int(m.group(1), 0) != RESOLVE_BL:
            continue
        # look back up to 12 insns for adrp/add into x1,x2 and mov w3
        pc = insn.address
        class_va = meth_va = None
        argc = None
        # scan previous instructions in by_addr
        for back in range(4, 48, 4):
            a = pc - back
            if a not in by_addr:
                continue
            prev = by_addr[a]
            if prev.mnemonic == "mov" and "w3" in prev.op_str:
                mm = re.search(r"w3,\s*#(0x[0-9a-fA-F]+|\d+)", prev.op_str)
                if mm:
                    argc = int(mm.group(1), 0)
                elif "wzr" in prev.op_str:
                    argc = 0
            # raw decode adrp/add for x1/x2
            w = struct.unpack_from("<I", data, a)[0]
            if (w & 0x9F00001F) == 0x90000000 or (w >> 24) in (0x90, 0xB0, 0xD0, 0xF0):
                # adrp family - check with capstone
                if prev.mnemonic == "adrp":
                    rd, page = decode_adrp(w, a)
                    # find following add
                    if a + 4 in by_addr and by_addr[a + 4].mnemonic == "add":
                        w2 = struct.unpack_from("<I", data, a + 4)[0]
                        rd2, rn2, imm12 = decode_add(w2)
                        if rn2 == rd:
                            va = page + imm12
                            if rd2 == 1:
                                class_va = va
                            elif rd2 == 2:
                                meth_va = va

        cls = read_cstr(data, class_va) if class_va else "?"
        meth = read_cstr(data, meth_va) if meth_va else "?"
        # IDMAP check: Namespace-Class-Method0 or Class-Method
        ok = False
        idmap_hit = []
        for im in idmaps:
            if meth != "?" and meth in im and (cls == "?" or cls in im):
                ok = True
                idmap_hit.append(im)
        if not ok and meth != "?":
            for im in idmaps:
                if im.endswith(meth + "0") or f"-{meth}0" in im:
                    idmap_hit.append(im)
                    ok = True
        results.append(
            {
                "pc": pc,
                "class": cls,
                "method": meth,
                "argc": argc,
                "ok": ok,
                "idmap": idmap_hit[:3],
            }
        )

    lines = [
        f"# Resolve audit ({SO.name})\n\n",
        f"Total bl resolve sites: {len(results)}\n\n",
        "| PC | Class | Method | argc | IDMAP? | hits |\n",
        "|----|-------|--------|------|--------|------|\n",
    ]
    bad = []
    for r in results:
        mark = "OK" if r["ok"] else "**FAIL?**"
        if not r["ok"]:
            bad.append(r)
        lines.append(
            f"| 0x{r['pc']:x} | `{r['class']}` | `{r['method']}` | {r['argc']} | {mark} | {', '.join(r['idmap'][:2])} |\n"
        )

    lines.append(f"\n## Suspicious resolves: {len(bad)}\n\n")
    for r in bad:
        lines.append(
            f"- 0x{r['pc']:x} `{r['class']}.{r['method']}` argc={r['argc']}\n"
        )

    lines.append(
        """
## Interpretation

- **OK**: IDMAP contains Class-Method (method still registered in current game).
- **FAIL?**: no IDMAP hit — hook/resolve likely broken on current season (patch candidate).

Note: IDMAP may keep stale names; class method list is stronger when dump has methods.
BuyHeroView.OnRefreshHeroRet is FAIL in method list despite IDMAP — already patched in 2.5.4.
"""
    )
    OUT.write_text("".join(lines), encoding="utf-8")
    print("wrote", OUT, "sites", len(results), "bad", len(bad))
    for r in bad[:30]:
        print(f"BAD 0x{r['pc']:x} {r['class']}.{r['method']} argc={r['argc']}")


if __name__ == "__main__":
    main()
