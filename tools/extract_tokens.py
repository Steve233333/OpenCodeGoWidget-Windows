#!/usr/bin/env python3
"""从 macOS 版源码扒设计 token，生成 Windows 版共用的 tokens.json / tokens.css。

用途：macOS 版改了配色或尺寸时重跑本脚本，两边就不会漂移。
    python3 tools/extract_tokens.py --source /path/to/OpenCodeGoWidget

默认从 design/tokens.json 同级的 .mac-source 文件读源码路径，或命令行传入。
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ModelPalette.swift 里的调色板：用于按模型名分配柱状图颜色
COLOR_RE = re.compile(
    r'"([^"]+)"\s*:\s*Color\(red:\s*([\d.]+),\s*green:\s*([\d.]+),\s*blue:\s*([\d.]+)\)'
)

# GoQuotaChart.swift 里的配额三段色（红/橙/绿）与免费金
NAMED_COLOR_RE = re.compile(
    r"private let (\w+): Color = Color\(red:\s*([\d.]+), green:\s*([\d.]+), blue:\s*([\d.]+)\)"
)


def _rgb(r: str, g: str, b: str) -> str:
    """SwiftUI 的 0~1 浮点色 → CSS hex，方便肉眼比对。"""
    vals = [round(float(v) * 255) for v in (r, g, b)]
    return "#" + "".join(f"{v:02x}" for v in vals)


def parse_palette(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    return {name: _rgb(r, g, b) for name, r, g, b in COLOR_RE.findall(text)}


def parse_named_colors(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    return {name: _rgb(r, g, b) for name, r, g, b in NAMED_COLOR_RE.findall(text)}


def build_tokens(source: Path) -> dict:
    palette = parse_palette(source / "Sources/ModelPalette.swift")
    quota_colors = parse_named_colors(source / "Sources/GoQuotaChart.swift")

    # 布局常量：直接对应 SwiftUI 里的数值，单位 px（1pt = 1px @1x）
    layout = {
        "window": {"width": 620, "height": 860},
        "header": {"paddingX": 18, "paddingTop": 16, "paddingBottom": 8},
        "stack": {"section": 16, "inner": 12, "tight": 6},
        "chart": {"height": 160},
        "quotaChart": {
            "padding": 10,
            "radius": 8,
            "rowHeight": 14,
            "rowGap": 5,
            "barHeight": 8,
            "modelColumnWidth": 150,
            "valueColumnWidth": 70,
            "rankWidth": 36,
            # 官网同款对数刻度：base + pow(log10(ratio)/log10(max), 2.2) * (宽-base)
            "axisBase": 24,
            "axisExponent": 2.2,
            "tickCandidates": [1, 5, 10, 25, 50, 100, 250, 500],
            "tickMinGap": 30,
        },
        "segmented": {
            "itemPaddingX": 10,
            "itemPaddingY": 4,
            "itemRadius": 5,
            "trackPadding": 2,
            "trackRadius": 7,
            "trackOpacity": 0.08,
        },
        "chip": {"paddingX": 6, "paddingY": 4, "radius": 6, "opacity": 0.06},
    }

    # 排版：SwiftUI 语义字号 → CSS px（按 macOS 语义字号的实际像素值取）
    typography = {
        "headline": 14,      # .headline
        "subheadline": 12,   # .subheadline
        "caption": 11,       # .caption
        "caption2": 10,      # .caption2
        "micro": 9,          # .system(size: 9)
        "nano": 8,           # .system(size: 8)
        "pico": 7,           # .system(size: 7)
        "fontFamily": {
            # macOS 用 SF Pro / 苹方；Windows 用 Inter / Noto Sans SC 替代
            # （SF Pro 是苹果授权字体，不能打包到 Windows）
            "mac": '-apple-system, "SF Pro Text", "PingFang SC", sans-serif',
            "windows": '"Inter", "Noto Sans SC", "Segoe UI Variable Text", sans-serif',
        },
    }

    return {
        "generatedFrom": str(source),
        "note": "由 tools/extract_tokens.py 自动生成，不要手改；改配色请改 macOS 版源码后重跑。",
        "palette": palette,
        "quotaColors": quota_colors,
        "layout": layout,
        "typography": typography,
    }


def to_css(tokens: dict) -> str:
    lines = [
        "/* 由 tools/extract_tokens.py 自动生成，不要手改 */",
        ":root {",
    ]
    for name, hexv in tokens["palette"].items():
        lines.append(f"  --model-{name}: {hexv};")
    for name, hexv in tokens["quotaColors"].items():
        lines.append(f"  --quota-{name}: {hexv};")
    layout = tokens["layout"]
    q = layout["quotaChart"]
    lines += [
        f"  --window-w: {layout['window']['width']}px;",
        f"  --window-h: {layout['window']['height']}px;",
        f"  --header-px: {layout['header']['paddingX']}px;",
        f"  --header-pt: {layout['header']['paddingTop']}px;",
        f"  --header-pb: {layout['header']['paddingBottom']}px;",
        f"  --gap-section: {layout['stack']['section']}px;",
        f"  --gap-inner: {layout['stack']['inner']}px;",
        f"  --gap-tight: {layout['stack']['tight']}px;",
        f"  --chart-h: {layout['chart']['height']}px;",
        f"  --quota-pad: {q['padding']}px;",
        f"  --quota-radius: {q['radius']}px;",
        f"  --quota-row-h: {q['rowHeight']}px;",
        f"  --quota-row-gap: {q['rowGap']}px;",
        f"  --quota-bar-h: {q['barHeight']}px;",
        f"  --quota-model-w: {q['modelColumnWidth']}px;",
        f"  --quota-value-w: {q['valueColumnWidth']}px;",
        f"  --quota-rank-w: {q['rankWidth']}px;",
    ]
    for key, size in tokens["typography"].items():
        if key == "fontFamily":
            continue
        lines.append(f"  --fs-{key}: {size}px;")
    lines.append("}")
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", help="macOS 版仓库根目录（含 Sources/ModelPalette.swift）")
    args = ap.parse_args()

    source = Path(args.source).expanduser() if args.source else None
    if source is None:
        marker = ROOT / "design" / ".mac-source"
        if marker.exists():
            source = Path(marker.read_text(encoding="utf-8").strip())
    if source is None or not (source / "Sources/ModelPalette.swift").exists():
        raise SystemExit("找不到 macOS 版源码，用 --source 指定仓库根目录")

    tokens = build_tokens(source)
    (ROOT / "design" / "tokens.json").write_text(
        json.dumps(tokens, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (ROOT / "design" / "tokens.css").write_text(to_css(tokens), encoding="utf-8")
    print(f"调色板 {len(tokens['palette'])} 项、配额色 {len(tokens['quotaColors'])} 项")
    print("已写出 design/tokens.json 与 design/tokens.css")


if __name__ == "__main__":
    main()
