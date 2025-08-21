# ascii_fix.py  (ASCII-only repository sanitizer)
# Usage:  py -3.13 ascii_fix.py --root src

from __future__ import annotations
import argparse, sys, re, unicodedata
from pathlib import Path

FANCY_MAP = {
    "\u2018": "'", "\u2019": "'",    # single quotes
    "\u201C": '"', "\u201D": '"',    # double quotes
    "\u2013": "-", "\u2014": "-",    # dashes
    "\u2026": "...",                 # ellipsis
    "\u00A0": " ",                   # NBSP -> space
}
ZW_RE   = re.compile(r"[\u200B-\u200D\u2060]")   # zero-width and word joiners
C1_RE   = re.compile(r"[\u0080-\u009F]")         # C1 control block

def ascii_transliterate(s: str) -> str:
    # Decompose to base letters and strip combining marks, then special cases
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if ord(ch) < 128 or not unicodedata.combining(ch))
    # remove any remaining non-ascii
    return "".join(ch if ord(ch) < 128 else "?" for ch in s)

def maybe_fix_cp1252_mojibake(s: str) -> str:
    # Heuristic: if sequences like 'Ã', 'Ä', 'Å' are present, try latin1->utf8 roundtrip
    if any(x in s for x in ("Ã", "Ä", "Å")):
        try:
            repaired = s.encode("latin1", "ignore").decode("utf-8", "ignore")
            if sum(repaired.count(ch) for ch in "ÃÄÅ") < sum(s.count(ch) for ch in "ÃÄÅ"):
                return repaired
        except Exception:
            pass
    return s

def fix_text(raw: str) -> str:
    s = raw

    # Strip BOM at start if any
    if s.startswith("\ufeff"):
        s = s.lstrip("\ufeff")

    # Replace common fancy chars
    for k, v in FANCY_MAP.items():
        s = s.replace(k, v)

    # Remove zero-width and C1 controls
    s = ZW_RE.sub("", s)
    s = C1_RE.sub("", s)

    # Global NBSP/BOM that might remain
    s = s.replace("\u00A0", " ").replace("\ufeff", "")

    # Try to repair mojibake like 'Ã¶', then enforce ASCII
    s = maybe_fix_cp1252_mojibake(s)
    s = ascii_transliterate(s)

    return s

def process_file(p: Path) -> bool:
    orig = p.read_bytes()
    try:
        txt = orig.decode("utf-8", "replace")
    except Exception:
        txt = orig.decode("utf-8", "ignore")
    new = fix_text(txt)
    if new != txt:
        p.write_text(new, encoding="utf-8", newline="\n")
        return True
    return False

def main() -> int:
    ap = argparse.ArgumentParser(description="ASCII-only repo sanitizer")
    ap.add_argument("--root", default="src", help="directory to scan (default: src)")
    ap.add_argument("--exts", default="py,txt,md,json,yml,yaml", help="extensions csv")
    args = ap.parse_args()

    root = Path(args.root)
    exts = tuple("." + e.strip().lower() for e in args.exts.split(",") if e.strip())

    scanned = fixed = 0
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            scanned += 1
            try:
                if process_file(p):
                    fixed += 1
                    print(f"[FIX] {p}")
            except Exception as e:
                print(f"[ERR] {p} : {e}")
    print(f"Done. Scanned {scanned}, fixed {fixed}.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
