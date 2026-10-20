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

(53 = total yang cocok; `--limit 5` hanya memotong yang dicetak. Deskripsi produk dipotong di 70
karakter, jadi baris seperti `Teh t` memang terpotong oleh tool, bukan data rusak.)

## Kenapa

Direktori UMKM Kota Bogor tersedia di portal SOLUSI (solusi.kotabogor.go.id), halaman yang memuat
tabelnya lewat JavaScript. Isinya campur: baris uji coba, usaha suspended, record tanpa alamat atau
koordinat, dan sebagian besar tanpa id kategori.

CLI ini menarik satu endpoint publik dari portal itu, membuang baris yang tidak bisa dipakai, dan
menyisakan 430 dari 10.891 record pada ambang default. Yang tidak ada di dataset: nomor HP, IG,
website — kontak tetap dicari manual, lihat `references/shortlist-method.md`.

## Mulai cepat

Python 3.9+, tanpa paket tambahan.

```bash
git clone https://github.com/hamgarian/umkm-bogor-mcp-skill
cd umkm-bogor-mcp-skill

# --grep menerima regex, dicocokkan ke nama, produk, alamat, dan kecamatan
python3 scripts/umkm_bogor.py search --grep "kopi|kue" --limit 10
python3 scripts/umkm_bogor.py search --kecamatan "Bogor Utara" --min-workers 5

python3 scripts/umkm_bogor.py stats
python3 scripts/umkm_bogor.py get --id 12345
python3 scripts/umkm_bogor.py search --grep "batik" --json out.json
python3 scripts/umkm_bogor.py search --grep "batik" --csv out.csv

python3 -m unittest discover -s tests -v
```

Server MCP (stdio, JSON-RPC 2.0):

```bash
python3 scripts/mcp_server.py
```

Contoh pendaftaran di klien MCP:

```json
{
  "mcpServers": {
    "umkm-bogor": {
      "command": "python3",
      "args": ["/path/absolut/umkm-bogor/scripts/mcp_server.py"]
    }
  }
}
```

Tool: `search_umkm`, `stats_umkm`, `get_umkm`. Log keluar ke stderr supaya stdout tetap bersih.

## Cara kerja

1. Ambil `umkm_portal` dan `umkm_table_portal` (peta kode kecamatan ke nama) dari
   `api-solusi.kotabogor.go.id`. Endpoint ini publik, tanpa token.
2. Cache JSON 24 jam di `$UMKM_CACHE` (default `~/.cache/umkm-bogor`); `--refresh` memaksa unduh ulang.
3. Saring record terhapus, suspended, belum disetujui, nama/deskripsi sampah (`tes12`, `asdadsads`),
   tanpa koordinat, atau tanpa alamat. Ini yang menyisakan 1.978 baris.
4. Terapkan ambang: `--min-workers 3` atau `--min-omset 5000000` (omset per bulan, rupiah), semantik
   OR — lolos kalau salah satu terpenuhi. Nilai `0` berarti ambang itu tidak dipakai, bukan
   "semua lolos"; dengan `--min-workers 0 --min-omset 0` seluruh 1.978 baris ikut.

Rincian field dan id kategori ada di `references/api.md`.

## Hasil

Diukur 2026-10-20 terhadap respons API hari itu:

- 10.891 record mentah → 1.978 lolos filter kualitas → 430 dengan ambang default; 1.548 sisanya
  gugur karena tenaga kerja < 3 dan omset < 5 juta
- 53 kandidat untuk `kopi|kue`; 13 untuk `kopi|coffee`
- Run pertama 20–23 detik (payload 9.490.063 byte), run berikutnya 0,27–0,35 detik dari cache
- 18 test lulus: filter, grep field produk, urutan/limit, cache, total stats, ambang nol, get,
  protokol MCP, dan pemindaian rahasia/path

Batasan: hanya Kota Bogor. Angka tenaga kerja dan omset adalah laporan usaha ke pemkot
(self-declared), bukan hasil audit.

## Lisensi

MIT. Lihat `LICENSE`.
