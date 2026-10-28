# SPDX-License-Identifier: AGPL-3.0-or-later
"""Command line interface. Every command accepts --json for agents."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from . import __version__, build, model
from .templates import DEFAULT, TEMPLATES, catalog

EXAMPLE = build.ROOT / "examples" / "example.json"


def _print(result: dict, as_json: bool, human):
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        human(result)


def _print_issues(issues):
    for i in issues:
        mark = "✗" if i["level"] == "error" else "!"
        print("  %s %s : %s" % (mark, i["path"], i["message"]))


def cmd_build(a):
    hide = [h.strip() for h in (a.hide or "").split(",") if h.strip()]
    formats = [f.strip() for f in a.formats.split(",") if f.strip()]
    names = list(TEMPLATES) if a.template == "all" else [a.template]
    results = [build.build(a.cv, lang=a.lang, template=t, variant=a.variant, hide=hide, out_dir=a.out,
                           formats=formats, dpi=a.dpi, engine=a.engine, fit=not a.no_fit) for t in names]
    result = results[0] if len(results) == 1 else {"ok": all(r["ok"] for r in results), "results": results}

    def human(r):
        if not r["ok"]:
            print("Failed (%s):" % r["stage"])
            _print_issues(r["errors"])
            if r.get("tex"):
                print("  LaTeX source: %s" % r["tex"])
            return
        print("CV built (%s, %s, %d page(s), engine %s):" % (r["template"], r["lang"], r["pages"] or 0, r["engine"]))
        for path in list(r["files"].values()) + r["images"]:
            print("  %s" % path)
        if r["warnings"]:
            print("Warnings:")
            _print_issues(r["warnings"])

    def human_all(r):
        for one in r.get("results", [r]):
            human(one)
    _print(result, a.json, human_all)
    return 0 if result["ok"] else 1


def cmd_check(a):
    result = model.check(a.cv)

    def human(r):
        print("CV is valid." if r["ok"] else "CV is invalid:")
        _print_issues(r["issues"])
    _print(result, a.json, human)
    return 0 if result["ok"] else 1


def cmd_templates(a):
    result = {"default": DEFAULT, "templates": catalog()}

    def human(r):
        for t in r["templates"]:
            print("%s%s\n  %s\n  Languages: %s" % (t["name"], " (default)" if t["name"] == r["default"] else "",
                                                 t["description"], ", ".join(t["languages"])))
    _print(result, a.json, human)
    return 0


def cmd_init(a):
    target = Path(a.path)
    if target.exists():
        raise model.CVError("%s already exists." % target)
    data = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    data["$schema"] = (build.ROOT / "schema" / "cv.schema.json").as_uri()  # keeps editor autocompletion working
    photo = target.resolve().parent / "photo.jpg"
    if photo.exists():
        data["basics"].pop("photo", None)  # never overwrite or reuse someone's photo
    else:
        shutil.copy(str(EXAMPLE.parent / "photo.jpg"), str(photo))
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result = {"ok": True, "created": str(target)}
    _print(result, a.json, lambda r: print("Created: %s\nEdit it, then run: ./cvfacile build %s" % (target, target)))
    return 0


def cmd_doctor(a):
    engines = build.available_engines()
    result = {"version": __version__, "python": sys.version.split()[0], "engines": engines,
              "rasterizer": build.available_rasterizer(), "ready": bool(engines)}

    def human(r):
        print("CVfacile %s, Python %s" % (r["version"], r["python"]))
        print("LaTeX engines: %s" % (", ".join(r["engines"]) or "none -> run ./cvfacile setup"))
        print("Images: %s" % (r["rasterizer"] or "no tool (pip install pymupdf)"))
    _print(result, a.json, human)
    return 0 if engines else 1


def cmd_setup(a):
    from .setup_tectonic import install
    path = install()
    _print({"ok": True, "tectonic": path}, a.json, lambda r: print("Tectonic installed: %s" % path))
    return 0


def cmd_mcp(a):
    from .mcp import serve
    serve()
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="cvfacile", description="Generate LaTeX CVs from a JSON or YAML file.")
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="command")

    def add(name, help_text, fn):
        sp = sub.add_parser(name, help=help_text)
        sp.add_argument("--json", action="store_true", help="JSON output (for agents)")
        sp.set_defaults(fn=fn)
        return sp

    b = add("build", "build the PDF (and images) of a CV", cmd_build)
    b.add_argument("cv", help="CV file (.json, .yaml)")
    b.add_argument("--lang", help='language, e.g. en or fr (default: the file\'s "lang" field)')
    b.add_argument("--template", help="template, or \"all\" to build every template (default: %s)" % DEFAULT)
    b.add_argument("--variant", help='variant defined in "variants"')
    b.add_argument("--hide", help="fields or sections to hide, e.g. phone,photo,projects")
    b.add_argument("--out", default="out", help="output directory (default: out)")
    b.add_argument("--formats", default="pdf,png", help="pdf,png,jpg (default: pdf,png)")
    b.add_argument("--dpi", type=int, default=200, help="image resolution (default: 200)")
    b.add_argument("--engine", default="auto", choices=("auto",) + build.ENGINES)
    b.add_argument("--no-fit", action="store_true", help="do not shrink the text when the CV is longer than one page")

    c = add("check", "validate a CV without compiling it", cmd_check)
    c.add_argument("cv")
    add("templates", "list templates", cmd_templates)
    i = add("init", "create an example CV to fill in", cmd_init)
    i.add_argument("path", nargs="?", default="cv.json")
    add("doctor", "check installed tools", cmd_doctor)
    add("setup", "install Tectonic into ./.bin (if no LaTeX is installed)", cmd_setup)
    add("mcp", "MCP mode (stdio): started automatically by agents", cmd_mcp)

    a = p.parse_args(argv)
    if not getattr(a, "fn", None):
        p.print_help()
        return 1
    try:
        return a.fn(a)
    except model.CVError as e:
        if getattr(a, "json", False):
            print(json.dumps({"ok": False, "errors": [{"level": "error", "path": "$", "message": str(e)}]},
                             ensure_ascii=False, indent=2))
        else:
            print("Error: %s" % e, file=sys.stderr)
        return 1
