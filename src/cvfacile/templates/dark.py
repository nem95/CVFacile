# SPDX-License-Identifier: AGPL-3.0-or-later
"""Main column on the left, dark sidebar on the right."""
from __future__ import annotations

from ..latex import escape
from .common import LABELS, Context, document, photo_circle  # noqa: F401

NAME = "dark"
DESCRIPTION = "Dark sidebar on the right (photo, contact, skills), bright accent color. Lato."

FONTS = r"\usepackage[default]{lato}"
GEOMETRY = "margin=0pt"
MACROS = r"""
\definecolor{sidetext}{HTML}{CBD5E1}
\colorlet{accentdark}{accent!65!black}
\newif\ifside
\newcommand{\cvsection}[1]{\par\ifside\vspace{9pt}{\color{accent}\bfseries\small\MakeUppercase{#1}}\par\vspace{2pt}%
  {\color{sidetext!30!soft}\rule{\linewidth}{0.6pt}}\par\vspace{4pt}%
  \else\vspace{9pt}{\color{ink}\bfseries\large\MakeUppercase{#1}}\par\vspace{3pt}{\color{accent}\rule{1.2cm}{2pt}}\par\vspace{5pt}\fi}
\newcommand{\cvjob}[4]{{\bfseries #1}\hfill{\small\color{muted}#4}\par{\color{accentdark}\bfseries\small #2}\cvif{#3}{{\small\color{muted}\ \textbullet\ #3}}\par\vspace{2pt}}
\newcommand{\cvproject}[4]{{\bfseries\small #1}\cvif{#2}{{\small\color{accentdark}\ \textbar\ #2}}\par{\footnotesize #4}\par%
  \cvif{#3}{{\footnotesize\color{muted}\itshape #3}\par}\vspace{5pt}}
\newcommand{\cvskill}[2]{{\bfseries\footnotesize\color{white}#1}\par\vspace{1pt}{\footnotesize #2}\par\vspace{5pt}}
\newcommand{\cvlang}[2]{{\small\bfseries\color{white}#1}\cvif{#2}{{\small\ -- #2}}}
\newcommand{\cvlangsep}{\par\vspace{2pt}}
\newcommand{\cvedu}[4]{{\small\bfseries\color{white}#1}\par\cvif{#2}{{\footnotesize\color{accent}#2}\par}%
  {\footnotesize #3\cvif{#3}{\cvif{#4}{ \textbullet\ }}#4}\par\vspace{5pt}}
\newcommand{\cvcontact}[2]{\makebox[1.2em][c]{\color{accent}#1}\hspace{4pt}{\small #2}}
\newcommand{\cvcontactsep}{\par\vspace{3pt}}
"""


def render(cv, lang, photo_file=None):
    c = Context(cv, lang, photo_file, accent="38BDF8", soft="1E293B")
    main = ["\\vspace{1.2cm}\n{\\fontsize{28}{32}\\selectfont\\bfseries %s \\textcolor{accentdark}{%s}}\\par\\vspace{4pt}\n"
            % (c.first, c.last)]
    if c.label:
        main.append("{\\Large\\color{muted} %s}\\par\n" % c.label)
    main.append("\\vspace{8pt}\n")
    if c.summary:
        main.append("\\justifying{\\small %s}\\par\\raggedright\n" % c.summary)
    main.append(c.sections("work", "projects"))

    side = ["\\vspace{1.1cm}\n"]
    photo = photo_circle(c, 1.6, "accent, line width=2pt")
    if photo:
        side.append("\\centering\n%s\\par\\vspace{4pt}\n" % photo)
    side.append("\\raggedright\n")
    if c.contact_list:
        side.append("\\cvsection{%s}\n%s\\par\n" % (escape(c.labels["contact"]), c.contacts()))
    side.append(c.sections("skills", "languages", "education"))

    body = ("\\begin{tikzpicture}[remember picture,overlay]\n"
            "\\fill[soft] ([xshift=-6.6cm]current page.north east) rectangle (current page.south east);\n"
            "\\end{tikzpicture}%\n\\noindent\\hspace*{1.2cm}"
            "\\begin{minipage}[t]{12.3cm}\\vspace{0pt}\n" + "".join(main) + "\\end{minipage}%\n"
            "\\hspace{0.9cm}\\begin{minipage}[t]{6.6cm}\\vspace{0pt}\\sidetrue\\color{sidetext}\n"
            "\\hspace*{0.7cm}\\begin{minipage}[t]{5.2cm}\n" + "".join(side) + "\\end{minipage}\n\\end{minipage}\n")
    return document(c, FONTS, GEOMETRY, MACROS, body)
