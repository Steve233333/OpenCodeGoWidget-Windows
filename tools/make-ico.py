#!/usr/bin/env python3
"""把 PNG 打包成 Windows .ico（Vista 起支持内嵌 PNG，不需要额外依赖）。

    python3 tools/make-ico.py out.ico in16.png in32.png in128.png in256.png
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path


def build_ico(pngs: list[Path]) -> bytes:
    images = [p.read_bytes() for p in pngs]
    header = struct.pack("<HHH", 0, 1, len(images))
    offset = len(header) + 16 * len(images)
    entries, payload = b"", b""
    for png, data in zip(pngs, images):
        width = height = 0 if "256" in png.name else int(png.stem.split("-")[1])
        entries += struct.pack("<BBBBHHII", width, height, 0, 0, 1, 32, len(data), offset)
        payload += data
        offset += len(data)
    return header + entries + payload


def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    out = Path(sys.argv[1])
    pngs = [Path(p) for p in sys.argv[2:]]
    out.write_bytes(build_ico(pngs))
    print(f"{out} ← {', '.join(p.name for p in pngs)}（{out.stat().st_size} 字节）")


if __name__ == "__main__":
    main()
