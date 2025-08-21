from pathlib import Path
import py_compile, sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src" / "kiripto_nova"

REPL = {
    "\u2018": "'", "\u2019": "'",     # ‘ ’  -> '
    "\u201C": '"', "\u201D": '"',     # “ ”  -> "
    "\u201E": '"', "\u201A": ',',     # „ ‚
    "\u00AB": '"', "\u00BB": '"',     # « »
    "\u2013": "-", "\u2014": "-",     # – —
    "\u2026": "...",                  # …
    "\u00A0": " ",                    # NBSP
    "\u200B": "",  "\u200C": "", "\u200D": "",  # ZW*
    "\ufeff": ""                      # BOM
}

bad = []
fixed = 0
scanned = 0
errors = []

def clean_text(t: str) -> str:
    for a, b in REPL.items():
        t = t.replace(a, b)
    return t

for p in SRC.rglob("*.py"):
    if "__pycache__" in p.parts:
        continue
    scanned += 1
    try:
        try:
            txt = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            txt = p.read_bytes().decode("utf-8", "replace")
        orig = txt
        txt = clean_text(txt)
        if txt != orig:
            try:
                p.write_text(txt, encoding="utf-8", newline="\n")
                print(f"[FIX ] {p.relative_to(ROOT)}")
                fixed += 1
            except PermissionError:
                print(f"[SKIP] {p.relative_to(ROOT)} (permission)")
        # compile check
        try:
            py_compile.compile(str(p), doraise=True)
        except Exception as e:
            bad.append(p)
            errors.append(f"[BAD ] {p} : {e}")
    except Exception as e:
        bad.append(p)
        errors.append(f"[ERR ] {p} : {e}")

report = ROOT / "compile_report.txt"
report.write_text("\n".join(errors), encoding="utf-8")
print(f"\nDone. Scanned {scanned} files, fixed {fixed}.")
print(f"Compile check complete. Fails: {len(bad)}")
print(f"Report written to: {report}")
