#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimal nova_rescue.py  (sade sürüm)
- import satırlarını DÜZELTMEZ, dosya taşımayı yapar.
- plan: move_map.csv var ise doğrular, yoksa şablon üretir ve unmapped.txt yazar
- apply: move_map.csv'e göre taşır (dosyadan klasöre -> __init__.py kuralı var)
- ensure-init: src altında .py dosyası olan klasörlerde eksik __init__.py üretir
- compile: tek tek derler; compile_report.txt oluşturur
"""

from __future__ import annotations
import argparse, csv, sys, os, shutil, py_compile
from pathlib import Path

ENC = "utf-8"

def abspath(root: Path, p: str|Path) -> Path:
    p = Path(p)
    return p if p.is_absolute() else (root / p)

def load_move_map(csv_path: Path) -> list[tuple[str,str]]:
    rows: list[tuple[str,str]] = []
    if not csv_path.exists():
        return rows
    with open(csv_path, "r", encoding=ENC, errors="ignore", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            if row[0].strip().startswith("#"):
                continue
            # header toleransı
            if row[0].strip().lower() in {"src","src_path","from"}:
                continue
            src = (row[0] if len(row) > 0 else "").strip()
            dst = (row[1] if len(row) > 1 else "").strip()
            if src and dst:
                rows.append((src, dst))
    return rows

def write_template(csv_path: Path):
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    template = [
        ["# src_path", "dst_path"],
        ["# ÖRNEKLER:", ""],
        ["# src\\kiripto_nova\\strategies\\strategic_ai_engine.py",
         "src\\kiripto_nova\\strategies\\strategic_ai_engine"],  # klasöre => __init__.py
        ["# src\\kiripto_nova\\apps\\telegram_bot.py",
         "src\\kiripto_nova\\apps\\bots\\telegram_bot.py"],
    ]
    with open(csv_path, "w", encoding=ENC, newline="") as f:
        w = csv.writer(f)
        w.writerows(template)

def list_all_py(src_root: Path) -> list[Path]:
    return [p for p in src_root.rglob("*.py") if p.is_file()]

def cmd_plan(root: Path, src_dir: Path, csv_path: Path):
    mapping = load_move_map(csv_path)
    if not mapping:
        print(f"[PLAN] {csv_path} bulunamadı veya boş. Şablon oluşturuldu.")
        write_template(csv_path)
    py_files = list_all_py(src_dir)
    all_src_rel = {str(p.relative_to(root)).replace("/", "\\") for p in py_files}

    mapped_src = {s.replace("/", "\\") for s, _ in mapping}
    unmapped = sorted(all_src_rel - mapped_src)

    out = root / "unmapped.txt"
    out.write_text("\n".join(unmapped), encoding=ENC)
    print(f"[PLAN] Toplam .py: {len(all_src_rel)} | eşleşen: {len(mapped_src & all_src_rel)} | eşleşmeyen: {len(unmapped)}")
    print(f"[PLAN] unmapped.txt üretildi.")
    print(f"[PLAN] move_map.csv hazır / güncel: {csv_path.exists()}")

def safe_move_file(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    # aynı hedefe tekrar taşımaya tolerans
    if src.resolve() == dst.resolve():
        print(f"[SKIP] Aynı hedef: {src}")
        return
    shutil.move(str(src), str(dst))
    print(f"[MOVE] {src} -> {dst}")

def cmd_apply(root: Path, src_dir: Path, csv_path: Path):
    mapping = load_move_map(csv_path)
    if not mapping:
        print(f"[APPLY] {csv_path} boş ya da yok. Önce plan ve CSV’yi düzenleyin.")
        sys.exit(1)

    missing = []
    done = 0
    for s_rel, d_rel in mapping:
        s = abspath(root, s_rel)
        d = abspath(root, d_rel)

        if not s.exists():
            missing.append(s_rel)
            print(f"[MISS] Kaynak yok: {s_rel}")
            continue

        # Dosyayı paket klasöre dönüştürme kuralı:
        # hedef .py uzantısı yoksa ve kaynak .py ise -> hedef klasöre __init__.py
        if s.is_file() and s.suffix == ".py" and d.suffix == "":
            d.mkdir(parents=True, exist_ok=True)
            d = d / "__init__.py"

        try:
            safe_move_file(s, d)
            done += 1
        except Exception as e:
            print(f"[ERR ] {s_rel} -> {d_rel} :: {e}")

    if missing:
        (root / "missing_in_apply.txt").write_text("\n".join(missing), encoding=ENC)
        print(f"[APPLY] Bulunamayan {len(missing)} kaynak missing_in_apply.txt dosyasına yazıldı.")
    print(f"[APPLY] Tamamlanan taşıma: {done}")

def cmd_ensure_init(src_dir: Path):
    created = 0
    for d in src_dir.rglob("*"):
        if not d.is_dir():
            continue
        has_py = any((c.suffix == ".py") for c in d.iterdir() if c.is_file())
        if has_py:
            initp = d / "__init__.py"
            if not initp.exists():
                initp.write_text("# package marker\n", encoding=ENC)
                created += 1
                print(f"[INIT] {initp}")
    print(f"[INIT] Oluşturulan __init__.py: {created}")

def cmd_compile(src_dir: Path, root: Path):
    fails: list[tuple[str,str]] = []
    total = 0
    for p in src_dir.rglob("*.py"):
        if not p.is_file():
            continue
        total += 1
        try:
            py_compile.compile(str(p), doraise=True)
        except Exception as e:
            fails.append((str(p.relative_to(root)), str(e)))
            print(f"[BAD ] {p}: {e}")

    rpt = root / "compile_report.txt"
    with open(rpt, "w", encoding=ENC) as f:
        f.write(f"Total: {total}, Fails: {len(fails)}\n")
        for rel, msg in fails:
            f.write(f"{rel} :: {msg}\n")
    print(f"[COMPILE] Bitti. Toplam: {total}, Hatalı: {len(fails)}")
    print(f"[COMPILE] Rapor: {rpt}")

def main():
    ap = argparse.ArgumentParser(description="Nova kurtarma aracı (sade)")
    ap.add_argument("--project-root", default=".", help="Proje kökü (varsayılan .)")
    ap.add_argument("--src", default="src", help="Kaynak klasörü (varsayılan src)")
    ap.add_argument("--move-map", default="move_map.csv", help="Taşıma haritası CSV yolu")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("plan", help="move_map.csv için durum/şablon + unmapped.txt üret")
    sub.add_parser("apply", help="move_map.csv’e göre taşı")
    sub.add_parser("ensure-init", help="Eksik __init__.py dosyalarını üret")
    sub.add_parser("compile", help="Hızlı derleme testi ve rapor")

    args = ap.parse_args()

    root = Path(args.project_root).resolve()
    src_dir = (root / args.src).resolve()
    csv_path = (root / args.move_map).resolve()

    if args.cmd == "plan":
        cmd_plan(root, src_dir, csv_path)
    elif args.cmd == "apply":
        cmd_apply(root, src_dir, csv_path)
    elif args.cmd == "ensure-init":
        cmd_ensure_init(src_dir)
    elif args.cmd == "compile":
        cmd_compile(src_dir, root)

if __name__ == "__main__":
    main()

