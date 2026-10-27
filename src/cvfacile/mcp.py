# SPDX-License-Identifier: AGPL-3.0-or-later
"""Minimal MCP server over stdio (no dependency, no port).

The agent starts `./cvfacile mcp` itself when it needs it (see .mcp.json)
and stops it afterwards. Messages are newline-delimited JSON-RPC 2.0.
"""
from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

from . import __version__, build, model
from .templates import DEFAULT, TEMPLATES

SCHEMA_PATH = build.ROOT / "schema" / "cv.schema.json"

TOOLS = [
    {
        "name": "check_cv",
        "description": "Validate a CV file (JSON/YAML) without compiling it. Returns errors and "
                       "warnings with their location (e.g. $.work[0].position).",
        "inputSchema": {"type": "object", "required": ["path"],
                        "properties": {"path": {"type": "string", "description": "Path to the CV file"}}},
    },
    {
        "name": "build_cv",
        "description": "Compile a CV to PDF (+ PNG). Returns the output files, the page count, "
                       "layout warnings and, if preview=true, an image of the first page.",
        "inputSchema": {
            "type": "object", "required": ["path"],
            "properties": {
                "path": {"type": "string", "description": "Path to the CV file"},
                "lang": {"type": "string", "description": "Language, e.g. en or fr"},
                "template": {"type": "string", "description": "Template (default: %s)" % DEFAULT},
                "variant": {"type": "string", "description": 'Variant defined in "variants"'},
                "hide": {"type": "array", "items": {"type": "string"},
                         "description": "Fields or sections to hide: %s" % ", ".join(sorted(model.HIDEABLE))},
                "out": {"type": "string", "description": "Output directory (default: out)"},
                "preview": {"type": "boolean", "description": "Attach a low-resolution PNG preview"},
                "fit": {"type": "boolean", "description": "Shrink the text to 9pt if the CV is longer than one page (default: true)"},
            },
        },
    },
    {
        "name": "list_templates",
        "description": "List available templates and their languages.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_schema",
        "description": "Return the JSON Schema of the CV format (fields, types, translations, variants).",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def _text(obj) -> dict:
    return {"type": "text", "text": json.dumps(obj, ensure_ascii=False, indent=2)}


def _preview(pdf: str):
    try:
        import fitz
    except ImportError:
        return None
    with fitz.open(pdf) as doc:
        png = doc[0].get_pixmap(dpi=90).tobytes("png")
    return {"type": "image", "mimeType": "image/png", "data": base64.b64encode(png).decode()}


def call_tool(name: str, args: dict):
    if name == "check_cv":
        path = Path(args["path"]).resolve()
        issues = model.validate(model.load(path), path.parent)
        result = {"ok": not any(i["level"] == "error" for i in issues), "issues": issues}
        return [_text(result)], not result["ok"]
    if name == "build_cv":
        result = build.build(args["path"], lang=args.get("lang"), template=args.get("template"),
                             variant=args.get("variant"), hide=args.get("hide") or (),
                             out_dir=args.get("out") or "out", fit=args.get("fit", True))
        content = [_text(result)]
        if result["ok"] and args.get("preview") and result["files"].get("pdf"):
            image = _preview(result["files"]["pdf"])
            if image:
                content.append(image)
        return content, not result["ok"]
    if name == "list_templates":
        return [_text([{"name": m.NAME, "description": m.DESCRIPTION, "languages": sorted(m.LABELS)}
                       for m in TEMPLATES.values()])], False
    if name == "get_schema":
        return [{"type": "text", "text": SCHEMA_PATH.read_text(encoding="utf-8")}], False
    raise model.CVError("Unknown tool: %s" % name)


def handle(msg: dict):
    method, mid = msg.get("method"), msg.get("id")
    if mid is None:
        return None  # notification (e.g. notifications/initialized)
    if method == "initialize":
        version = (msg.get("params") or {}).get("protocolVersion") or "2025-06-18"
        result = {"protocolVersion": version, "capabilities": {"tools": {}},
                  "serverInfo": {"name": "cvfacile", "version": __version__}}
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        params = msg.get("params") or {}
        try:
            content, is_error = call_tool(params.get("name"), params.get("arguments") or {})
        except Exception as e:  # never crash the server: report to the agent
            content, is_error = [_text({"ok": False, "error": str(e)})], True
        result = {"content": content, "isError": is_error}
    else:
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": "Unknown method: %s" % method}}
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def serve():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Invalid JSON"}}
        else:
            reply = handle(msg)
        if reply is not None:
            sys.stdout.write(json.dumps(reply, ensure_ascii=False) + "\n")
            sys.stdout.flush()
