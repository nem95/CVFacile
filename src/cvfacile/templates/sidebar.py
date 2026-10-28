# SPDX-License-Identifier: AGPL-3.0-or-later
"""Two-column template: light sidebar (photo, contact, skills) + main column."""
from __future__ import annotations

from ..latex import escape
from .common import LABELS, Context, document  # noqa: F401  (LABELS is part of the template API)

NAME = "sidebar"
DESCRIPTION = "Two columns: sidebar (photo, contact, skills) and main column. A4, Lato font."

FONTS = r"\usepackage[default]{lato}"
GEOMETRY = "margin=0pt"
MACROS = r"""
\newif\ifside
\newcommand{\cvsection}[1]{\ifside
  \vspace{9pt}{\color{accent}\bfseries\small\MakeUppercase{#1}}\par
  \vspace{2pt}{\color{accent!40}\rule{\linewidth}{0.6pt}}\par\vspace{3pt}%
  \else
  \vspace{8pt}{\color{accent}\bfseries\large\MakeUppercase{#1}}\par
  \vspace{2pt}{\color{accent!40}\rule{\linewidth}{0.6pt}}\par\vspace{4pt}\fi}
\newcommand{\cvcontact}[2]{\makebox[1.2em][c]{\color{accent}#1}\hspace{4pt}{\small #2}\par\vspace{3pt}}
\newcommand{\cvcontactsep}{}
\newcommand{\cvlang}[2]{{\small\bfseries #1}\cvif{#2}{{\small\color{muted} \ - #2}}}
\newcommand{\cvlangsep}{\par\vspace{2pt}}
\newcommand{\cvskill}[2]{%
  {\bfseries\footnotesize #1}\par\vspace{1pt}
  {\footnotesize\color{ink!85} #2}\par\vspace{5pt}}
\newcommand{\cvedu}[4]{{\small\bfseries #1}\par
  \cvif{#2}{{\footnotesize\color{accent} #2}\par}%
  \cvif{#3#4}{{\footnotesize\color{muted} #3\cvif{#3}{\cvif{#4}{\ \textbullet\ }}#4}\par}\vspace{5pt}}
\newcommand{\cvjob}[4]{%
  {\bfseries\normalsize #1}\hfill{\small\color{muted}#4}\par
  {\color{accent}\bfseries\small #2}{\small\color{muted}\cvif{#3}{\ \textbullet\ #3}}\par\vspace{2pt}}
\newcommand{\cvproject}[4]{%
  {\bfseries\small #1}{\small\color{accent}\cvif{#2}{\ \textbar\ #2}}\par
  {\footnotesize\color{ink!90} #4}\par
  \cvif{#3}{{\footnotesize\color{muted}\textit{#3}}\par}\vspace{5pt}}
"""


def render(cv, lang, photo_file=None):
    c = Context(cv, lang, photo_file)

    side = ["\\vspace{1.1cm}\n"]
    if c.photo:
        side.append("\\centering\n\\begin{tikzpicture}\n  \\clip (0,0) circle (1.75cm);\n"
                    "  \\node at (0,-0.3) {\\includegraphics[width=4.8cm]{%s}};\n\\end{tikzpicture}\n"
                    "\\par\\vspace{4pt}\n" % c.photo)
    side.append("\\raggedright\n")
    if c.contact_list:
        side.append("\\cvsection{%s}\n%s\n" % (escape(c.labels["contact"]), c.contacts()))
    side.append(c.sections("languages", "skills", "education"))

    main = ["\\vspace{1.15cm}\n{\\fontsize{28}{32}\\selectfont\\bfseries %s \\textcolor{accent}{%s}}\\par\\vspace{4pt}\n"
            % (c.first, c.last)]
    if c.label:
        main.append("{\\Large\\color{muted} %s}\\par\n" % c.label)
    main.append("\\vspace{8pt}\n\n")
    if c.summary:
        main.append("\\justifying\\noindent{\\small %s}\n\\raggedright\n\n" % c.summary)
    main.append(c.sections("work", "projects"))

    body = ("\\begin{tikzpicture}[remember picture,overlay]\n"
            "  \\fill[soft] (current page.north west) rectangle ([xshift=6.6cm]current page.south west);\n"
            "\\end{tikzpicture}%\n\\noindent\n"
            "\\begin{minipage}[t]{6.6cm}\\vspace{0pt}\\sidetrue\n"
            "\\hspace*{0.75cm}\\begin{minipage}[t]{5.1cm}\n" + "".join(side) + "\\end{minipage}\n\\end{minipage}%\n"
            "\\hspace{0.8cm}%\n\\begin{minipage}[t]{12.9cm}\n" + "".join(main) + "\\end{minipage}\n")
    return document(c, FONTS, GEOMETRY, MACROS, body)
