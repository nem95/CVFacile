#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Assemble the GitHub Pages site into a folder.

Copies docs/ and examples/output, makes WebP thumbnails of the template renders
(480 and 910 px wide), and fills __VERSION__ and __LASTMOD__ in the text files.
Needs Pillow (pip install pillow), unlike the CVfacile tool itself.

Usage: python3 scripts/build_site.py [out_dir]   (default: _site)
Preview: python3 -m http.server -d _site
"""
import datetime
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
out = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "_site").resolve()

if out.exists():
    shutil.rmtree(str(out))
shutil.copytree(str(ROOT / "docs"), str(out))
renders = out / "examples" / "output"
shutil.copytree(str(ROOT / "examples" / "output"), str(renders))

thumbs = renders / "thumb"
thumbs.mkdir()
for png in sorted(renders.glob("*.png")):
    img = Image.open(str(png)).convert("RGB")
    for width in (480, 910):
        height = round(img.height * width / img.width)
        img.resize((width, height), Image.LANCZOS).save(
            str(thumbs / ("%s-%d.webp" % (png.stem, width))), "WEBP", quality=80, method=6)

version = re.search(r'__version__ = "([^"]+)"', (ROOT / "src" / "cvfacile" / "__init__.py").read_text()).group(1)
try:
    lastmod = subprocess.check_output(["git", "log", "-1", "--format=%cs"], cwd=str(ROOT), text=True).strip()
except (OSError, subprocess.CalledProcessError):
    lastmod = ""
lastmod = lastmod or datetime.date.today().isoformat()

for f in list(out.rglob("*.html")) + list(out.rglob("*.xml")) + list(out.rglob("*.txt")):
    text = f.read_text(encoding="utf-8")
    if "__VERSION__" in text or "__LASTMOD__" in text:
        f.write_text(text.replace("__VERSION__", version).replace("__LASTMOD__", lastmod), encoding="utf-8")

print("site: %s (version %s, updated %s)" % (out, version, lastmod))
