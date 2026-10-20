# Changelog

## 1.0.0 — 2026-10-20
- Rilis awal: CLI (search/stats/get) di atas API publik UMKM SOLUSI Kota Bogor.
- Filter membuang baris uji, record suspended/belum disetujui, baris tanpa teks produk, alamat,
  atau koordinat.
- Cache JSON 24 jam; `--refresh` memaksa unduh ulang.
- Server MCP stdio menyediakan search_umkm, stats_umkm, get_umkm.
- 18 kasus unittest mencakup filter, grep field produk, urutan/limit, cache, total stats, semantik
  ambang nol, get, protokol MCP, dan pemindaian rahasia/path.
- Pencarian MCP mematuhi `min_workers`/`min_omset`; stats MCP melaporkan total record yang sebenarnya.
- `stats` menerima flag ambang dan mencetaknya; direktori cache bisa diatur lewat `UMKM_CACHE`.
