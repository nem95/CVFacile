# SPDX-License-Identifier: AGPL-3.0-or-later
"""Compile .tex to PDF and render images, with whatever engine is available."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

from . import model
from .templates import DEFAULT, TEMPLATES

ROOT = Path(__file__).resolve().parents[2]
LOCAL_BIN = ROOT / ".bin"
DOCKER_IMAGE = os.environ.get("CVFACILE_DOCKER_IMAGE", "texlive/texlive:latest")
ENGINES = ("pdflatex", "tectonic", "docker")


def _which(name):
    local = LOCAL_BIN / (name + (".exe" if os.name == "nt" else ""))
    return str(local) if local.is_file() else shutil.which(name)


def available_engines() -> dict:
    found = {}
    for name in ENGINES:
        path = _which(name)
        if name == "docker" and path:
            ok = subprocess.run([path, "image", "inspect", DOCKER_IMAGE],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
            if not ok:
                continue  # docker present but image not pulled: skip to avoid a 4 GB surprise
        if path:
            found[name] = path
    return found


def available_rasterizer():
    try:
        import fitz  # noqa: F401  (PyMuPDF)
        return "pymupdf"
    except ImportError:
        pass
    if _which("pdftoppm"):
        return "pdftoppm"
    return None


def pick_engine(preference="auto"):
    engines = available_engines()
    if preference != "auto":
        if preference not in engines:
            raise model.CVError('Engine "%s" is not available. Found: %s'
                                % (preference, ", ".join(engines) or "none"))
        return preference, engines[preference]
    for name in ENGINES:
        if name in engines:
            return name, engines[name]
    raise model.CVError('No LaTeX engine found. Run "./cvfacile setup" to install '
                        "Tectonic into the project (no admin rights needed), or install TeX Live.")


def _compile(engine, exe, workdir: Path, tex_name: str):
    """Run the engine in workdir. Returns None on success, else the engine output."""
    # pdflatex needs 2 passes to place TikZ overlays (remember picture); tectonic reruns by itself.
    if engine == "pdflatex":
        cmds = [[exe, "-interaction=nonstopmode", "-halt-on-error", tex_name]] * 2
    elif engine == "tectonic":
        cmds = [[exe, "--keep-logs", "--chatter", "minimal", tex_name]]
    else:
        pdflatex = "pdflatex -interaction=nonstopmode -halt-on-error %s" % tex_name
        # Run as the current user so the output files are not owned by root.
        user = ["-u", "%d:%d" % (os.getuid(), os.getgid())] if hasattr(os, "getuid") else []
        cmds = [[exe, "run", "--rm"] + user + ["-e", "HOME=/tmp", "-v", "%s:/w" % workdir, "-w", "/w",
                                               DOCKER_IMAGE, "sh", "-c", "%s && %s" % (pdflatex, pdflatex)]]
    for cmd in cmds:
        proc = subprocess.run(cmd, cwd=str(workdir), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if proc.returncode != 0:
            return proc.stdout.decode("utf-8", "replace")
    return None


def parse_log(text: str) -> dict:
    """Extract errors (with their line number), page count and overfull boxes from a LaTeX log."""
    lines = text.splitlines()
    errors = []
    for i, line in enumerate(lines):
        if line.startswith("!") or line.startswith("error:"):
            context = next((l.strip() for l in lines[i + 1:i + 8] if re.match(r"l\.\d+", l.strip())), "")
            errors.append((line + " " + context).strip())
    pages = re.search(r"Output written on .*?\((\d+) pages?", text)
    overfull = len(re.findall(r"^Overfull \\[hv]box", text, re.M))
    return {"errors": errors, "pages": int(pages.group(1)) if pages else None, "overfull": overfull}


def _pdf_pages(pdf: Path):
    try:
        import fitz
        with fitz.open(str(pdf)) as doc:
            return doc.page_count
    except ImportError:
        return None


def rasterize(pdf: Path, fmt: str, dpi: int) -> list:
    """Render every page; returns the image paths."""
    tool = available_rasterizer()
    outputs = []
    if tool == "pymupdf":
        import fitz
        with fitz.open(str(pdf)) as doc:
            for i, page in enumerate(doc):
                suffix = "" if doc.page_count == 1 else "-%d" % (i + 1)
                out = pdf.with_name(pdf.stem + suffix + "." + fmt)
                page.get_pixmap(dpi=dpi).save(str(out))
                outputs.append(out)
    elif tool == "pdftoppm":
        flag = "-jpeg" if fmt == "jpg" else "-png"
        prefix = pdf.with_name(pdf.stem)
        for old in pdf.parent.glob(pdf.stem + "-*." + fmt):
            old.unlink()  # pages left over from a previous, longer build
        subprocess.run([_which("pdftoppm"), flag, "-r", str(dpi), str(pdf), str(prefix)], check=True)
        produced = sorted(pdf.parent.glob(pdf.stem + "-*." + fmt))
        if len(produced) == 1:
            target = pdf.with_name(pdf.stem + "." + fmt)
            produced[0].replace(target)
            produced = [target]
        outputs = produced
    return outputs


def output_stem(cv_path: Path, *parts) -> str:
    """Output file name: <file>[-<variant>][-<template>]-<lang>, safe to use as a single path component."""
    stem = "-".join(x for x in (cv_path.stem,) + parts if x)
    return re.sub(r"[^\w.-]+", "_", stem)  # variant and lang come from the user: never let them reach outside out_dir


def build(cv_path, lang=None, template=None, variant=None, hide=(), out_dir="out",
          formats=("pdf", "png"), dpi=200, engine="auto", keep_tex=True, fit=True) -> dict:
    """Validate, render and compile a CV file.

    Never raises for CV or LaTeX errors: returns {"ok": False, "stage": "validation" | "latex",
    "errors": [...]}, or on success {"ok": True, "files", "images", "pages", "warnings", ...}.
    """
    cv_path = Path(cv_path).resolve()
    data = model.load(cv_path)
    lang = lang or model.default_lang(data)
    file_template = data.get("template") or DEFAULT
    template = template or file_template
    if template not in TEMPLATES:
        raise model.CVError("Unknown template: %s (available: %s)" % (template, ", ".join(TEMPLATES)))

    issues = model.validate(data, cv_path.parent)
    errors = [i for i in issues if i["level"] == "error"]
    if errors:
        return {"ok": False, "stage": "validation", "errors": errors,
                "warnings": [i for i in issues if i["level"] == "warning"]}

    cv, _ = model.resolve(data, lang, variant, hide)
    stem = output_stem(cv_path, variant, None if template == file_template else template, lang)
    out_dir = Path(out_dir).resolve()
    work = out_dir / ".build" / stem
    if work.exists():
        shutil.rmtree(str(work))
    work.mkdir(parents=True)

    photo_file = None
    photo = cv.get("basics", {}).get("photo")
    if photo:
        src = cv_path.parent / photo
        photo_file = "photo" + src.suffix.lower()
        shutil.copy(str(src), str(work / photo_file))

    engine_name, exe = pick_engine(engine)
    pdf_built, log_file = work / "cv.pdf", work / "cv.log"
    # Try 10pt first; if the CV spills onto a second page, retry once at 9pt.
    for size in ("10pt", "9pt") if fit else ("10pt",):
        cv["_size"] = size
        (work / "cv.tex").write_text(TEMPLATES[template].render(cv, lang, photo_file), encoding="utf-8")
        failure = _compile(engine_name, exe, work, "cv.tex")
        log = parse_log(log_file.read_text("utf-8", "replace") if log_file.exists() else (failure or ""))
        if failure is not None or not pdf_built.exists():
            break
        if (_pdf_pages(pdf_built) or log["pages"] or 1) <= 1:
            break
    if failure is not None or not pdf_built.exists():
        errs = log["errors"] or [(failure or "").strip()[-1500:]]
        return {"ok": False, "stage": "latex", "engine": engine_name, "tex": str(work / "cv.tex"),
                "errors": [{"level": "error", "path": "latex", "message": e} for e in errs]}

    out_dir.mkdir(parents=True, exist_ok=True)
    pdf = out_dir / (stem + ".pdf")
    shutil.copy(str(pdf_built), str(pdf))
    files = {"pdf": str(pdf)}
    if keep_tex:
        shutil.copy(str(work / "cv.tex"), str(out_dir / (stem + ".tex")))
        files["tex"] = str(out_dir / (stem + ".tex"))

    warnings = [i for i in issues if i["level"] == "warning"]
    images = []
    for fmt in formats:
        if fmt in ("png", "jpg"):
            produced = rasterize(pdf, fmt, dpi)
            if not produced:
                warnings.append({"level": "warning", "path": "images",
                                 "message": "No tool to render images (pip install pymupdf, or install poppler-utils)."})
                break
            images += [str(p) for p in produced]
    if "pdf" not in formats:
        pdf.unlink()
        files.pop("pdf")

    pages = _pdf_pages(pdf_built) or log["pages"]
    if cv["_size"] != "10pt" and pages == 1:
        warnings.append({"level": "warning", "path": "layout",
                         "message": "Text reduced to %s to fit on one page (use --no-fit to keep 10pt)." % cv["_size"]})
    if pages and pages > 1:
        warnings.append({"level": "warning", "path": "layout",
                         "message": "The CV is %d pages long. Shorten the content to fit on one page." % pages})
    if log["overfull"]:
        warnings.append({"level": "warning", "path": "layout",
                         "message": "%d line(s) overflow their box (long text without spaces, e.g. a URL)." % log["overfull"]})
    return {"ok": True, "engine": engine_name, "template": template, "lang": lang, "variant": variant,
            "pages": pages, "files": files, "images": images, "warnings": warnings}
