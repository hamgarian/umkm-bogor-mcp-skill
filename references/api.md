# Referensi API — SOLUSI Kota Bogor

Base: `https://api-solusi.kotabogor.go.id/api`. Tanpa auth, tanpa key, tanpa header rate-limit
yang terlihat.

| path | isi | catatan |
| --- | --- | --- |
| `umkm_portal` | seluruh record UMKM (10.891 baris, 9,5 MB) | yang dipakai; satu respons, tanpa paging |
| `umkm_table_portal` | baris agregat per kecamatan | memberi nama `kode_kec` → `kecamatan`, plus hitungan per kategori |
| `total_umkm` | satu baris agregat | total tingkat kota |
| `umkm` | `{"success": false, "message": "Silahkan login terlebih dahulu!"}` | khusus login, jangan dipakai |
| `getVisitor`, `getRunningText` | elemen portal | tidak relevan |

Halaman portal `https://solusi.kotabogor.go.id/umkm/data-umkm` merender tabel di sisi klien
("Memuat..."); endpoint di atas adalah yang dipanggil JS-nya. Ditemukan dengan menangkap XHR
memakai patchright.

## Field record yang dipakai

- `tdu_id` — id record (yang diminta `get --id`)
- `tdu_nama` — nama usaha
- `tdu_keterangan_produk` — deskripsi produk; sinyal kategori paling andal
- `tdu_alamat`, `tdu_koordinat` (`"lat,long"`), `tdu_kec_kode`, `tdu_kel_kode`
- `tdu_jumlah_tenaga_kerja`, `tdu_omset_perbulan`, `tdu_penghasilan_pertahun` — skala, sering kosong
- `tdu_approval` — `2` terverifikasi, `1` disetujui, `0` menunggu (dibuang filter)
- `tdu_suspend` — `1` suspended (dibuang filter)
- `deleted_at` — tidak null berarti dihapus (dibuang filter)
- `tdu_nib`, `tdu_nomor_reg`, `tdu_tgl_mulai_usaha`, `tdu_image`, `tdu_produk` (gambar produk
  dipisah koma)

## Kualitas field (diukur 2026-10-20, 10.891 baris)

- 9.160 baris punya koordinat; 10.069 punya teks produk; 6.371 alamat unik
- 7.279 baris punya `tdu_tku_id = null` → id kategori tidak bisa dipakai untuk mayoritas baris
- Setelah filter: 1.978 baris lolos sanity dasar, 430 lolos default `>=3 tenaga kerja atau >=5jt omset`
- Tidak ada field telepon, email, website, atau media sosial — pengayaan selalu dari luar

## Id kategori (kalau ada)

`1` makanan, `2` pangan, `3` gas, `4` kendaraan, `5` kerajinan, `6` fashion, `7` kantin sekolah,
`9` kuliner, `11` otomotif, `12` pendidikan, `13` PKL, `14` teknologi/internet, `15` rumah warung makan,
`17` agrobisnis, `18` minuman, `19` jasa, `20` kesehatan, `21` warung sembako, `30`/`32` tanpa kategori.
Id disimpulkan dari mencocokkan hitungan dengan `umkm_table_portal`, jadi anggap petunjuk, bukan kebenaran.
