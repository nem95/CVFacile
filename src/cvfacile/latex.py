# SPDX-License-Identifier: AGPL-3.0-or-later
"""Turn plain text into safe LaTeX.

Supported inline markup in every text field:
  **bold**        -> \\textbf{bold}
  [label](url)    -> \\href{url}{label}
Everything else is escaped, so users never have to write LaTeX.
"""
from __future__ import annotations

import re

_ESCAPES = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
    "•": r"\textbullet{}",
}
_ESCAPE_RE = re.compile("|".join(re.escape(c) for c in _ESCAPES))
_INLINE_RE = re.compile(r"\*\*(.+?)\*\*|\[([^\]]+)\]\(([^)\s]+)\)")


def escape(text: str) -> str:
    return _ESCAPE_RE.sub(lambda m: _ESCAPES[m.group(0)], str(text))


def escape_url(url: str) -> str:
    """Escape a URL for \\href: hyperref handles the other special characters itself."""
    return str(url).replace("\\", "").replace("%", r"\%").replace("#", r"\#")


def inline(text: str) -> str:
    """Escape text and convert the small inline markup to LaTeX."""
    text = str(text)
    out, pos = [], 0
    for m in _INLINE_RE.finditer(text):
        out.append(escape(text[pos:m.start()]))
        if m.group(1) is not None:
            out.append(r"\textbf{%s}" % inline(m.group(1)))
        else:
            out.append(r"\href{%s}{%s}" % (escape_url(m.group(3)), inline(m.group(2))))
        pos = m.end()
    out.append(escape(text[pos:]))
    return "".join(out)
