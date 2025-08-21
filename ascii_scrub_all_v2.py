from pathlib import Path
import sys, unicodedata

ROOT = Path("src")
EXCLUDE_DIRS = {".git", ".venv", "venv", "env", "__pycache__", "tools", "backup_"}
EXTS = {".py",".txt",".md",".json",".yml",".yaml"}

# Common mojibake pairs (utf-8 bytes misread as cp1252/latin-1)
MOJI = {
    "\u00C3\u0087":"C", "\u00C3\u0096":"O", "\u00C3\u009C":"U",
    "\u00C4\u00B0":"I", "\u00C5\u009E":"S", "\u00C4\u009E":"G",
    "\u00C3\u00A7":"c", "\u00C3\u00B6":"o", "\u00C3\u00BC":"u",
    "\u00C4\u00B1":"i", "\u00C5\u009F":"s", "\u00C4\u009F":"g",
    # curly quotes/dash/ellipsis seen as mojibake
    "\u00E2\u0080\u0098":"'", "\u00E2\u0080\u0099":"'",
    "\u00E2\u0080\u009C":'"', "\u00E2\u0080\u009D":'"',
    "\u00E2\u0080\u0093":"-", "\u00E2\u0080\u0094":"-",
    "\u00E2\u0080\u00A6":"...",
}

# invisibles
REPL = {
    "\u00A0":" ",   # NBSP
    "\uFEFF":"",   # BOM
}

def reverse_mojibake(s: str) -> str:
    """
    Try to undo utf-8 -> cp1252/latin-1 mojibake by reinterpreting bytes.
    """
    try:
        # take current text as cp1252/latin-1 bytes, then decode as utf-8
        fixed = s.encode("latin-1", errors="ignore").decode("utf-8", errors="ignore")
        # only keep if it actually helped
        return fixed if sum(ord(c)>127 for c in fixed) <= sum(ord(c)>127 for c in s) else s
    except Exception:
        return s

def fold_ascii(s: str) -> str:
    for a,b in REPL.items():
        s = s.replace(a,b)
    for a,b in MOJI.items():
        s = s.replace(a,b)
    # generic unicode fold
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if ord(ch) < 128)
    return s

def should_skip(p: Path) -> bool:
    if not p.suffix.lower() in EXTS:
        return True
    for part in p.parts:
        if part in EXCLUDE_DIRS:
            return True
    return False

scanned = fixed = 0
for p in ROOT.rglob("*"):
    if not p.is_file() or should_skip(p):
        continue
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        continue
    orig = text
    text = reverse_mojibake(text)
    text = fold_ascii(text)
    scanned += 1
    if text != orig:
        p.write_text(text, encoding="utf-8", newline="\n")
        print(f"[FIX] {p}")
        fixed += 1

print(f"Done. Scanned {scanned}, fixed {fixed}.")
