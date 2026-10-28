# SPDX-License-Identifier: AGPL-3.0-or-later
"""Photo header, then two columns split by a thin rule. Section titles as colored tags."""
from __future__ import annotations

from .common import LABELS, Context, document, paracol, photo_circle  # noqa: F401  (LABELS is part of the template API)

NAME = "banner"
DESCRIPTION = "Header with photo, two columns split by a thin rule, section titles as colored tags. Roboto."

FONTS = r"\usepackage[sfdefault]{roboto}" "\n" r"\usepackage{paracol}"
GEOMETRY = "margin=1.5cm,top=1.3cm,bottom=1.2cm"
MACROS = r"""
\newcommand{\cvsection}[1]{\par\vspace{8pt}\leavevmode\colorbox{accent}{\color{white}\bfseries\footnotesize\MakeUppercase{#1}}\par\vspace{6pt}}
\newcommand{\cvjob}[4]{{\bfseries #1}\par{\color{accent}\bfseries\small #2}\cvif{#3}{{\small\color{muted}, #3}}\hfill{\small\color{muted}#4}\par\vspace{2pt}}
\newcommand{\cvjobsep}{\vspace{5pt}}
\newenvironment{cvitems}{\small\begin{itemize}[labelsep=0.5em,leftmargin=1.1em,itemsep=1pt,parsep=0pt,topsep=1pt,label={\color{accent}\textbullet}]}{\end{itemize}}
\newcommand{\cvproject}[4]{{\bfseries #1}\cvif{#2}{{\color{muted}\ \textbar\ #2}}\par{\small #4}\par\cvif{#3}{{\footnotesize\color{accent}#3}\par}\vspace{5pt}}
\newcommand{\cvskill}[2]{{\bfseries\small #1}\par{\small\color{ink!85}#2}\par\vspace{4pt}}
\newcommand{\cvlang}[2]{{\small\bfseries #1}\cvif{#2}{\hfill{\small\color{muted}#2}}}
\newcommand{\cvlangsep}{\par\vspace{2pt}}
\newcommand{\cvedu}[4]{{\small\bfseries #1}\par\cvif{#2}{{\footnotesize #2}\par}{\footnotesize\color{muted}#3\cvif{#3}{\cvif{#4}{ \textbullet\ }}#4}\par\vspace{5pt}}
\newcommand{\cvcontact}[2]{{\color{accent}#1}~#2}
\newcommand{\cvcontactsep}{\quad}
"""


def render(cv, lang, photo_file=None):
    c = Context(cv, lang, photo_file, accent="C2410C")
    photo = photo_circle(c, 1.3)
    head = ["{\\fontsize{28}{32}\\selectfont\\bfseries %s}\\par\\vspace{3pt}\n" % c.name]
    if c.label:
        head.append("{\\large\\color{accent} %s}\\par\n" % c.label)
    head.append("\\vspace{6pt}{\\small\\raggedright %s\\par}\n" % c.contacts())
    if photo:
        body = ["\\noindent\\begin{minipage}[c]{2.8cm}%s\\end{minipage}\\hspace{0.4cm}"
                "\\begin{minipage}[c]{\\dimexpr\\linewidth-3.2cm\\relax}\n%s\\end{minipage}\\par\n" % (photo, "".join(head))]
    else:
        body = ["".join(head) + "\\par\n"]
    body.append("\\vspace{8pt}{\\color{accent}\\rule{\\linewidth}{2pt}}\\par\\vspace{4pt}\n")
    if c.summary:
        body.append("\\justifying{\\small %s\\par}\\raggedright\n" % c.summary)
    body.append(paracol(c.sections("work", "projects"), c.sections("skills", "education", "languages"), 0.68, rule="accent!25"))
    return document(c, FONTS, GEOMETRY, MACROS, "".join(body))
