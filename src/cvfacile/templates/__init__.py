# SPDX-License-Identifier: AGPL-3.0-or-later
"""Template registry. To add a template, create a module with NAME,
DESCRIPTION, LABELS and render(cv, lang, photo_file) -> str, then list it here.
Most templates build on common.py: they only define macros and layout."""
from . import banner, classic, compact, dark, elegant, minimal, modern, sidebar, tech, timeline

TEMPLATES = {m.NAME: m for m in (sidebar, classic, modern, minimal, timeline, compact, dark, elegant, banner, tech)}
DEFAULT = "sidebar"
