# repair_and_check.py
from pathlib import Path
import sys, re, py_compile

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("src/kiripto_nova")

def looks_mojibake(s: str) -> int:
    # Ã, Â, Ä, Å, â kalıntıları çoksa puan yükselir
    return sum(s.count(ch) for ch in "ÃÂÄÅâ")

REPL_TABLE = {
    "\ufeff": "",      # BOM
    "\u00a0": " ",     # NBSP -> boşluk
    "“": '"', "”": '"', "„": '"', "«": '"', "»": '"',
    "‘": "'", "’": "'", "‚": "'",
    "—": "-", "–": "-",
    "…": "...",
}

# Görünmez karakter aralığı (ZWS vb.) kaldır
INVISIBLES = {ord(c): None for r in [(0x2000,0x200F),(0x202A,0x202E),(0x2066,0x2069)]
              for c in map(chr, range(r[0], r[1]+1))}

def normalize_text(t: str) -> str:
    # Yaygın mojibake -> gerçek UTF-8 (örn. 'Ã–' -> 'Ö')
    repaired = t.encode("latin1", "ignore").decode("utf-8", "ignore")
    if looks_mojibake(repaired) < looks_mojibake(t):
        t = repaired
    # Akıllı tırnak, tire, NBSP, görünmezler, // -> #
    for a, b in REPL_TABLE.items():
        t = t.replace(a, b)
    t = t.translate(INVISIBLES)
    t = re.sub(r"^(\s*)//", r"\1# ", t, flags=re.M)
    # Satır sonlarını normalize et, kuyruğu buda
    t = "\n".join(line.rstrip() for line in t.splitlines()) + "\n"
    return t

def fix_file(p: Path) -> bool:
    raw = p.read_text(encoding="utf-8", errors="replace")
    new = normalize_text(raw)
    if new != raw:
        p.write_text(new, encoding="utf-8", newline="\n")
        return True
    return False

def repair(root: Path):
    fixed = 0; total = 0
    for p in sorted(root.rglob("*.py")):
        total += 1
        try:
            if fix_file(p):
                print(f"[FIX ] {p}")
                fixed += 1
        except Exception as e:
            print(f"[SKIP] {p} -> {e}")
    print(f"\nDone. Scanned {total} files, fixed {fixed}.")

def preflight(root: Path, report: Path):
    fails = []
    for p in sorted(root.rglob("*.py")):
        try:
            py_compile.compile(str(p), doraise=True)
        except Exception as e:
            fails.append((p, f"{e.__class__.__name__}: {e}"))
    report.write_text(
        "TOTAL FAILS: " + str(len(fails)) + "\n\n" +
        "\n".join(f"{p}\n    {err}\n" for p, err in fails),
        encoding="utf-8"
    )
    print(f"\nCompile check complete. Fails: {len(fails)}")
    print(f"Report written to: {report}")

if __name__ == "__main__":
    root = ROOT
    print(f"Root: {root.resolve()}")
    if not root.exists():
        print("ERROR: root not found."); sys.exit(1)
    repair(root)
    preflight(root, Path("compile_report.txt"))
