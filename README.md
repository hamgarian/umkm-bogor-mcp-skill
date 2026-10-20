<p align="center"><img src="assets/logo.svg" width="96" alt=""></p>
<h1 align="center">umkm-bogor</h1>
<p align="center">Cari data UMKM Kota Bogor dari terminal, atau biarkan AI agent yang mencarikan.</p>

## Ini apa?

Pemerintah Kota Bogor punya daftar resmi 10.891 usaha kecil dan menengah di portal SOLUSI.
Daftarnya publik, tapi bentuknya tabel web yang panjang dan isinya campur: ada baris uji coba,
usaha yang sudah tutup, dan record tanpa alamat.

Repo ini isinya dua hal:

- **Satu perintah terminal** untuk mencari usaha di daftar itu berdasarkan produk, kecamatan, atau
  skala usaha, lalu mengekspornya ke JSON/CSV.
- **Server MCP** — protokol kecil yang membuat AI agent bisa memanggil tool — supaya Claude Code,
  Codex, Antigravity, Cursor, atau Hermes bisa mencari sendiri tanpa kamu ketik perintah.

Yang keluar: nama usaha, kecamatan, alamat, produk, jumlah tenaga kerja, omset per bulan, dan
koordinat. Yang tidak ada di data: nomor HP, IG, atau website — itu tetap dicari manual.

Cocok untuk: cari supplier, cari mitra UMKM untuk proyek kampus, riset pasar, atau cari kompetitor
di satu kecamatan.

![Demo: pasang MCP di Claude Code, lalu minta agent cari UMKM kopi](assets/demo.gif)

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

## Tool yang dipakai AI

Dipasang sebagai MCP, agent dapat tiga tool. Ini yang dipanggilnya saat kamu bertanya biasa.

### `search_umkm`

Cari usaha, balik `{count, rows}`.

| parameter | tipe | default | arti |
| --- | --- | --- | --- |
| `grep` | string | — | regex, dicocokkan ke nama, produk, alamat, kecamatan |
| `kecamatan` | string | — | nama kecamatan persis (`Bogor Barat`) |
| `min_workers` | integer | `3` | minimal tenaga kerja |
| `min_omset` | integer | `5000000` | minimal omset per bulan (rupiah) |
| `sort` | string | `default` | `default`, `workers`, `omset`, `name` |
| `limit` | integer | `20` | jumlah baris yang dikembalikan |

`min_workers` dan `min_omset` bersambung dengan OR: lolos kalau salah satu terpenuhi. Isi `0` untuk
mematikan salah satunya.

Contoh hasil nyata (`grep: "kopi"`, `min_workers: 5`, `limit: 1`):

```json
{
  "count": 10,
  "rows": [
    {
      "id": 11377,
      "name": "Mie Aceh Kurnia",
      "kecamatan": "Tanah Sareal",
      "alamat": "Yasmin Jl. KH. R. Abdullah Bin Nuh No.99",
      "produk": "Mie Aceh, Kopi Aceh, Martabak aceh, Nasi goreng Aceh, Roti Cane, Teh tarik",
      "tenaga_kerja": 7,
      "omset_per_bulan": 90000000,
      "koordinat": "1234567i",
      "nib": "2410230073774"
    }
  ]
}
```

Field yang selalu ada di tiap baris: `id`, `name`, `kecamatan`, `alamat`, `produk`, `tenaga_kerja`,
`omset_per_bulan`, `koordinat`, `nib`.

### `stats_umkm`

Ringkasan jumlah, dipakai untuk "ada berapa usaha di tiap kecamatan".

| parameter | tipe | default |
| --- | --- | --- |
| `min_workers` | integer | `3` |
| `min_omset` | integer | `5000000` |

```json
{
  "records": 10891,
  "candidates": 430,
  "per_kecamatan": {"Bogor Barat": 125, "Tanah Sareal": 78, "Bogor Utara": 74,
                    "Bogor Selatan": 62, "Bogor Tengah": 47, "Bogor Timur": 44},
  "min_workers": 3,
  "min_omset": 5000000
}
```

### `get_umkm`

Ambil satu record berdasarkan `id` (wajib, string). Contoh: `{"id": "11377"}`. Kalau id tidak ada di
data yang sudah difilter, balikannya error JSON-RPC `-32000`, bukan hasil kosong.

Protokol yang didukung: `initialize`, `tools/list`, `tools/call`, `notifications/initialized`,
`ping`. Tool tak dikenal dibalas `-32601`.

## Fitur skill

Tanpa MCP pun skill ini berguna: agent membaca `SKILL.md` lalu memakai CLI-nya sendiri.

- Pencarian regex ke empat field sekaligus (nama, produk, alamat, kecamatan), tanpa peduli huruf besar/kecil
- Filter kecamatan dan ambang skala (tenaga kerja / omset per bulan, OR; `0` mematikan ambang)
- Urutkan berdasarkan tenaga kerja, omset, atau nama
- Ekspor hasil ke JSON atau CSV untuk diolah di spreadsheet
- Cache 24 jam supaya pertanyaan berikutnya instan; `--refresh` memaksa data baru
- Rekap jumlah per kecamatan (`stats`) dan ambil satu record (`get --id`)
- Logika filter yang sama dipakai CLI dan MCP, jadi jawaban agent dan terminal tidak pernah beda
- `references/api.md` untuk field dan id kategori, `references/shortlist-method.md` untuk heuristik memilih mitra
- 18 test yang mengunci filter, cache, ambang nol, protokol MCP, dan pemindaian rahasia

## Coba dulu, 2 menit

Butuh Python 3.9+. Tidak ada paket tambahan.

```bash
git clone https://github.com/hamgarian/umkm-bogor-mcp-skill
cd umkm-bogor-mcp-skill

python3 scripts/umkm_bogor.py search --grep "kopi|kue" --limit 10
python3 scripts/umkm_bogor.py stats
```

Kalau dua perintah itu keluar hasilnya, semuanya sudah jalan.

## Pasang biar AI agent bisa pakai

Pilih satu sesuai alat yang kamu pakai. Ganti `/path/ke/` dengan lokasi folder hasil clone
(contoh `/home/ilham/umkm-bogor-mcp-skill`); cek dengan `pwd` di dalam folder.

### Claude Code

```bash
claude mcp add --scope user umkm-bogor -- python3 /path/ke/umkm-bogor-mcp-skill/scripts/mcp_server.py
claude mcp get umkm-bogor
```

Perintah kedua harus menampilkan `Status: ✔ Connected`. Lalu buka Claude Code dan minta:
"cari UMKM kopi di Bogor pakai tool umkm-bogor".

### Codex CLI

```bash
codex mcp add umkm-bogor -- python3 /path/ke/umkm-bogor-mcp-skill/scripts/mcp_server.py
codex mcp list
```

Nama `umkm-bogor` harus muncul dengan status `enabled`.

### Antigravity (IDE atau CLI)

Buka `~/.gemini/config/mcp_config.json` (global) atau `.agents/mcp_config.json` di folder proyek,
lalu tambahkan:

```json
{
  "mcpServers": {
    "umkm-bogor": {
      "command": "python3",
      "args": ["/path/ke/umkm-bogor-mcp-skill/scripts/mcp_server.py"]
    }
  }
}
```

Simpan, lalu reload Antigravity. Kalau file itu sebelumnya kosong, paste objek di atas utuh.

### Cursor

Isi yang sama, filenya `~/.cursor/mcp.json`.

### Client MCP lain

Format `mcpServers` di atas dipakai hampir semua client. Kalau client-mu minta `.mcp.json` di root
proyek, isi yang sama juga berlaku.

### Hermes

Salin foldernya jadi skill, lalu mulai sesi baru:

```bash
cp -r /path/ke/umkm-bogor-mcp-skill ~/.hermes/skills/research/umkm-bogor
```

Hermes membaca `SKILL.md` di dalamnya dan menjalankan CLI-nya sendiri. Untuk jalur MCP, jalankan
`hermes mcp add` lalu pilih server stdio.

### Pasang sebagai skill (bukan MCP)

Kalau alatmu mendukung skill tapi belum tentu MCP:

```bash
# Claude Code
mkdir -p ~/.claude/skills && cp -r /path/ke/umkm-bogor-mcp-skill ~/.claude/skills/umkm-bogor

# Antigravity
mkdir -p ~/.gemini/skills && cp -r /path/ke/umkm-bogor-mcp-skill ~/.gemini/skills/umkm-bogor
```

Bedanya: MCP memberi agent tiga tool terpisah; skill memberinya instruksi cara memakai CLI ini.

## Contoh pemakaian

**Cari supplier kue untuk kafe.** Minta ke agent: "pakai umkm-bogor, cari produsen kue di Bogor
Barat dengan minimal 5 pekerja, kasih 10 nama dan alamatnya." Agent memanggil:

```bash
python3 scripts/umkm_bogor.py search --grep "kue" --kecamatan "Bogor Barat" --min-workers 5 --limit 10
```

**Shortlist mitra proyek kampus.** Butuh usaha yang cukup besar untuk diajak bikin aplikasi:

```bash
python3 scripts/umkm_bogor.py search --grep "kopi|mochi|bakso|seragam" --min-workers 5 --sort workers --limit 15
```

**Lihat sebaran usaha per kecamatan** sebelum memilih lokasi survey:

```bash
python3 scripts/umkm_bogor.py stats
```

**Ekspor ke spreadsheet** untuk diolah sendiri:

```bash
python3 scripts/umkm_bogor.py search --grep "batik|kriya" --csv kerajinan.csv
```

## Cara kerja

1. Ambil dua endpoint publik dari `api-solusi.kotabogor.go.id`: `umkm_portal` (semua record) dan
   `umkm_table_portal` (peta kode kecamatan ke nama). Tanpa token, tanpa login.
2. Cache JSON 24 jam di `$UMKM_CACHE` (default `~/.cache/umkm-bogor`), jadi pertanyaan kedua instan.
   `--refresh` memaksa unduh ulang.
3. Buang record terhapus, suspended, belum disetujui, nama/deskripsi sampah (`tes12`, `asdadsads`),
   tanpa koordinat, atau tanpa alamat. Sisa 1.978 baris.
4. Terapkan ambang `--min-workers 3` atau `--min-omset 5000000` (omset per bulan, rupiah), semantik
   OR: lolos kalau salah satu terpenuhi. Nilai `0` mematikan ambang itu, bukan "semua lolos".

Rincian field dan id kategori: `references/api.md`. Heuristik memilih mitra: `references/shortlist-method.md`.

## Hasil

Diukur 2026-10-20 terhadap respons API hari itu:

- 10.891 record mentah → 1.978 lolos filter kualitas → 430 pada ambang default; 1.548 gugur karena
  tenaga kerja < 3 dan omset < 5 juta
- 53 kandidat untuk `kopi|kue`; 13 untuk `kopi|coffee`
- Run pertama 20–23 detik (payload 9.490.063 byte), berikutnya 0,27–0,35 detik dari cache
- 18 test lulus: filter, grep field produk, urutan/limit, cache, total stats, ambang nol, get,
  protokol MCP, dan pemindaian rahasia/path

## Batasan

- Hanya Kota Bogor. Kota lain punya portal sendiri dan tidak tercakup.
- Tanpa nomor HP, IG, atau website. Pencarian kontak tetap manual.
- Sebagian koordinat tidak valid (contoh `1234567i`); jangan dipakai langsung untuk peta tanpa cek.
- Tenaga kerja dan omset adalah laporan usaha ke pemkot (self-declared), bukan hasil audit.
- Angka berubah kalau pemkot memperbarui data; `stats` selalu menunjukkan total terbaru.

## Lisensi

MIT. Lihat `LICENSE`.

Demo GIF di README dibuat dengan
[remotion-product-motion](https://github.com/hamgarian/remotion-product-motion), lalu dikompres jadi
GIF 820×461 (12 fps, 868 KB) supaya tetap autoplay di GitHub.
