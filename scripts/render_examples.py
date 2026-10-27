#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Rebuild examples/output: one PDF and one PNG per template, from examples/example.json.

Usage: python3 scripts/render_examples.py [--engine docker|pdflatex|tectonic]
"""
import argparse
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cvfacile import build  # noqa: E402
from cvfacile.templates import TEMPLATES  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("--engine", default="auto")
args = parser.parse_args()

out = ROOT / "examples" / "output"
out.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory() as tmp:
    for name in TEMPLATES:
        r = build.build(ROOT / "examples" / "example.json", template=name, out_dir=tmp,
                        formats=("pdf", "png"), dpi=110, engine=args.engine)
        if not r["ok"]:
            sys.exit("%s failed: %s" % (name, r["errors"]))
        shutil.copy(r["files"]["pdf"], str(out / (name + ".pdf")))
        shutil.copy(r["images"][0], str(out / (name + ".png")))
        print("%-9s %d page(s) %s" % (name, r["pages"], "; ".join(w["message"] for w in r["warnings"])))
