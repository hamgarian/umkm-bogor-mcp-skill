# SPEC — skill umkm-bogor

Tujuan: menjawab pertanyaan "cari/shortlist UMKM di Kota Bogor" dengan satu perintah, dari direktori
resmi SOLUSI, tanpa menulis scraper baru atau mengunduh 20 MB tiap pertanyaan.

## Input
- regex teks bebas atas nama / produk / alamat / kecamatan
- filter opsional: kecamatan, minimal tenaga kerja, minimal omset, urutan, limit
- path ekspor opsional (json/csv)

## Output
- baris: id, nama, kecamatan, alamat, produk, tenaga_kerja, omset_per_bulan, koordinat, nib
- stats: jumlah record, jumlah kandidat, rekap per kecamatan
- satu record berdasarkan id
- server MCP stdio opsional yang menyediakan search/stats/get sebagai tool

## Checklist penerimaan (tiap baris harus dibuktikan test yang benar-benar dijalankan)
1. Baris sampah dibuang: nama seperti "tes12"/"asdadsads", record suspended, record belum disetujui,
   baris tanpa teks produk, tanpa alamat, atau tanpa koordinat tidak pernah muncul di hasil.
2. `--grep` mencocokkan tanpa peduli huruf besar/kecil di nama, produk, alamat, dan kecamatan.
3. `--min-workers` / `--min-omset` menyaring dengan semantik OR (baris lolos kalau salah satu terpenuhi).
4. `--sort` dan `--limit` bekerja (urutan default: tenaga kerja desc, lalu omset desc).
5. Panggilan kedua dalam jendela cache tidak melakukan HTTP sama sekali; `--refresh` memaksa satu unduhan.
6. `stats` melaporkan total record, jumlah kandidat, dan rekap per kecamatan yang totalnya sama
   dengan jumlah kandidat.
7. `get --id` mengembalikan tepat record yang diminta, atau keluar dengan status non-nol dan pesan
   kalau tidak ada.
8. Server MCP: `initialize`, `tools/list` (search/stats/get), dan `tools/call search` mengembalikan
   JSON-RPC valid beserta baris yang sudah diparse.
9. Tidak ada kredensial, data kontak pribadi, atau path pengguna yang di-hardcode (direktori cache
   berasal dari `$UMKM_CACHE`).
10. Uji langsung ke API asli mengembalikan lebih dari 100 kandidat.

## Non-tujuan
- Tidak memakai endpoint khusus login (`/api/umkm` butuh auth).
- Tidak mengambil nomor HP/IG: pengayaan adalah langkah manual terdokumentasi (mesin pencari),
  bukan bagian otomatisasi ini.
