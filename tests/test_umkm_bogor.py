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


class CacheTests(unittest.TestCase):
    def test_cache_prevents_second_fetch_and_refresh_forces_one(self):
        calls = {"n": 0}
        payload = [{"kode_kec": "32.71.01", "kecamatan": "Bogor Selatan"}]

        class FakeUrl:
            def __init__(self, data): self.data = data
            def read(self): return json.dumps(self.data).encode()

        def fake_open(url, timeout=0):
            calls["n"] += 1
            return FakeUrl(payload)

        orig = U.urllib.request.urlopen
        U.urllib.request.urlopen = fake_open
        try:
            with tempfile.TemporaryDirectory() as d:
                cache = os.path.join(d, "rows.json")
                U.fetch("x", cache, 24)
                U.fetch("x", cache, 24)
                self.assertEqual(calls["n"], 1)
                U.fetch("x", cache, 0)
                self.assertEqual(calls["n"], 2)
        finally:
            U.urllib.request.urlopen = orig


class StatsAndGetTests(unittest.TestCase):
    def test_stats_counts_sum_to_candidates(self):
        cands = U.candidates(ROWS, KEC, 0, 0)
        stats = U.stats(cands, len(ROWS))
        self.assertEqual(stats["records"], len(ROWS))
        self.assertEqual(stats["candidates"], len(cands))
        self.assertEqual(sum(stats["per_kecamatan"].values()), len(cands))

    def test_get_by_id(self):
        cands = U.candidates(ROWS, KEC, 0, 0)
        self.assertEqual(U.get(cands, "1")["name"], "Kopi Nusantara")
        with self.assertRaises(SystemExit) as ctx:
            U.get(cands, "999")
        self.assertNotEqual(ctx.exception.code, 0)


class McpTests(unittest.TestCase):
    def setUp(self):
        self.rows = U.candidates(ROWS, KEC, 0, 0)

    def test_initialize_and_tools_list(self):
        init = M.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}, self.rows)
        self.assertEqual(init["result"]["serverInfo"]["name"], "umkm-bogor")
        listed = M.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, self.rows)
        names = {t["name"] for t in listed["result"]["tools"]}
        self.assertEqual(names, {"search_umkm", "stats_umkm", "get_umkm"})

    def test_tools_call_search(self):
        res = M.handle({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                        "params": {"name": "search_umkm", "arguments": {"grep": "batik"}}}, self.rows)
        payload = json.loads(res["result"]["content"][0]["text"])
        self.assertEqual([r["name"] for r in payload["rows"]], ["Batik Sari"])

    def test_unknown_tool_is_jsonrpc_error(self):
        res = M.handle({"jsonrpc": "2.0", "id": 4, "method": "tools/call",
                        "params": {"name": "nope", "arguments": {}}}, self.rows)
        self.assertIn("error", res)


class CoverageGapTests(unittest.TestCase):
    """Cases the first review flagged as untested (SPEC items 1, 4, 5, 10)."""

    def test_empty_product_and_short_address_dropped(self):
        rows = [row(tdu_id=11, tdu_keterangan_produk=""),
                row(tdu_id=12, tdu_alamat="Jl. A", tdu_koordinat="-6.5,106.8")]
        self.assertEqual(U.candidates(rows, KEC, 0, 0), [])

    def test_workers_tiebreak_uses_omset(self):
        rows = [row(tdu_id=21, tdu_nama="Tie A", tdu_jumlah_tenaga_kerja="4", tdu_omset_perbulan="1000000"),
                row(tdu_id=22, tdu_nama="Tie B", tdu_jumlah_tenaga_kerja="4", tdu_omset_perbulan="9000000")]
        order = [r["name"] for r in U.sorted_rows(U.candidates(rows, KEC, 0, 0), "default")]
        self.assertEqual(order[0], "Tie B")

    def test_cli_limit_and_refresh_flag(self):
        import io
        from contextlib import redirect_stdout
        orig_load = U.load
        U.load = lambda refresh=False: (ROWS, KEC)
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                U.main(["search", "--limit", "2", "--quiet"])
            self.assertEqual(buf.getvalue().strip(), "")   # quiet prints nothing
            buf = io.StringIO()
            with redirect_stdout(buf):
                U.main(["search", "--limit", "2"])
            self.assertEqual(len([l for l in buf.getvalue().splitlines() if l.startswith("- ")]), 2)
        finally:
            U.load = orig_load

    def test_mcp_thresholds_and_real_totals(self):
        res = M.handle({"jsonrpc": "2.0", "id": 9, "method": "tools/call",
                        "params": {"name": "search_umkm",
                                   "arguments": {"grep": "batik", "min_workers": 99}}}, self._rows())
        payload = json.loads(res["result"]["content"][0]["text"])
        self.assertEqual(payload["count"], 0)
        stats = M.handle({"jsonrpc": "2.0", "id": 10, "method": "tools/call",
                          "params": {"name": "stats_umkm", "arguments": {}}}, self._rows(), len(ROWS))
        data = json.loads(stats["result"]["content"][0]["text"])
        self.assertEqual(data["records"], len(ROWS))
        self.assertLess(data["candidates"], data["records"])

    def _rows(self):
        return U.candidates(ROWS, KEC, 0, 0)


class ReviewGapTests(unittest.TestCase):
    """Product-only grep, zero-threshold semantics, MCP stats defaults, secret/path scan."""

    def test_grep_matches_product_only(self):
        rows = [row(tdu_id=31, tdu_nama="Toko Sinar", tdu_keterangan_produk="Anyaman bambu khas Bogor",
                    tdu_alamat="Jl. Raya Dramaga No. 7, Bogor")]
        hit = U.grep(U.candidates(rows, KEC, 0, 0), "anyaman")
        self.assertEqual([r["name"] for r in hit], ["Toko Sinar"])

    def test_zero_threshold_means_unset(self):
        rows = [row(tdu_id=41, tdu_nama="Kecil Sekali", tdu_jumlah_tenaga_kerja="0",
                    tdu_omset_perbulan=None)]
        self.assertEqual(len(U.candidates(rows, KEC, 0, 0)), 1)          # 0/0 = no floor
        self.assertEqual(len(U.candidates(rows, KEC, 0, 5_000_000)), 0)  # omset floor only
        self.assertEqual(len(U.candidates(rows, KEC, 3, 0)), 0)          # workers floor only
        self.assertTrue(U.passes_floor(30, 0, 20, 0))
        self.assertFalse(U.passes_floor(3, 10_000_000, 20, 0))           # omset must not rescue

    def test_mcp_stats_uses_documented_defaults(self):
        res = M.handle({"jsonrpc": "2.0", "id": 11, "method": "tools/call",
                        "params": {"name": "stats_umkm", "arguments": {}}}, self._rows(), len(ROWS))
        data = json.loads(res["result"]["content"][0]["text"])
        self.assertEqual(data["min_workers"], 3)
        self.assertEqual(data["min_omset"], 5_000_000)
        self.assertEqual(data["records"], len(ROWS))
        self.assertLessEqual(data["candidates"], len(ROWS))

    def test_package_has_no_secrets_or_user_paths(self):
        import pathlib
        root = pathlib.Path(__file__).resolve().parent.parent
        offenders = []
        for path in root.rglob("*"):
            if path.suffix in (".py", ".md") and path.is_file() and not path.name.startswith("test_"):
                text = path.read_text(errors="ignore")
                for needle in ("/root/", "/home/", "api_key=", "password=", "Bearer "):
                    if needle in text:
                        offenders.append(f"{path.name}:{needle}")
        self.assertEqual(offenders, [])

    def _rows(self):
        return U.candidates(ROWS, KEC, 0, 0)


if __name__ == "__main__":
    unittest.main()
