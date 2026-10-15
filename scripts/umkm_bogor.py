#!/usr/bin/env python3
"""Direktori UMKM Kota Bogor — API publik SOLUSI, disaring jadi usaha yang benar-benar ada.

  umkm_bogor.py search --grep "kopi|kue" --limit 10
  umkm_bogor.py search --kecamatan "Bogor Utara" --min-workers 5 --json out.json
  umkm_bogor.py stats
  umkm_bogor.py get --id 12345
Data disimpan 24 jam di $UMKM_CACHE (default ~/.cache/umkm-bogor); --refresh memaksa unduh ulang.
"""
import argparse, json, re, sys, urllib.request

BASE = "https://api-solusi.kotabogor.go.id/api"
CACHE_DIR = os.environ.get("UMKM_CACHE", os.path.expanduser("~/.cache/umkm-bogor"))

JUNK_WORDS = {"none", "test", "tes", "tes12", "x", "zxc", "-", "warung sembako", "warung makan"}


def fetch(path):
    return json.loads(urllib.request.urlopen(f"{BASE}/{path}", timeout=90).read().decode())


def num(v):
    s = re.sub(r"[^0-9]", "", str(v or ""))
    return int(s) if s else 0


def junk(*values):
    for v in values:
        t = str(v or "").strip().lower()
        if not t or t in JUNK_WORDS:
            return True
        if re.fullmatch(r"(test|tes|coba|dummy|contoh|asd\w*)\w*", t):
            return True
    return False


def candidates(rows, kec_map, min_workers=0, min_omset=0):
    out = []
    for x in rows:
        if x.get("deleted_at") not in (None, "None", ""):
            continue
        if str(x.get("tdu_suspend")) == "1" or str(x.get("tdu_approval")) not in ("1", "2"):
            continue
        name, desc = x.get("tdu_nama"), x.get("tdu_keterangan_produk")
        if junk(name, desc) or len(str(name).strip()) < 5 or len(str(desc).strip()) < 12:
            continue
        if not x.get("tdu_koordinat") or x["tdu_koordinat"] == "None":
            continue
        if len(str(x.get("tdu_alamat") or "").strip()) < 12:
            continue
        tk, om = num(x.get("tdu_jumlah_tenaga_kerja")), num(x.get("tdu_omset_perbulan"))
        if tk < min_workers and om < min_omset:
            continue
        out.append({
            "id": x.get("tdu_id"), "name": str(name).strip(),
            "kecamatan": kec_map.get(x.get("tdu_kec_kode"), x.get("tdu_kec_kode")),
            "alamat": x.get("tdu_alamat"), "produk": str(desc).strip(),
            "tenaga_kerja": tk, "omset_per_bulan": om,
            "koordinat": x.get("tdu_koordinat"), "nib": x.get("tdu_nib") or "",
        })
    return sorted_rows(out, "default")


def sorted_rows(rows, key="default"):
    if key == "workers":
        return sorted(rows, key=lambda r: (r["tenaga_kerja"], r["omset_per_bulan"]), reverse=True)
    if key == "omset":
        return sorted(rows, key=lambda r: (r["omset_per_bulan"], r["tenaga_kerja"]), reverse=True)
    if key == "name":
        return sorted(rows, key=lambda r: r["name"].lower())
    return sorted(rows, key=lambda r: (r["tenaga_kerja"], r["omset_per_bulan"]), reverse=True)


def grep(rows, pattern):
    rx = re.compile(pattern, re.I)
    return [r for r in rows
            if rx.search(f"{r['name']} {r['produk']} {r['alamat']} {r['kecamatan']}")]


def stats(rows, total_records):
    per = {}
    for r in rows:
        per[r["kecamatan"]] = per.get(r["kecamatan"], 0) + 1
    return {"records": total_records, "candidates": len(rows),
            "per_kecamatan": dict(sorted(per.items(), key=lambda t: -t[1]))}


def get(rows, needle):
    for r in rows:
        if str(r["id"]) == str(needle):
            return r
    sys.exit(f"tidak ada UMKM dengan id {needle} di hasil filter (coba --min-workers 0 --min-omset 0)")


def load():
    kec_map = {x["kode_kec"]: x["kecamatan"] for x in fetch("umkm_table_portal") if x.get("kode_kec")}
    return fetch("umkm_portal"), kec_map


def main(argv=None):
    ap = argparse.ArgumentParser(description="Direktori UMKM Kota Bogor (API publik SOLUSI)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="saring kandidat")
    s.add_argument("--grep", help="regex atas nama/produk/alamat/kecamatan")
    s.add_argument("--kecamatan", help="nama kecamatan persis")
    s.add_argument("--min-workers", type=int, default=3)
    s.add_argument("--min-omset", type=int, default=5_000_000)
    s.add_argument("--sort", choices=["default", "workers", "omset", "name"], default="default")
    s.add_argument("--limit", type=int, default=20)
    s.add_argument("--json", dest="json_out")
    s.add_argument("--quiet", action="store_true")



    a = ap.parse_args(argv)
    rows, kec_map = load()
    cands = candidates(rows, kec_map, a.min_workers, a.min_omset)

    if a.grep:
        cands = grep(cands, a.grep)
    if a.kecamatan:
        cands = [r for r in cands if r["kecamatan"].lower() == a.kecamatan.lower()]
    cands = sorted_rows(cands, a.sort)
    if a.json_out:
        json.dump(cands, open(a.json_out, "w"), ensure_ascii=False, indent=1)
    if not a.quiet:
        print(f"{len(cands)} kandidat")
        for r in cands[:a.limit]:
            print(f"- {r['name']} | {r['kecamatan']} | {r['tenaga_kerja']} pekerja | {r['produk'][:70]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
