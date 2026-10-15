"""Tests for umkm_bogor CLI + MCP server. Run: python3 -m unittest discover -s tests -v"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import umkm_bogor as U  # noqa: E402
import mcp_server as M  # noqa: E402

KEC = {"32.71.01": "Bogor Selatan", "32.71.02": "Bogor Timur"}


def row(**kw):
    base = {
        "tdu_id": 1, "tdu_nama": "Kopi Nusantara", "tdu_keterangan_produk": "Kopi robusta lokal",
        "tdu_alamat": "Jl. Pajajaran No. 10, Bogor", "tdu_kec_kode": "32.71.01",
        "tdu_koordinat": "-6.56,106.79", "tdu_jumlah_tenaga_kerja": "5", "tdu_omset_perbulan": "10000000",
        "tdu_approval": "2", "tdu_suspend": "0", "deleted_at": None, "tdu_nib": "123",
    }
    base.update(kw)
    return base


ROWS = [
    row(),
    row(tdu_id=2, tdu_nama="tes12", tdu_keterangan_produk="test"),
    row(tdu_id=3, tdu_nama="asdadsads", tdu_keterangan_produk="asdasdadasdsad"),
    row(tdu_id=4, tdu_nama="Batik Sari", tdu_keterangan_produk="Batik tulis tangan",
        tdu_alamat="Jl. Siliwangi No. 22, Bogor", tdu_kec_kode="32.71.02",
        tdu_jumlah_tenaga_kerja="3", tdu_omset_perbulan=None),
    row(tdu_id=5, tdu_nama="Warung Suspend", tdu_keterangan_produk="Makanan ringan enak", tdu_suspend="1"),
    row(tdu_id=6, tdu_nama="Tanpa Koordinat", tdu_keterangan_produk="Kerajinan anyaman bambu",
        tdu_koordinat=None),
    row(tdu_id=7, tdu_nama="Belum Approve", tdu_keterangan_produk="Kue basah tradisional", tdu_approval="0"),
    row(tdu_id=8, tdu_nama="Roti Enak", tdu_keterangan_produk="Roti manis aneka rasa",
        tdu_alamat="Jl. Baru 5, Bogor", tdu_jumlah_tenaga_kerja="1", tdu_omset_perbulan="20000000",
        tdu_kec_kode="32.71.02"),
]


class FilterTests(unittest.TestCase):
    def test_junk_and_invalid_rows_dropped(self):
        names = [r["name"] for r in U.candidates(ROWS, KEC, 0, 0)]
        self.assertNotIn("tes12", names)
        self.assertNotIn("asdadsads", names)
        self.assertNotIn("Warung Suspend", names)
        self.assertNotIn("Tanpa Koordinat", names)
        self.assertNotIn("Belum Approve", names)
        self.assertIn("Kopi Nusantara", names)

    def test_grep_case_insensitive_across_fields(self):
        cands = U.candidates(ROWS, KEC, 0, 0)
        self.assertEqual([r["name"] for r in U.grep(cands, "BATIK")], ["Batik Sari"])
        self.assertEqual([r["name"] for r in U.grep(cands, "pajajaran")], ["Kopi Nusantara"])
        self.assertEqual([r["name"] for r in U.grep(cands, "bogor timur")], ["Batik Sari", "Roti Enak"])

    def test_thresholds_are_or(self):
        cands = U.candidates(ROWS, KEC, 3, 5_000_000)
        names = {r["name"] for r in cands}
        self.assertIn("Kopi Nusantara", names)   # both
        self.assertIn("Batik Sari", names)       # workers only
        self.assertIn("Roti Enak", names)        # omset only
        strict = {r["name"] for r in U.candidates(ROWS, KEC, 9, 99_000_000)}
        self.assertEqual(strict, set())

    def test_sort_and_limit(self):
        cands = U.candidates(ROWS, KEC, 0, 0)
        self.assertEqual(cands[0]["name"], "Kopi Nusantara")      # default: workers desc
        self.assertEqual(U.sorted_rows(cands, "omset")[0]["name"], "Roti Enak")
        by_workers = U.sorted_rows(cands, "workers")
        self.assertEqual(by_workers[0]["tenaga_kerja"], 5)
        self.assertEqual(len(by_workers[:2]), 2)


if __name__ == "__main__":
    unittest.main()
