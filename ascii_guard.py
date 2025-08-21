# ascii_guard.py  (fail build if any non-ASCII appears)
# Usage:  py -3.13 ascii_guard.py --root src

from __future__ import annotations
import argparse, sys, re
from pathlib import Path

NON_ASCII = re.compile(r"[^\x00-\x7F]")

def scan_file(p: Path) -> list[tuple[int, int, str]]:
    out = []
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        text = p.read_text(encoding="utf-8", errors="ignore")
    for i, line in enumerate(text.splitlines(True), 1):
        m = NON_ASCII.search(line)
        if m:
            col = m.start() + 1
            ch = m.group(0)
            out.append((i, col, f"U+{ord(ch):04X} '{ch.encode('unicode_escape').decode()}'"))
    return out

def main() -> int:
    ap = argparse.ArgumentParser(description="ASCII-only guard")
    ap.add_argument("--root", default="src", help="directory (default: src)")
    ap.add_argument("--exts", default="py,txt,md,json,yml,yaml", help="extensions csv")
    args = ap.parse_args()

    root = Path(args.root)
    exts = tuple("." + e.strip().lower() for e in args.exts.split(",") if e.strip())

    bad = 0
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            hits = scan_file(p)
            for i, col, info in hits:
                print(f"{p}:{i}:{col}: non-ASCII -> {info}")
                bad = 1
    if bad:
        print("FAILED: non-ASCII characters found.")
        return 1
    print("OK: ASCII-only.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
