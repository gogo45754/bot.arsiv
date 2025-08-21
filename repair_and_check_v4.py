from pathlib import Path
import py_compile, sys

ROOT = Path(__file__).resolve().parent
SRC  = ROOT / "src" / "kiripto_nova"

# Görünmez/akıllı tırnak vb.
REPL = {
    "\u2018": "'", "\u2019": "'",
    "\u201C": '"', "\u201D": '"',
    "\u2013": "-",  "\u2014": "-",
    "\u00A0": " ",  # NBSP
    "\u200B": "", "\u200C": "", "\u200D": "",  # ZW*
    "\uFEFF": "",   # BOM
    "Â": "",        # C1 işareti (çoğu zaman gereksiz)
}

# Türkçe mojibake düzeltmeleri
MOJI = {
    "Ã§":"ç","ÃÇ":"Ç","Ã‡":"Ç",
    "Ã¶":"ö","Ã–":"Ö",
    "Ã¼":"ü","Ãœ":"Ü",
    "Ä±":"ı","Ä°":"İ",
    "ÅŸ":"ş","Åž":"Ş",
    "ÄŸ":"ğ","Äž":"Ğ",
    "â€™":"'", "â€˜":"'",
    "â€œ":'"', "â€":'"',
    "â€“":"-", "â€”":"-",
    "â€¦":"...",
}

def clean_text(t: str) -> str:
    for a,b in {**REPL, **MOJI}.items():
        t = t.replace(a,b)
    return t

bad, errors = [], []
fixed = scanned = 0

for p in SRC.rglob("*.py"):
    if "__pycache__" in p.parts: 
        continue
    try:
        s  = p.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        errors.append(f"[ERR ] {p} : {e}")
        continue
    s2 = clean_text(s)
    if s2 != s:
        p.write_text(s2, encoding="utf-8", newline="\n")
        fixed += 1
    scanned += 1
    try:
        py_compile.compile(str(p), doraise=True)
    except Exception as e:
        bad.append(f"[BAD ] {p} : {e}")

rep = ROOT / "compile_report.txt"
rep.write_text("\n".join(bad + errors), encoding="utf-8")

print(f"Done. Scanned {scanned} files, fixed {fixed}.")
print(f"Compile check complete. Fails: {len(bad)}")
print(f"Report written to: {rep}")
