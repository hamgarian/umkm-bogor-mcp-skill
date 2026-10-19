#!/usr/bin/env python3
"""Server MCP stdio minimal untuk direktori UMKM Kota Bogor.

Tools: search_umkm, stats_umkm, get_umkm. Speak JSON-RPC 2.0 over stdin/stdout (one JSON per line);
logs go to stderr so the protocol stays clean.

Register with an MCP client as: python3 <this file>
"""
import json
import sys

import umkm_bogor as U

TOOLS = [
    {"name": "search_umkm", "description": "Cari UMKM Kota Bogor yang sudah difilter lewat regex dan ambang.",
     "inputSchema": {"type": "object", "properties": {
         "grep": {"type": "string", "description": "regex atas nama/produk/alamat/kecamatan"},
         "kecamatan": {"type": "string"},
         "min_workers": {"type": "integer", "default": 3},
         "min_omset": {"type": "integer", "default": 5000000},
         "sort": {"type": "string", "enum": ["default", "workers", "omset", "name"]},
         "limit": {"type": "integer", "default": 20}}}},
    {"name": "stats_umkm", "description": "Jumlah record dan kandidat per kecamatan.",
     "inputSchema": {"type": "object", "properties": {
         "min_workers": {"type": "integer", "default": 3},
         "min_omset": {"type": "integer", "default": 5000000}}}}, 
    {"name": "get_umkm", "description": "Satu record UMKM berdasarkan id.",
     "inputSchema": {"type": "object", "properties": {"id": {"type": "string"}}, "required": ["id"]}},
]


def _text(payload):
    return [{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}]


def _search(rows, args):
    out = U.grep(rows, args["grep"]) if args.get("grep") else list(rows)
    if args.get("kecamatan"):
        out = [r for r in out if r["kecamatan"].lower() == args["kecamatan"].lower()]
    mw, mo = int(args.get("min_workers", 3)), int(args.get("min_omset", 5_000_000))
    out = [r for r in out if U.passes_floor(r["tenaga_kerja"], r["omset_per_bulan"], mw, mo)]
    out = U.sorted_rows(out, args.get("sort", "default"))
    return {"count": len(out), "rows": out[: int(args.get("limit", 20))]}


def handle(msg, rows, total_records=None):
    mid, method = msg.get("id"), msg.get("method")
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": mid, "result": {
            "protocolVersion": msg.get("params", {}).get("protocolVersion", "2024-11-05"),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "umkm-bogor", "version": "1.0.0"}}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}}
    if method == "tools/call":
        name = msg.get("params", {}).get("name")
        args = msg.get("params", {}).get("arguments", {}) or {}
        try:
            if name == "search_umkm":
                data = _search(rows, args)
            elif name == "stats_umkm":
                mw, mo = int(args.get("min_workers", 3)), int(args.get("min_omset", 5_000_000))
                subset = [r for r in rows
                          if U.passes_floor(r["tenaga_kerja"], r["omset_per_bulan"], mw, mo)]
                data = U.stats(subset, total_records or len(rows))
                data["min_workers"], data["min_omset"] = mw, mo
            elif name == "get_umkm":
                data = U.get(rows, args["id"])
            else:
                return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"unknown tool {name}"}}
        except SystemExit as exc:
            return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32000, "message": str(exc)}}
        return {"jsonrpc": "2.0", "id": mid, "result": {"content": _text(data), "isError": False}}
    if method in ("notifications/initialized", "ping"):
        return None
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": "method not found"}}


def main():
    rows_raw, kec_map = U.load()
    rows = U.candidates(rows_raw, kec_map, 0, 0)
    print(f"umkm-bogor MCP siap: {len(rows)} kandidat dari {len(rows_raw)} record", file=sys.stderr)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            reply = handle(json.loads(line), rows, len(rows_raw))
        except Exception as exc:  # keep the loop alive for the client
            reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(exc)}}
        if reply:
            print(json.dumps(reply, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
