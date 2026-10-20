<div align="center">

<img src="assets/logo.svg" width="96" alt="Logo umkm-bogor">

# umkm-bogor

### Cari UMKM Kota Bogor lewat AI agent, dari data resmi pemkot.

**Tanya pakai bahasa biasa. Agent yang mencarikan di 10.891 data UMKM SOLUSI Kota Bogor.**

[![Lisensi MIT](https://img.shields.io/badge/lisensi-MIT-f4c430?style=flat-square)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776ab?style=flat-square&logo=python&logoColor=white)](#coba-dulu-tanpa-agent)
[![MCP stdio: 3 tool](https://img.shields.io/badge/MCP-3_tool-5c4ee5?style=flat-square)](#tool-yang-dipakai-agent)
[![Rilis v1.0.0](https://img.shields.io/badge/rilis-v1.0.0-2ea44f?style=flat-square)](CHANGELOG.md)

[Pasang](#pasang-di-antigravity) · [Contoh pakai](#contoh-pakai) · [Tool](#tool-yang-dipakai-agent) · [Kemampuan](#kemampuan) · [FAQ & batasan](#faq) · [Referensi](#referensi)

</div>

---

Pemerintah Kota Bogor punya daftar resmi UMKM di portal SOLUSI. Daftarnya publik, tapi bentuknya
tabel web panjang dan isinya campur: ada baris uji coba, usaha yang sudah tutup, dan data tanpa
alamat.

Repo ini membersihkan daftar itu dan memberikannya ke AI agent kamu. Kamu cukup bertanya, misalnya
"cari produsen kue di Bogor Barat", dan agent mengembalikan nama usaha, kecamatan, alamat, produk,
jumlah tenaga kerja, omset per bulan, dan koordinat. Bisa juga dipakai langsung dari terminal.

Isinya dua bagian yang bisa dipasang sendiri-sendiri:

- **Skill**: instruksi (`SKILL.md`) yang mengajari agent cara memakai CLI di repo ini.
- **Server MCP**: MCP adalah cara standar agar AI agent bisa memanggil tool. Server ini memberi
  agent tiga tool: cari, rekap, dan ambil satu data.

Tidak perlu akun, token, atau paket tambahan. Cukup Python 3.9+.

<div align="center">

<img src="assets/demo.gif" width="820" alt="Ilustrasi alur kerja di Antigravity: skill umkm-bogor aktif, agent memanggil search_umkm untuk UMKM kopi dan menampilkan 2 hasil">

<sub>Ilustrasi alur kerja di Antigravity, bukan rekaman layar. Argumen <code>search_umkm</code>
(<code>grep: "kopi"</code>, <code>min_workers: 5</code>, <code>min_omset: 0</code>, <code>limit: 5</code>)
dan dua baris hasilnya diambil dari keluaran asli <code>scripts/mcp_server.py</code> pada cache data
2026-10-20. Hasilmu bisa beda kalau pemkot sudah memperbarui data.</sub>

</div>

## Pasang di Antigravity

Antigravity adalah jalur utama. Pilih salah satu atau pasang keduanya.

**1. Ambil kodenya**, lalu catat lokasi foldernya:

```bash
git clone https://github.com/hamgarian/umkm-bogor-mcp-skill
cd umkm-bogor-mcp-skill
pwd
```

Hasil `pwd` adalah path absolut yang dipakai di langkah berikutnya. Di contoh di bawah, ganti
`/path/ke/umkm-bogor-mcp-skill` dengan hasil itu.

**2a. Pasang sebagai MCP (disarankan).** Buka file konfigurasi MCP Antigravity:
melalui menu pengelolaan MCP Antigravity, lalu pilih **View raw config**. Lokasi file bisa berbeda
menurut versi; edit file yang dibuka aplikasi. Tambahkan entri `umkm-bogor` ke dalam `mcpServers`:

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

> [!WARNING]
> **Jangan menimpa konfigurasi yang sudah ada.** Kalau file itu sudah berisi server MCP lain,
> jangan paste seluruh blok di atas. Cukup sisipkan bagian `"umkm-bogor": { ... }` ke dalam
> `mcpServers` yang sudah ada, dengan koma di antara entri. Salin dulu file lamanya sebagai
> cadangan. Blok di atas boleh di-paste utuh hanya kalau file itu kosong atau belum ada.

Simpan, lalu reload Antigravity. Untuk mengecek, minta agent: "pakai tool umkm-bogor, ada berapa
UMKM per kecamatan?" Agent seharusnya memanggil `stats_umkm`.

**2b. Pasang sebagai skill.** Agent membaca `SKILL.md` lalu menjalankan CLI sendiri:

```bash
mkdir -p ~/.gemini/skills
cp -r /path/ke/umkm-bogor-mcp-skill ~/.gemini/skills/umkm-bogor
```

Kalau di sana sudah ada folder `umkm-bogor`, periksa atau hapus dulu folder lama itu. `cp -r` ke
folder yang sudah ada akan membuat folder bertumpuk, bukan menggantinya.

Bedanya: MCP memberi agent tiga tool siap pakai, sedangkan skill memberi agent instruksi cara
memakai CLI. Keduanya membaca data dan filter yang sama.

<details>
<summary><strong>Claude Code</strong></summary>

```bash
claude mcp add --scope user umkm-bogor -- python3 /path/ke/umkm-bogor-mcp-skill/scripts/mcp_server.py
claude mcp get umkm-bogor
```

Perintah kedua harus menampilkan `Status: ✔ Connected`. Sebagai skill:

```bash
mkdir -p ~/.claude/skills && cp -r /path/ke/umkm-bogor-mcp-skill ~/.claude/skills/umkm-bogor
```

</details>

<details>
<summary><strong>Codex CLI</strong></summary>

```bash
codex mcp add umkm-bogor -- python3 /path/ke/umkm-bogor-mcp-skill/scripts/mcp_server.py
codex mcp list
```

Nama `umkm-bogor` harus muncul dengan status `enabled`.

</details>

<details>
<summary><strong>Cursor, Hermes, dan client MCP lain</strong></summary>

- **Cursor:** isi JSON yang sama seperti di Antigravity, di `~/.cursor/mcp.json`. Peringatan soal
  menggabungkan konfigurasi yang sudah ada juga berlaku.
- **Client lain:** hampir semua client memakai format `mcpServers` yang sama, termasuk `.mcp.json`
  di root proyek.
- **Hermes:** salin folder ke `~/.hermes/skills/research/umkm-bogor`, lalu mulai sesi baru. Untuk
  jalur MCP, jalankan `hermes mcp add` lalu pilih server stdio.

</details>

### Coba dulu tanpa agent

```bash
python3 scripts/umkm_bogor.py search --grep "kopi|kue" --limit 5
python3 scripts/umkm_bogor.py stats
```

Run pertama mengunduh sekitar 9,5 MB, jadi butuh kira-kira 20 detik. Berikutnya, data dibaca dari
cache dalam waktu kurang dari 1 detik. Kalau dua perintah itu menampilkan hasil, berarti semuanya
sudah jalan.

## Contoh pakai

Tulis permintaan ke agent dengan bahasa biasa. Di bawah tiap contoh ada pemanggilan yang setara,
supaya kamu bisa mengecek hasilnya sendiri.

> [!NOTE]
> Tenaga kerja dan omset dibatasi dengan **OR**: sebuah usaha lolos kalau *salah satu* ambang
> terpenuhi. Default-nya 3 tenaga kerja **atau** omset 5 juta per bulan. Jadi, kalau kamu benar-benar
> hanya mau "minimal 5 pekerja", omset harus dimatikan dengan `0`.

**Cari supplier: kue untuk kafe.**

> "Pakai umkm-bogor, cari produsen kue di Bogor Barat yang punya minimal 5 pekerja. Kasih nama dan
> alamatnya."

```bash
python3 scripts/umkm_bogor.py search --grep "kue" --kecamatan "Bogor Barat" --min-workers 5 --min-omset 0
```

Pada cache 2026-10-20 hasilnya 3 kandidat. Tanpa `--min-omset 0`, hasilnya 13, karena usaha dengan
kurang dari 5 pekerja tapi omset ≥ 5 juta ikut lolos.

**Cari mitra proyek kampus: UMKM yang cukup besar untuk diajak bikin aplikasi.**

> "Cari UMKM kopi, mochi, bakso, atau seragam dengan minimal 5 pekerja, urutkan dari yang paling
> besar."

```bash
python3 scripts/umkm_bogor.py search --grep "kopi|mochi|bakso|seragam" --min-workers 5 --min-omset 0 --sort workers --limit 15
```

Setelah itu, agent bisa mencari akun IG tiap usaha lewat web search. Dataset ini tidak berisi kontak
(lihat [`references/shortlist-method.md`](references/shortlist-method.md)).

**Studi data: sebaran usaha per kecamatan, lalu ekspor ke spreadsheet.**

> "Ada berapa UMKM per kecamatan? Lalu ekspor semua usaha batik dan kriya ke CSV."

```bash
python3 scripts/umkm_bogor.py stats
python3 scripts/umkm_bogor.py search --grep "batik|kriya" --csv kerajinan.csv
```

Angkanya berarti "kandidat setelah filter", bukan total resmi pemkot. Omset adalah angka yang
dilaporkan sendiri oleh pelaku usaha, bukan data transaksi atau penjualan.

## Tool yang dipakai agent

Kalau dipasang sebagai MCP, agent mendapat tiga tool:

| Tool | Gunanya | Parameter |
| --- | --- | --- |
| `search_umkm` | Mencari usaha. Mengembalikan `{count, rows}` | `grep` (regex), `kecamatan`, `min_workers` (3), `min_omset` (5000000), `sort`, `limit` (20) |
| `stats_umkm` | Menghitung jumlah usaha per kecamatan | `min_workers` (3), `min_omset` (5000000) |
| `get_umkm` | Mengambil satu data berdasarkan id | `id` (wajib) |

Tiap baris hasil berisi `id`, `name`, `kecamatan`, `alamat`, `produk`, `tenaga_kerja`,
`omset_per_bulan`, `koordinat`, dan `nib`. Skema lengkap ada di `TOOLS` pada
[`scripts/mcp_server.py`](scripts/mcp_server.py), dan arti tiap field ada di
[`references/api.md`](references/api.md).

## Kemampuan

- **Satu pencarian untuk empat kolom:** nama, produk, alamat, dan kecamatan, tanpa membedakan huruf
  besar atau kecil.
- **Filter kecamatan dan skala usaha:** tenaga kerja atau omset, digabung dengan OR. Nilai `0`
  mematikan ambang itu.
- **Data dibersihkan dulu:** data uji coba, yang dihapus, yang di-suspend, yang belum disetujui,
  yang tanpa alamat, dan yang tanpa koordinat dibuang. Dari 10.891 data mentah, tersisa 1.978.
  Dengan ambang default, tersisa 430.
- **Hasil bisa diurutkan** (tenaga kerja, omset, nama) **dan diekspor** ke JSON atau CSV.
- **Cache 24 jam** di `~/.cache/umkm-bogor` (bisa diubah lewat `UMKM_CACHE`). `--refresh` memaksa
  unduh ulang.
- **CLI dan MCP memakai logika filter yang sama.** Dengan parameter dan cache yang sama, jawaban agent
  dan terminal akan sama. Default `limit` keduanya 20, tapi CLI selalu mencetak jumlah total kandidat.

## FAQ

<details>
<summary><strong>Apakah GIF demo itu rekaman asli?</strong></summary>

Bukan. GIF itu ilustrasi alur kerja di Antigravity, bukan rekaman layar. Argumen tool dan dua baris
hasilnya memang keluaran asli server MCP pada cache data 2026-10-20, tapi tampilan antarmukanya
dibuat ulang.

</details>

<details>
<summary><strong>Seberapa baru datanya?</strong></summary>

Data diunduh dari API publik SOLUSI lalu disimpan selama 24 jam. Jadi hasil bisa tertinggal sampai
24 jam dari portal. Pakai `--refresh` di CLI untuk mengunduh ulang. Server MCP memuat data sekali saat
start, jadi restart server (reload agent) supaya ikut membaca data baru.

</details>

<details>
<summary><strong>Ada nomor HP, IG, atau website?</strong></summary>

Tidak ada. Dataset publiknya memang tidak berisi kontak. Kontak harus dicari manual. Agent tidak
boleh mengarang kontak; kalau tidak ketemu, jawabannya "tidak ditemukan".

</details>

<details>
<summary><strong>Bisa langsung dipetakan pakai koordinat?</strong></summary>

Jangan langsung. Sebagian koordinat tidak valid, misalnya `1234567i` atau `12345678`, padahal format
yang benar adalah `"lat,long"`. Cek dulu sebelum dipakai untuk peta.

</details>

<details>
<summary><strong>Apakah angka tenaga kerja dan omset bisa dipercaya?</strong></summary>

Angka itu dilaporkan sendiri oleh pelaku usaha ke pemkot, bukan hasil audit dan bukan data transaksi.
Pakai sebagai petunjuk skala, bukan fakta keuangan.

</details>

<details>
<summary><strong>Kota lain bisa?</strong></summary>

Tidak. Cakupannya hanya Kota Bogor (bukan Kabupaten Bogor). Kota lain punya portal sendiri.

</details>

<details>
<summary><strong>Kenapa hasil "minimal 5 pekerja" saya masih memuat usaha 3 pekerja?</strong></summary>

Karena ambang omset default (5 juta) masih aktif, dan kedua ambang digabung dengan OR. Tambahkan
`--min-omset 0` (CLI) atau `"min_omset": 0` (MCP).

</details>

<details>
<summary><strong>Data saya dikirim ke mana?</strong></summary>

Tool hanya mengunduh dari `api-solusi.kotabogor.go.id` dan menyimpan cache di komputermu. Hasil tool
dibaca oleh agent, dan penyedia model agent punya kebijakan datanya sendiri.

</details>

## Referensi

- [`SKILL.md`](SKILL.md): instruksi untuk agent, perintah cepat, dan jebakan data
- [`references/api.md`](references/api.md): endpoint, field, kualitas data, dan id kategori
- [`references/shortlist-method.md`](references/shortlist-method.md): cara memilih mitra, supplier, atau studi pasar
- [`scripts/mcp_server.py`](scripts/mcp_server.py): server MCP dan skema tool
- [`CHANGELOG.md`](CHANGELOG.md): riwayat rilis
- Test: `python3 -m unittest discover -s tests -v`

## Lisensi

[MIT](LICENSE). Data milik Pemerintah Kota Bogor (portal SOLUSI). GIF demo dibuat dengan
[remotion-product-motion](https://github.com/hamgarian/remotion-product-motion).
