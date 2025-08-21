# build_move_map.py
# Kiripto Nova: klasör şablonu kur + move_map.csv üret
from __future__ import annotations
from pathlib import Path
import argparse, csv, re

# ---- Şablon ve kurallar -----------------------------------------------------
BUCKETS = [
    "apps","analytics","backtesting","core","data","exchanges",
    "network","risk","signals","strategies","indicators"
]

# Şablonda alt klasör istiyorsan burada tanımla
SUBFOLDERS = {
    "analytics": ["onchain"],
    "data": ["pipelines"],
    "exchanges": ["binance"],
}

INIT_TEXT = '# -*- coding: utf-8 -*-\n"""Kiripto Nova package."""\n'

# İsim temelli kurallar
NAME_RULES: list[tuple[re.Pattern, str]] = [
    # Apps / bot / script
    (re.compile(r"^(nova_.*_bot|telegram_.*|auto_.*bot|boot|pro_(?:main|live)|run_.*|wep?soc(?:et|ket))\.py$", re.I), "apps"),
    # Signals (TR dâhil)
    (re.compile(r"(?:^|_)signal(?:s|_|\b)|sinyal|scanner|router", re.I), "signals"),
    # Strategies (TR dâhil)
    (re.compile(r"strateg(y|ies|ic)|strateji", re.I), "strategies"),
    # Backtesting / analiz
    (re.compile(r"backtest|testnet|tester|pnl|eval[_-]?error|analysis[_-]?graph", re.I), "backtesting"),
    # Exchanges
    (re.compile(r"binance|exchange|okx|bybit|kucoin", re.I), "exchanges"),
    # Risk
    (re.compile(r"\brisk(_|)|guard", re.I), "risk"),
    # Indicators
    (re.compile(r"indicator|rsi|macd|ema|sma|mom\b", re.I), "indicators"),
    # Analytics / on-chain
    (re.compile(r"analytic|onchain|chain|wallet_.*analyz|dashboard", re.I), "analytics"),
    # Core / engine
    (re.compile(r".*(_)?engine|config_loader|decision|alpha|neural|core|scheduler", re.I), "core"),
    # Data pipelines
    (re.compile(r"data[_-]?loader|twitter[_-]?data|pipeline", re.I), "data"),
]

# Yol temelli kurallar
PATH_RULES: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\\?tests?\\", re.I), "apps"),
    (re.compile(r"\\?backtest", re.I), "backtesting"),
    (re.compile(r"\\?analytics", re.I), "analytics"),
    (re.compile(r"\\?signals?", re.I), "signals"),
    (re.compile(r"\\?strateg", re.I), "strategies"),
    (re.compile(r"\\?exchanges?", re.I), "exchanges"),
    (re.compile(r"\\?risk", re.I), "risk"),
    (re.compile(r"\\?core", re.I), "core"),
    (re.compile(r"\\?data(\\|/)?pipelines?", re.I), "data"),
]

IGNORE_TOP = {
    "src", ".git", ".hg", ".svn", ".venv", "venv", "__pycache__", ".mypy_cache",
    ".idea", ".vscode", "dist", "build", ".pytest_cache"
}
IGNORE_FILES = {"nova_rescue.py", "rearrange_v2.py", "auto_move_map.py", "auto_full_plan.py", "build_move_map.py"}

# İsteğe bağlı özel yönlendirmeler
OVERRIDES: dict[str, str] = {
    # "backtester.py": "backtesting/backtester.py",
    # "analysis_graphs.py": "analytics/analysis_graphs.py",
}

# ---- Yardımcılar ------------------------------------------------------------
def ensure_template(pkg_root: Path, make_template: bool, ensure_init: bool):
    if not make_template and not ensure_init:
        return
    pkg_root.mkdir(parents=True, exist_ok=True)
    wanted: list[Path] = []
    for b in BUCKETS:
        base = pkg_root / b
        wanted.append(base)
        for sub in SUBFOLDERS.get(b, []):
            wanted.append(base / sub)
    for d in wanted:
        d.mkdir(parents=True, exist_ok=True)
        if ensure_init:
            ini = d / "__init__.py"
            if not ini.exists():
                ini.write_text(INIT_TEXT, encoding="utf-8")
    if ensure_init:
        root_init = pkg_root / "__init__.py"
        if not root_init.exists():
            root_init.write_text(INIT_TEXT, encoding="utf-8")

def guess_bucket(rel_path: Path) -> str:
    rel_str = str(rel_path)
    for pat, bucket in PATH_RULES:
        if pat.search(rel_str):
            return bucket
    name = rel_path.name
    for pat, bucket in NAME_RULES:
        if pat.match(name):
            return bucket
    return "apps"  # varsayılan

def should_skip(p: Path, project_root: Path, pkg_root: Path) -> bool:
    rel = p.relative_to(project_root)
    if rel.parts and rel.parts[0] in IGNORE_TOP:
        return True
    if p.suffix.lower() != ".py":
        return True
    if p.name in IGNORE_FILES:
        return True
    # zaten hedef paket altında olanları alma
    try:
        p.relative_to(pkg_root)
        return True
    except ValueError:
        return False

# ---- Main -------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Şablon kur + move_map.csv üret")
    ap.add_argument("--project-root", default=".", help="Proje kökü (.)")
    ap.add_argument("--src", default="src", help="Kaynak klasörü (src)")
    ap.add_argument("--package", default="kiripto_nova", help="Paket adı (kiripto_nova)")
    ap.add_argument("--out", default="move_map.csv", help="Çıktı CSV")
    ap.add_argument("--make-template", action="store_true", help="Standart klasör şablonunu oluştur")
    ap.add_argument("--ensure-init", action="store_true", help="Tüm paket klasörlerine __init__.py ekle")
    ap.add_argument("--unmapped", default="unmapped.txt", help="Varsayılan (apps) gidenleri listele")
    args = ap.parse_args()

    PROJECT = Path(args.project_root).resolve()
    SRC = PROJECT / args.src
    PKG = SRC / args.package

    # Şablon + init (dosya içeriklerini açmadan)
    ensure_template(PKG, args.make_template, args.ensure_init)

    candidates: list[Path] = []
    for p in PROJECT.rglob("*.py"):
        if should_skip(p, PROJECT, PKG):
            continue
        candidates.append(p)

    seen_dest: set[Path] = set()
    rows: list[tuple[str, str]] = []
    defaulted: list[str] = []

    for p in sorted(candidates):
        rel = p.relative_to(PROJECT)
        ov = OVERRIDES.get(rel.as_posix()) or OVERRIDES.get(rel.name)
        if ov:
            dest = PKG / ov
        else:
            bucket = guess_bucket(rel)
            dest = PKG / bucket / p.name
            if bucket == "apps":  # varsayılanı ayrıca kaydet
                defaulted.append(rel.as_posix())

        # Çakışmaları benzersizleştir
        base, ext, i = dest.stem, dest.suffix, 1
        while dest in seen_dest or dest.exists():
            dest = dest.with_name(f"{base}_{i}{ext}")
            i += 1
        seen_dest.add(dest)

        rows.append((rel.as_posix(), dest.as_posix()))

    out_csv = PROJECT / args.out
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["old", "new"])
        w.writerows(rows)

    if defaulted:
        (PROJECT / args.unmapped).write_text("\n".join(defaulted), encoding="utf-8")

    print(f"[OK] {out_csv.name} yazıldı (eşleşme: {len(rows)}).")
    if defaulted:
        print(f"[INFO] Varsayılan (apps) atanan {len(defaulted)} dosya -> {args.unmapped}")

    for s, d in rows[:10]:
        print("  ", s, "->", d)

if __name__ == "__main__":
    main()
