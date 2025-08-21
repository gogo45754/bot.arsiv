from pathlib import Path
import re, io, tokenize, token, py_compile, sys

ROOT = Path(__file__).resolve().parent
SRC  = ROOT / "src" / "kiripto_nova"

# Görünmez/fancy karakter düzeltmeleri
FANCY = {
    "\u2018": "'", "\u2019": "'",  # ‘ ’ -> '
    "\u201C": '"', "\u201D": '"',  # “ ” -> "
    "\u2013": "-", "\u2014": "-",  # – — -> -
    "\u00A0": " ",                 # NBSP -> normal boşluk
    "\ufeff": "",                  # BOM
}
C1_RE   = re.compile(r"[\u0080-\u009F]")        # C1 control block
ZW_RE   = re.compile(r"[\u200B\u200C\u200D\u2060]")  # ZW* görünmezler

# Yaygın Türkçe mojibake düzeltmeleri
MOJI = {
    "Ä°": "İ", "Ä±": "ı", "Ã¼": "ü", "Ãœ": "Ü", "Ã§": "ç", "Ã‡": "Ç",
    "Ã¶": "ö", "Ã–": "Ö", "ÅŸ": "ş", "Åž": "Ş", "ÄŸ": "ğ", "Äž": "Ğ",
    "Â°": "°", "Â±": "±", "Â·": "·", "Â«": "«", "Â»": "»",
}
# Bazı metinlerde 'Â' tek başına giriyor; genelde gürültü
STRIP_A_CARET = True

def fix_fragment(s: str) -> str:
    # Fancy & görünmezler
    for a, b in FANCY.items():
        s = s.replace(a, b)
    s = C1_RE.sub("", s)
    s = ZW_RE.sub("", s)
    if STRIP_A_CARET:
        s = s.replace("Â", "")
    # Türkçe mojibake
    for a, b in MOJI.items():
        if a in s:
            s = s.replace(a, b)
    # UTF-8 -> Latin-1 karışması varsa “Ã, Å, Ä” gibi ipuçlarına bak
    if any(x in s for x in ("Ã", "Å", "Ä")):
        try:
            s2 = s.encode("latin-1").decode("utf-8")
            # yeniden bozulma riskine karşı sadece iyileşmişse uygula
            if sum(map(ord, s2)) <= sum(map(ord, s)):
                s = s2
        except Exception:
            pass
    return s

def clean_file_text(text: str) -> str:
    # Dosya genelinde NBSP -> ' ' (indent sorunlarını çözer)
    text = text.replace("\u00A0", " ").replace("\ufeff", "")
    out_tokens = []
    changed = False
    src = io.StringIO(text)
    for tok in tokenize.generate_tokens(src.readline):
        ttype, tstring, start, end, line = tok
        if ttype in (token.STRING, tokenize.COMMENT):
            new_s = fix_fragment(tstring)
            if new_s != tstring:
                changed = True
            out_tokens.append(tokenize.TokenInfo(ttype, new_s, start, end, line))
        else:
            out_tokens.append(tok)
    new_text = tokenize.untokenize(out_tokens)
    # Güvenlik: C1 ve ZW kalmadığından emin ol
    new_text = C1_RE.sub("", new_text)
    new_text = ZW_RE.sub("", new_text)
    return new_text if new_text != text else text

def process_one(path: Path, relroot: Path) -> tuple[bool, str|None]:
    txt = path.read_text(encoding="utf-8", errors="replace")
    new = clean_file_text(txt)
    if new != txt:
        path.write_text(new, encoding="utf-8", newline="\n")
        print(f"[FIX] {path.relative_to(relroot)}")
        return True, None
    return False, None

def compile_check(path: Path):
    py_compile.compile(str(path), doraise=True)

report = []
scanned = fixed = bad = 0

for p in SRC.rglob("*.py"):
    if "__pycache__" in p.parts:
        continue
    scanned += 1
    try:
        did_fix, _ = process_one(p, ROOT)
        if did_fix:
            fixed += 1
        try:
            compile_check(p)
        except Exception as e:
            bad += 1
            report.append(f"[BAD ] {p} : {e.__class__.__name__}: {e}")
    except Exception as e:
        bad += 1
        report.append(f"[ERR ] {p} : {e.__class__.__name__}: {e}")

rep = ROOT / "compile_report.txt"
rep.write_text("\n".join(report), encoding="utf-8")

print(f"Done. Scanned {scanned} files, fixed {fixed}.")
print(f"Compile check complete. Fails: {bad}")
print(f"Report written to: {rep}")
