<p align="center"><img src="assets/logo.svg" width="96" alt=""></p>
<h1 align="center">umkm-bogor</h1>
<p align="center">Direktori UMKM Kota Bogor sebagai CLI dan server MCP.</p>

![Pencarian UMKM kopi dan kue lewat CLI](assets/social-preview.png)

```console
$ python3 scripts/umkm_bogor.py search --grep "kopi|kue" --limit 5
53 kandidat
- Dapoer Ibu Hasim | Bogor Barat | 8 pekerja | Makanan dan Kue Kue
- Mie Aceh Kurnia | Tanah Sareal | 7 pekerja | Mie Aceh, Kopi Aceh, Martabak aceh, Nasi goreng Aceh, Roti Cane, Teh t
- Sagala Bolu | Bogor Barat | 7 pekerja | Produksi dan penjualan Kue caramel, bolen pisang, pie mede, bolu susu,
- Butterfun | Bogor Barat | 6 pekerja | Butterfun merupakan perusahaan home industri yang bergerak dalam bidan
- Flash Burger | Bogor Timur | 6 pekerja | Restoran yang menyediakan makanan dan minuman yang berbasis burger dan
```

## Kenapa

Data UMKM Kota Bogor ada di portal SOLUSI, tapi tabelnya dirender di browser dan isinya campur:
baris uji coba, usaha suspended, record tanpa alamat atau koordinat. Mencari "UMKM kopi di Bogor"
secara manual berarti menggulir 10.891 baris tiap kali.

Repo ini menarik satu endpoint publik, membuang baris yang tidak bisa dipakai, dan menyisakan
usaha yang bisa benar-benar dihubungi: 430 kandidat dari 10.891 record pada ambang default.

## Mulai cepat

Tidak ada dependensi di luar Python 3.9+.

```bash
git clone https://github.com/hamgarian/umkm-bogor-mcp-skill
cd umkm-bogor-mcp-skill

# cari berdasarkan kata produk, kecamatan, atau skala
python3 scripts/umkm_bogor.py search --grep "kopi|kue" --limit 10
python3 scripts/umkm_bogor.py search --kecamatan "Bogor Utara" --min-workers 5

# rekap per kecamatan
python3 scripts/umkm_bogor.py stats

# satu record, plus ekspor
python3 scripts/umkm_bogor.py get --id 12345
python3 scripts/umkm_bogor.py search --grep "batik" --json out.json
python3 scripts/umkm_bogor.py search --grep "batik" --csv out.csv

# test
python3 -m unittest discover -s tests -v
```

Server MCP (stdio, JSON-RPC 2.0):

```bash
python3 scripts/mcp_server.py
```

Daftarkan path absolut skrip itu di klien MCP. Tool yang tersedia: `search_umkm`, `stats_umkm`,
`get_umkm`. Log ditulis ke stderr, jadi stdout tetap bersih untuk protokol.

## Cara kerja

1. Ambil `umkm_portal` (10.891 baris, 9,5 MB) dan `umkm_table_portal` (nama kecamatan) dari
   `api-solusi.kotabogor.go.id`. Tanpa auth.
2. Simpan ke cache JSON 24 jam di `$UMKM_CACHE` (default `~/.cache/umkm-bogor`). `--refresh`
   memaksa unduh ulang.
3. Saring: buang record terhapus, suspended, belum disetujui, nama/deskripsi sampah
   (`tes12`, `asdadsads`), tanpa koordinat, atau tanpa alamat.
4. `--min-workers` / `--min-omset` memakai semantik OR: lolos kalau salah satu terpenuhi.
   Nilai `0` berarti "tidak diset", bukan "terima semua".

Field, id kategori, dan kualitas data dibahas di `references/api.md`; heuristik pemilihan mitra di
`references/shortlist-method.md`.

## Hasil

Diukur 2026-10-20 pada data yang sama:

- 10.891 record mentah, 1.978 lolos sanity dasar, 430 kandidat pada ambang default
  (`>= 3 tenaga kerja` atau `>= 5 juta omset`)
- 53 kandidat untuk `kopi|kue`, 13 untuk `kopi|coffee`
- Run pertama 20–23 detik (unduh 9.490.063 byte), run berikutnya 0,27–0,35 detik dari cache
- 18 test lulus: filter, grep field produk, urutan/limit, cache, total stats, ambang nol, get,
  protokol MCP, dan pemindaian rahasia/path

Batasan: hanya Kota Bogor; tidak ada nomor HP, IG, atau website di dataset, jadi pengayaan kontak
tetap manual. Skala usaha adalah laporan self-declared ke pemkot, bukan hasil audit.

## Lisensi

MIT. Lihat `LICENSE`.
