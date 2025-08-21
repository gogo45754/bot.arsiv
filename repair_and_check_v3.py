# repair_and_check_v3.py
from __future__ import annotations
from pathlib import Path
import re, py_compile, sys

ROOT = Path(__file__).resolve().parent
SRC  = ROOT / "src" / "kiripto_nova"
REPORT = ROOT / "compile_report.txt"

# “akıllı tırnak”, tire, üç nokta, NBSP/ZW*, BOM normalizasyonu
REPL = {
    "\u2018": "'",  "\u2019": "'",                      # ‘ ’  -> '
    "\u201C": '"',  "\u201D": '"',                      # “ ”  -> "
    "\u00AB": '"',  "\u00BB": '"',                      # « »  -> "
    "\u2013": "-",  "\u2014": "--",                     # – —  -> - / --
    "\u2026": "...",                                    # …    -> ...
    "\u00A0": " ",                                      # NBSP -> space
    "\u200B": "", "\u200C": "", "\u200D": "",           # ZW*  -> remove
    "\ufeff": "",                                       # BOM  -> remove
}

# cp1252/1254 yanlış çözülmüş tırnak dizileri
CP_REPL = {
    "â€™": "'", "â€˜": "'", "â€œ": '"', "â€\x9d": '"', "â€\x9c": '"',
    "â€“": "-", "â€”": "--", "â€¦": "...", "Â ": " ",
}

CTRL_CHARS = re.compile(r"[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F-\u009F]")

def maybe_demojibake(t: str) -> str:
    # Eğer metinde tipik mojibake izleri çoksa latin1->utf8 roundtrip dene
    if sum(t.count(c) for c in "ÃÂÄÅ") >= 3:
        try:
            t2 = t.encode("latin-1", "ignore").decode("utf-8", "ignore")
            # roundtrip işe yaradıysa geri dön
            if len(t2) and (t2.count(" ") <= t.count(" ")):
                return t2
        except Exception:
            pass
    return t

def clean_text(t: str) -> str:
    # önce olası mojibake'i düzelt
    t = maybe_demojibake(t)
    # cp1252 kalıntıları
    for a,b in CP_REPL.items():
        t = t.replace(a,b)
    # tek tek unicode normalizasyonları
    for a,b in REPL.items():
        t = t.replace(a,b)
    # kontrol karakterlerini sil
    t = CTRL_CHARS.sub("", t)
    # satır sonlarını normalize et
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    return t

bad, fixed, scanned, errors = [], 0, 0, []

for p in SRC.rglob("*.py"):
    if "__pycache__" in p.parts:
        continue
    scanned += 1
    try:
        raw = p.read_bytes()
        try:
            txt = raw.decode("utf-8")
        except UnicodeDecodeError:
            # son şans: latin-1 ile oku (tüm baytları kaybetmeden)
            txt = raw.decode("latin-1")

        cleaned = clean_text(txt)
        if cleaned != txt:
            p.write_text(cleaned, encoding="utf-8", newline="\n")
            fixed += 1
            print(f"[FIX] {p.relative_to(ROOT)}")

        # derleme kontrolü
        try:
            py_compile.compile(str(p), doraise=True)
        except Exception as e:
            bad.append(p)
            errors.append(f"[BAD ] {p} : {e}")
    except Exception as e:
        bad.append(p)
        errors.append(f"[ERR ] {p} : {e}")

REPORT.write_text(
    "Compile check complete.\n"
    f"Scanned: {scanned}, fixed: {fixed}, fails: {len(bad)}\n\n"
    + "\n".join(errors),
    encoding="utf-8"
)

print(f"Done. Scanned {scanned} files, fixed {fixed}.")
print(f"Compile check complete. Fails: {len(bad)}")
print(f"Report written to: {REPORT}")
sys.exit(1 if bad else 0)
