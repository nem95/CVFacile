# SPDX-License-Identifier: AGPL-3.0-or-later
"""Download the Tectonic LaTeX engine into ./.bin (no admin rights needed)."""
from __future__ import annotations

import io
import json
import platform
import tarfile
import urllib.request
import zipfile

from .build import LOCAL_BIN
from .model import CVError

API = "https://api.github.com/repos/tectonic-typesetting/tectonic/releases?per_page=30"


def _target() -> str:
    system, machine = platform.system(), platform.machine().lower()
    arch = "aarch64" if machine in ("arm64", "aarch64") else "x86_64"
    if system == "Linux":
        return "%s-unknown-linux-musl" % arch
    if system == "Darwin":
        return "%s-apple-darwin" % arch
    if system == "Windows":
        return "x86_64-pc-windows-msvc"
    raise CVError("Automatic install is not supported on: %s" % system)


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "cvfacile-setup"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def install() -> str:
    target = _target()
    releases = json.loads(_get(API).decode())
    for rel in releases:
        if not rel.get("tag_name", "").startswith("tectonic@") or rel.get("prerelease"):
            continue
        for asset in rel.get("assets", []):
            name = asset["name"]
            if target in name and (name.endswith(".tar.gz") or name.endswith(".zip")):
                blob = _get(asset["browser_download_url"])
                LOCAL_BIN.mkdir(exist_ok=True)
                exe = "tectonic.exe" if name.endswith(".zip") else "tectonic"
                if name.endswith(".zip"):
                    with zipfile.ZipFile(io.BytesIO(blob)) as z:
                        (LOCAL_BIN / exe).write_bytes(z.read(exe))
                else:
                    with tarfile.open(fileobj=io.BytesIO(blob)) as t:
                        member = next(m for m in t.getmembers() if m.name.endswith("tectonic"))
                        (LOCAL_BIN / exe).write_bytes(t.extractfile(member).read())
                (LOCAL_BIN / exe).chmod(0o755)
                return "%s (%s)" % (LOCAL_BIN / exe, rel["tag_name"])
    raise CVError("No Tectonic release found for %s." % target)
