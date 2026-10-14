---
name: umkm-bogor
description: "Cari dan shortlist UMKM Kota Bogor dari data resmi."
version: 1.0.0
author: Ilham
license: MIT
metadata:
  hermes:
    tags: [UMKM, Bogor, Scraping, MCP, Capstone]
---

# umkm-bogor

Telusuri direktori UMKM resmi Kota Bogor (SOLUSI, Dinas KUKMDagin) lalu ubah jadi shortlist usaha
nyata yang bisa dihubungi — daftar yang dibutuhkan tim capstone, pencarian mitra, atau studi pasar.

## Kapan dipakai

- "cari UMKM di Bogor", "shortlist UMKM buat capstone", "UMKM kuliner/fashion/kriya Bogor"
- butuh nama + kecamatan + skala (tenaga kerja, omset) + koordinat usaha lokal
- butuh ekspor dataset UMKM Bogor yang sudah difilter (JSON/CSV)
- klien MCP mau pencarian UMKM sebagai tool

Bukan untuk: nomor HP atau akun IG (tidak ada di dataset publik — pengayaan manual, lihat
`references/shortlist-method.md`), atau kota lain (endpoint hanya Kota Bogor).

## Mulai cepat

```bash
# 13 kandidat terkait kopi, urut tenaga kerja
python3 scripts/umkm_bogor.py search --grep "kopi|coffee" --limit 10

# fashion/kriya di satu kecamatan, sekalian ekspor
python3 scripts/umkm_bogor.py search --kecamatan "Bogor Utara" --grep "batik|kriya" --json out.json

# berapa usaha nyata per wilayah
python3 scripts/umkm_bogor.py stats

# satu record
python3 scripts/umkm_bogor.py get --id 12345
```

Default: `--min-workers 3`, `--min-omset 5000000` (semantik OR; nilai `0` berarti "tidak diset",
jadi `--min-omset 0 --min-workers 20` hanya menyaring tenaga kerja). Run pertama mengunduh 9,5 MB
sekitar 22 detik; run berikutnya pakai cache 24 jam sekitar 0,3 detik. `--refresh` memaksa unduh ulang.

## Metode

1. Tanya dulu daftarnya untuk apa (mitra capstone, supplier, studi pasar) dan kategori/kecamatan apa.
2. `search` dengan `--grep` kata kategori berbahasa Indonesia (`kopi`, `kue`, `batik`, `anyaman`, `sepatu`).
3. Untuk mitra yang operasionalnya nyata, utamakan baris dengan `tenaga_kerja >= 5` atau omset terlihat;
   kalau tujuannya bantuan digitalisasi, usaha mikro juga layak diambil.
4. Cukup 10 teratas yang diperkaya: web search `"<nama>" instagram` untuk cari handle, lalu DM/kunjungi.
5. Laporkan nama, kecamatan, produk, skala, dan apakah sudah punya IG/web — celah itulah bahan pitch.
   Jangan pernah mengarang kontak.

## Server MCP

`scripts/mcp_server.py` bicara JSON-RPC 2.0 lewat stdio (satu JSON per baris) dan menyediakan
`search_umkm`, `stats_umkm`, `get_umkm`. Daftarkan di klien MCP sebagai
`python3 /path/absolut/scripts/mcp_server.py`; log ke stderr, jadi stdout tetap bersih untuk protokol.

## Jebakan

- `/api/umkm` wajib login; yang publik `/api/umkm_portal` (semua baris, tanpa paging).
- Sekitar 7,3 ribu dari 10,9 ribu baris tidak punya id kategori — filter lewat teks
  `tdu_keterangan_produk`, bukan kategori.
- Ada baris sampah (`tes12`, `asdadsads`, `warung sembako`), record suspended dan belum disetujui,
  serta baris tanpa koordinat. Filter sudah membuangnya; jangan dilewati.
- Jumlah kategori di `umkm_table_portal` adalah agregat per kecamatan; jangan dijumlahkan untuk
  mencari nama usaha.

## Verifikasi

```bash
python3 -m unittest discover -s tests -v     # 18 test
```

Cek langsung: `python3 scripts/umkm_bogor.py stats` harus mencetak `records: 10891` (atau lebih baru)
dan jumlah kandidat di atas 100.

Lihat `references/api.md` untuk endpoint/field dan `references/shortlist-method.md` untuk heuristik seleksi.
