# SPDX-License-Identifier: AGPL-3.0-or-later
"""Load, resolve (variant + language + hidden fields) and validate CV data."""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

LANG_KEY = re.compile(r"^[a-z]{2}$")
HEX = re.compile(r"^#?[0-9A-Fa-f]{6}$")

CONTACT_FIELDS = ("email", "phone", "location", "website", "github", "linkedin")
SECTIONS = ("summary", "work", "projects", "education", "skills", "languages")
HIDEABLE = set(CONTACT_FIELDS) | set(SECTIONS) | {"photo"}
TOP_LEVEL = {"$schema", "basics", "work", "projects", "education", "skills",
             "languages", "labels", "theme", "hide", "variants", "template", "lang"}


class CVError(Exception):
    pass


# ---------- loading ----------

def load(path) -> dict:
    path = Path(path)
    if not path.is_file():
        raise CVError("File not found: %s" % path)
    suffix = path.suffix.lower()
    if suffix == ".json":
        parse = json.loads
    elif suffix in (".yaml", ".yml"):
        try:
            import yaml  # optional dependency
        except ImportError:
            raise CVError("YAML files need PyYAML (pip install pyyaml). JSON works with no dependency.")
        parse = yaml.safe_load
    else:
        raise CVError("Unsupported format: %s (use .json, .yaml or .yml)" % suffix)
    try:
        data = parse(path.read_text(encoding="utf-8"))
    except Exception as e:  # JSON, YAML and encoding errors all become a readable message
        raise CVError("Cannot read %s: %s" % (path.name, e))
    if not isinstance(data, dict):
        raise CVError("The file must contain an object at the root.")
    return data


# ---------- resolving ----------

def is_localized(value) -> bool:
    return (isinstance(value, dict) and bool(value)
            and all(isinstance(k, str) and LANG_KEY.match(k) for k in value))


def languages_used(node, found=None) -> set:
    """All language codes used in localized values, e.g. {"fr", "en"}."""
    found = set() if found is None else found
    if is_localized(node):
        found.update(node)
        for v in node.values():
            languages_used(v, found)
    elif isinstance(node, dict):
        for v in node.values():
            languages_used(v, found)
    elif isinstance(node, list):
        for v in node:
            languages_used(v, found)
    return found


def default_lang(data: dict) -> str:
    """The "lang" field, else English if present, else the first language used."""
    used = sorted(languages_used(data))
    return data.get("lang") or ("en" if "en" in used or not used else used[0])


def localize(node, lang, missing=None, path="$"):
    """Replace every {"fr": ..., "en": ...} value by the requested language."""
    if is_localized(node):
        if lang in node:
            return localize(node[lang], lang, missing, path)
        if missing is not None:
            missing.append(path)
        fallback = node.get("en", next(iter(node.values())))
        return localize(fallback, lang, missing, path)
    if isinstance(node, dict):
        return {k: localize(v, lang, missing, "%s.%s" % (path, k)) for k, v in node.items()}
    if isinstance(node, list):
        return [localize(v, lang, missing, "%s[%d]" % (path, i)) for i, v in enumerate(node)]
    return node


def deep_merge(base, override):
    """Merge dicts recursively; any other value (lists included) is replaced."""
    if isinstance(base, dict) and isinstance(override, dict):
        out = dict(base)
        for k, v in override.items():
            out[k] = deep_merge(base.get(k), v)
        return out
    return copy.deepcopy(override)


def resolve(data: dict, lang: str, variant=None, hide=()):
    """Return (cv, missing_translations) ready for a template."""
    data = copy.deepcopy(data)
    variants = data.pop("variants", {}) or {}
    hidden = set(data.pop("hide", []) or [])
    if variant:
        if variant not in variants:
            raise CVError("Unknown variant: %s (available: %s)"
                          % (variant, ", ".join(sorted(variants)) or "none"))
        patch = dict(variants[variant])
        hidden |= set(patch.pop("hide", []) or [])
        data = deep_merge(data, patch)
    hidden |= set(hide or ())

    missing = []
    cv = localize(data, lang, missing)
    basics = cv.setdefault("basics", {})
    for key in hidden:
        basics.pop(key, None)  # contact fields, photo and summary live in "basics"
        if key in SECTIONS:
            cv.pop(key, None)
    return cv, missing


# ---------- validation ----------

def _issue(level, path, message):
    return {"level": level, "path": path, "message": message}


def _check_text(issues, value, path, required=False):
    if value is None or value == "":
        if required:
            issues.append(_issue("error", path, "Required field is missing."))
        return
    if not isinstance(value, str):
        issues.append(_issue("error", path, "Must be a string."))
        return
    if value.count("**") % 2:
        issues.append(_issue("warning", path, 'Unclosed bold: odd number of "**".'))


def _check_list(issues, cv, key, item_check):
    items = cv.get(key)
    if items is None:
        return
    if not isinstance(items, list):
        issues.append(_issue("error", "$.%s" % key, "Must be a list."))
        return
    for i, item in enumerate(items):
        path = "$.%s[%d]" % (key, i)
        if not isinstance(item, dict):
            issues.append(_issue("error", path, "Must be an object."))
            continue
        item_check(item, path)


def _check_text_list(issues, value, path):
    if value is None:
        return
    if not isinstance(value, list):
        issues.append(_issue("error", path, "Must be a list of strings."))
        return
    for i, v in enumerate(value):
        _check_text(issues, v, "%s[%d]" % (path, i), required=True)


def _check_hide(issues, hide, path):
    if hide is None:
        return
    if not isinstance(hide, list):
        issues.append(_issue("error", path, "Must be a list."))
        return
    for h in hide:
        if h not in HIDEABLE:
            issues.append(_issue("warning", path, "Unknown value: %s" % h))


def validate_resolved(cv: dict, base_dir: Path) -> list:
    """Check one resolved CV (a single language and variant)."""
    issues = []
    for key in cv:
        if key not in TOP_LEVEL and not key.startswith("_"):
            issues.append(_issue("warning", "$.%s" % key, "Unknown key, ignored."))

    basics = cv.get("basics")
    if not isinstance(basics, dict):
        issues.append(_issue("error", "$.basics", '"basics" section is required (object).'))
        basics = {}
    _check_text(issues, basics.get("name"), "$.basics.name", required=True)
    for key in ("label", "summary") + CONTACT_FIELDS:
        _check_text(issues, basics.get(key), "$.basics.%s" % key)
    photo = basics.get("photo")
    if photo:
        if not isinstance(photo, str):
            issues.append(_issue("error", "$.basics.photo", "Must be a file path."))
        elif not (base_dir / photo).is_file():
            issues.append(_issue("error", "$.basics.photo",
                                 "Photo not found: %s (path is relative to the CV file)." % photo))

    def work(item, path):
        _check_text(issues, item.get("position"), path + ".position", required=True)
        _check_text(issues, item.get("company"), path + ".company", required=True)
        for k in ("location", "dates"):
            _check_text(issues, item.get(k), "%s.%s" % (path, k))
        _check_text_list(issues, item.get("highlights"), path + ".highlights")

    def project(item, path):
        _check_text(issues, item.get("name"), path + ".name", required=True)
        for k in ("kind", "url", "description"):
            _check_text(issues, item.get(k), "%s.%s" % (path, k))
        _check_text_list(issues, item.get("keywords"), path + ".keywords")

    def education(item, path):
        _check_text(issues, item.get("degree"), path + ".degree", required=True)
        for k in ("institution", "location", "dates"):
            _check_text(issues, item.get(k), "%s.%s" % (path, k))

    def skill(item, path):
        _check_text(issues, item.get("name"), path + ".name", required=True)
        _check_text_list(issues, item.get("keywords"), path + ".keywords")

    def language(item, path):
        _check_text(issues, item.get("language"), path + ".language", required=True)
        _check_text(issues, item.get("fluency"), path + ".fluency")

    _check_list(issues, cv, "work", work)
    _check_list(issues, cv, "projects", project)
    _check_list(issues, cv, "education", education)
    _check_list(issues, cv, "skills", skill)
    _check_list(issues, cv, "languages", language)

    theme = cv.get("theme") or {}
    accent = theme.get("accent") if isinstance(theme, dict) else None
    if accent is not None and not (isinstance(accent, str) and HEX.match(accent)):
        issues.append(_issue("error", "$.theme.accent", 'Expected a hex color, e.g. "2F5D8A".'))
    return issues


def validate(data: dict, base_dir: Path) -> list:
    """Check the base CV and every variant, in every language used by the file."""
    issues = []
    variants = data.get("variants") or {}
    if not isinstance(variants, dict):
        issues.append(_issue("error", "$.variants", "Must be an object { name: changes }."))
        variants = {}
    _check_hide(issues, data.get("hide"), "$.hide")
    for name, patch in variants.items():
        if isinstance(patch, dict):
            _check_hide(issues, patch.get("hide"), "$.variants.%s.hide" % name)
        else:
            issues.append(_issue("error", "$.variants.%s" % name, "Must be an object."))
    # Resolving needs well-formed "hide" and "variants": stop here otherwise.
    if any(i["level"] == "error" for i in issues):
        return issues

    langs = sorted(languages_used(data)) or [default_lang(data)]
    seen = set()
    for variant in [None] + sorted(variants):
        for lang in langs:
            try:
                cv, missing = resolve(data, lang, variant)
            except CVError as e:
                issues.append(_issue("error", "$", str(e)))
                continue
            where = "[%s%s] " % (lang, ", variant " + variant if variant else "")
            found = [_issue("warning", p, 'Missing "%s" translation.' % lang) for p in missing]
            found += validate_resolved(cv, base_dir)
            for issue in found:
                key = (issue["level"], issue["path"], issue["message"])
                if key in seen:
                    continue
                seen.add(key)
                issue["message"] = where + issue["message"] if variant or len(langs) > 1 else issue["message"]
                issues.append(issue)
    return issues


def check(path) -> dict:
    """Load and validate a CV file: {"ok": bool, "issues": [...]}."""
    path = Path(path).resolve()
    issues = validate(load(path), path.parent)
    return {"ok": not any(i["level"] == "error" for i in issues), "issues": issues}
