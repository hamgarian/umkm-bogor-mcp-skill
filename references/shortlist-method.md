# Metode shortlist (terbukti 2026-10-20)

Tergantung tujuan, jadi tentukan profilnya dulu:

## A. Mitra capstone / digitalisasi (proyek mahasiswa)
Yang dicari: operasional nyata, identitas merek, belum punya website, bisa dihubungi lewat DM.
- `--min-workers 5` (atau omset >= 10jt) — volume cukup untuk butuh aplikasi
- kata kategori yang menyiratkan stok/pesanan: `kopi`, `kue`, `mochi`, `bakso`, `seragam`, `batik`, `kriya`
- cek celah digital: cari `"<nama>" instagram`; IG ada = bisa dihubungi, tanpa web/aplikasi = celahnya
- contoh terverifikasi (handle IG ditemukan, belum punya website sendiri):
  Circuloo Coffee & Cat `@circuloocafe` (Tanah Sareal, 16 pekerja),
  Ayam Goreng Fatmawati `@ayamgorengfatmawati` (Bogor Barat, 22),
  Mochibo `@mochibo_bogor` (Bogor Timur, 15),
  Bakso Kribo `@baksokriboo` (Bogor Tengah, 13),
  Mellz Indonesia `@mellzkonveksi_office` (Bogor Barat, 25)
- belum terverifikasi saat itu: Bloom With Kaia (Tanah Sareal, 15, tekstil/fashion) — IG tidak ditemukan

## B. Supplier / pengadaan
Yang dicari: NIB ada, teks produk spesifik, koordinat di kecamatan yang bisa dikunjungi.
- utamakan baris dengan `nib` terisi; `get --id` untuk memeriksa satu record
- cek `tdu_penghasilan_pertahun` untuk kapasitas

## C. Studi pasar / hitungan
Pakai `stats` untuk hitungan per kecamatan, `search --json` untuk kohort mentah, lalu agregasi lokal.
Jangan pernah menyajikan hitungan hasil filter sebagai total resmi — sebut "kandidat setelah filter".

## Aturan
- Laporkan skala sesuai laporan usaha ke pemkot (self-declared), bukan hasil audit.
- Tidak ada data kontak di dataset: cari handle manual dan kutip persis, atau bilang "tidak ditemukan".
- Pertanyaan DKI/kota lain di luar cakupan; dataset ini hanya Kota Bogor.
