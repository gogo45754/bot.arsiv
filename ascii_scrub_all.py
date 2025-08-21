import re, sys, pathlib

ROOT = pathlib.Path("src")

# C1 control, ZW*, BOM, NBSP, smart quotes, en dash, em dash, ellipsis
FANCY = {
    "\u00a0": " ",
    "\ufeff": "",
    "\u2018": "'", "\u2019": "'",
    "\u201c": '"', "\u201d": '"',
    "\u2013": "-", "\u2014": "-",
    "\u2026": "...",
}
RE_C1 = re.compile(r"[\u0080-\u009F]")
RE_ZW = re.compile(r"[\u2000-\u200f\u202a-\u202e\u2060-\u206f]")

def to_ascii(s: str) -> str:
    for a,b in FANCY.items():
        s = s.replace(a,b)
    s = RE_C1.sub("", s)
    s = RE_ZW.sub("", s)
    # drop remaining non-ascii
    return s.encode("ascii", "ignore").decode("ascii")

def clean_file(p: pathlib.Path) -> bool:
    try:
        txt = p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return False
    new = to_ascii(txt)
    if new != txt:
        p.write_text(new, encoding="utf-8", newline="\n")
        print(f"[FIX] {p}")
        return True
    return False

fixed = 0
scanned = 0
for p in ROOT.rglob("*"):
    if not p.is_file():
        continue
    if p.suffix.lower() not in {".py",".txt",".md",".json",".yml",".yaml"}:
        continue
    if any(part in {".git",".venv","venv","env","__pycache__"} for part in p.parts):
        continue
    scanned += 1
    try:
        if clean_file(p):
            fixed += 1
    except Exception as e:
        print(f"[ERR] {p}: {e}")

print(f"Done. Scanned: {scanned}, fixed: {fixed}.")
