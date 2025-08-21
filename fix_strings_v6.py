from __future__ import annotations
from pathlib import Path
import re, io, tokenize, py_compile, sys

ROOT = Path(__file__).resolve().parent
SRC  = ROOT/"src"/"kiripto_nova"

# Görünmez/fancy karakter düzeltmeleri (C1, ZW*, NBSP, BOM ve tipografik tırnaklar)
FANCY = {
    "\u2018":"'", "\u2019":"'", "\u201C":'"', "\u201D":'"',
    "\u2013":"-", "\u2014":"-", "\u2026":"...", "\u00A0":" ", "\ufeff":"",
}
C1_RE = re.compile(r"[\u0080-\u009F]")     # C1 kontrol bloğu
ZW_RE = re.compile(r"[\u200B\u200C\u200D\u2060]")  # ZW* görünmezler

# Yaygın Türkçe ve CP1252↔UTF8 mojibake düzeltmeleri
MOJI = {
    "Ã§":"ç","ÃÇ":"Ç","Ã¶":"ö","Ã–":"Ö","Ã¼":"ü","Ãœ":"Ü",
    "Ä±":"ı","Ã±":"ñ","Ä°":"İ","ÅŸ":"ş","Åž":"Ş","ÄŸ":"ğ","Äž":"Ğ",
    "â€“":"-","â€”":"-","â€˜":"'", "â€™":"'", "â€œ":'"', "â€":'"',
    "â€¦":"...", "â€¢":"*", "Â±":"±", "Â°":"°", "Â·":"·", "Â«":"«", "Â»":"»",
    "Â":"",   # tek başına kalmış “Â” gürültüsünü sil
}

# ± gibi sembolleri ASCII karşılıklarına isteğe göre sadeleştirmek istersen:
SYMBOL_SOFT = {"±":"+/-"}

def _apply_maps(s: str) -> str:
    for a,b in FANCY.items(): s = s.replace(a,b)
    s = C1_RE.sub("", s)
    s = ZW_RE.sub("", s)
    for a,b in MOJI.items(): s = s.replace(a,b)
    for a,b in SYMBOL_SOFT.items(): s = s.replace(a,b)
    return s

def fix_token_string(tok_text: str) -> str:
    """tokenize ile yakalanan STRING literalini güvenli biçimde normalize et."""
    # prefix (f, r, u, b, fr, rf ...) + açılış tırnağıları yakala
    m = re.match(r"(?i)^([urbf]*)(['\"])((?:.|\n)*)\2$", tok_text)
    if not m:
        # üç tırnaklı ya da farklı biçimleri olabilir; gene de içeriği temizle
        return _apply_maps(tok_text)
    pref, quote, inner = m.groups()
    inner = _apply_maps(inner)
    # satır sonlarında yanlış kaçışlardan doğan kırılmaları önlemek için backslash kaçır
    inner = inner.replace("\\\n", "\\n")
    return f"{pref}{quote}{inner}{quote}"

def clean_with_tokenize(text: str) -> tuple[bool,str]:
    """STRING/COMMENT alanlarını tokenize ederek temizle. TokenError olursa False döner."""
    out = []
    reader = io.StringIO(text).readline
    try:
        for tok in tokenize.generate_tokens(reader):
            ttype, tstring, start, end, line = tok
            if ttype in (tokenize.STRING, tokenize.COMMENT):
                tstring = fix_token_string(tstring)
            out.append(tokenize.TokenInfo(ttype, tstring, start, end, line))
        new = tokenize.untokenize(out)
        return True, new
    except tokenize.TokenError:
        return False, text  # sonra düz metin temizliğine düşeceğiz

def clean_file_text(text: str) -> str:
    # Dosya geneli görünmez & mojibake
    text = _apply_maps(text)
    # satır sonu devamı sonrası garip karakter hatasına sebep olan trailing backslash'ları toparla
    text = re.sub(r"\\\s*\n", r"\\\n", text)
    # karışık sekme/nbsp -> normal boşluk
    text = text.replace("\t", "    ")
    return text

def process_one(path: Path, relroot: Path) -> tuple[bool, str | None]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    ok, t1 = clean_with_tokenize(raw)
    new = clean_file_text(t1 if ok else raw)
    if new != raw:
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
        did, _ = process_one(p, ROOT)
        if did: fixed += 1
        try:
            compile_check(p)
        except Exception as e:
            bad += 1
            report.append(f"[BAD ] {p.relative_to(ROOT)} : {e.__class__.__name__}: {e}")
    except Exception as e:
        bad += 1
        report.append(f"[ERR ] {p.relative_to(ROOT)} : {e.__class__.__name__}: {e}")

rep = ROOT/"compile_report.txt"
rep.write_text("\n".join(report), encoding="utf-8")

print(f"Done. Scanned {scanned} files, fixed {fixed}.")
print(f"Compile check complete. Fails: {bad}")
print(f"Report written to: {rep}")
