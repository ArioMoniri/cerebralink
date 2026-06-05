#!/usr/bin/env python3
"""Redact sensitive regions of a screenshot before it goes into a public repo.

Blurs (or solid-boxes) rectangular regions — patient names, protocol IDs, doctor
names, dates of birth, MRNs — so screenshots from a live instance can be shown in
the README without leaking PHI.

Uses ImageMagick (`magick`). Regions are given as `x,y,w,h` in pixels (top-left
origin). Use `--box` for opaque redaction (safest — irreversible) or the default
heavy blur.

Examples
--------
# Blur two regions:
python scripts/redact_screenshot.py raw/chat.png docs/assets/screenshots/chat-real.png \
    --region 120,80,260,24 --region 40,300,300,18

# Opaque black boxes instead of blur:
python scripts/redact_screenshot.py raw/assessment.png out.png --box --region 90,40,380,22

Tip: open the image, read off the pixel rectangle of each sensitive label, and pass
one --region per item. `magick identify -format '%wx%h' file.png` prints the size.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys


def main() -> int:
    ap = argparse.ArgumentParser(description="Redact rectangular regions of an image.")
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--region", action="append", default=[], metavar="x,y,w,h",
                    help="region to redact (pixels, top-left origin); repeatable")
    ap.add_argument("--box", action="store_true", help="opaque box instead of blur (safest)")
    ap.add_argument("--blur", default="0x18", help="blur sigma when not --box (default 0x18)")
    ap.add_argument("--color", default="#0b0f2a", help="box color when --box (default theme navy)")
    args = ap.parse_args()

    magick = shutil.which("magick") or shutil.which("convert")
    if not magick:
        print("ERROR: ImageMagick not found (install with `brew install imagemagick`).", file=sys.stderr)
        return 2
    if not args.region:
        print("ERROR: pass at least one --region x,y,w,h", file=sys.stderr)
        return 2

    cmd: list[str] = [magick, args.input]
    for r in args.region:
        try:
            x, y, w, h = (int(v) for v in r.split(","))
        except ValueError:
            print(f"ERROR: bad --region '{r}' (want x,y,w,h)", file=sys.stderr)
            return 2
        geom = f"{w}x{h}+{x}+{y}"
        if args.box:
            cmd += ["-fill", args.color, "-draw", f"rectangle {x},{y} {x + w},{y + h}"]
        else:
            # blur only inside the region
            cmd += ["-region", geom, "-blur", args.blur, "+region"]
    cmd += [args.output]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stderr.strip() or "magick failed", file=sys.stderr)
        return proc.returncode
    print(f"redacted → {args.output} ({len(args.region)} region(s), {'box' if args.box else 'blur'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
