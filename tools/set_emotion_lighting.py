"""Insert a per-emotion `灯光氛围（检验视频）:` line into each `_emotion.md`
(after the 功能主轴 line). The performance test videos are shot in a simple
表演室 with lighting that fits the emotion (per the user's generic-library
design) — this line is the single source of truth the prompt rewriter reads.
Idempotent.
"""
from __future__ import annotations

import sys
from pathlib import Path

PERF_ROOT = Path(__file__).resolve().parent.parent / "ai_videos" / "_performances"

LIGHTING = {
    "yayi_yinren": "冷调低饱和、柔和侧光、略压暗（窒息感）",
    "shuanggan_fanzhuan": "明亮高调、主光偏正、轻微冷暖对比（敞亮、扬眉吐气）",
    "bengkui_shikong": "冷调低饱和、环境光收暗、单侧柔光（孤立、失温）",
    "henli_yinzhi": "低调硬光、侧逆光打出半脸阴影（压迫、威胁）",
    "zhenjing_cuoe": "中性偏冷、略高对比、清晰（瞬间击穿感）",
    "rouqing_shenqing": "暖调柔光、低对比、浅景深氛围（亲密、放软）",
    "weiqu_kelian": "柔光偏暖、眼神光点亮泪膜、略俯柔（楚楚、示弱）",
    "buxie_chaofeng": "中性偏冷、清晰平光（居高临下的清醒）",
    "xiuru_nankan": "冷调、略不安的侧光（难堪、失血感）",
    "waifang_fennu": "硬光高对比、略偏暖（火气、逼迫）",
}

MARKER = "灯光氛围（检验视频）:"


def main() -> None:
    touched = 0
    for slug, lighting in LIGHTING.items():
        md = PERF_ROOT / slug / "_emotion.md"
        if not md.is_file():
            continue
        lines = md.read_text(encoding="utf-8").splitlines()
        if any(line.startswith(MARKER) for line in lines):
            continue
        out: list[str] = []
        inserted = False
        for line in lines:
            out.append(line)
            if not inserted and line.startswith("功能主轴"):
                out.append("")
                out.append(f"{MARKER} {lighting}")
                inserted = True
        if not inserted:
            # no 功能主轴 line: insert after H1
            out = []
            for i, line in enumerate(lines):
                out.append(line)
                if i == 0 and line.startswith("# "):
                    out.append("")
                    out.append(f"{MARKER} {lighting}")
                    inserted = True
        md.write_text("\n".join(out) + "\n", encoding="utf-8")
        touched += 1
    sys.stdout.write(f"set lighting on {touched} _emotion.md files\n")


if __name__ == "__main__":
    main()
