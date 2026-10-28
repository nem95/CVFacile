# SPDX-License-Identifier: AGPL-3.0-or-later
"""Swiss-style: section titles in a left column, lots of white space, no icons."""
from __future__ import annotations

from .common import LABELS, Context, document  # noqa: F401  (LABELS is part of the template API)

NAME = "minimal"
DESCRIPTION = "Swiss style: section titles in the margin, lots of white space, almost no color. Roboto. No photo."

FONTS = r"\usepackage[sfdefault]{roboto}"
GEOMETRY = "margin=1.5cm,top=1.2cm,bottom=1.1cm"
MACROS = r"""
\newcommand{\cvsection}[1]{\par\vspace{8pt}\leavevmode\llap{\parbox[t]{2.6cm}{\raggedright\leavevmode\footnotesize\bfseries\color{accent}\MakeUppercase{#1}}\hspace{0.5cm}}\ignorespaces}
\newcommand{\cvjob}[4]{{\bfseries #1}\cvif{#2}{, #2}\cvif{#3}{{\color{muted}, #3}}\hfill{\color{muted}#4}\par\vspace{1pt}}
\newcommand{\cvjobsep}{\vspace{5pt}}
\newcommand{\cvproject}[4]{{\bfseries #1}\cvif{#2}{{\color{muted}\ \textemdash\ #2}}\par #4\cvif{#3}{ {\color{muted}(#3)}}\par\vspace{3pt}}
\newcommand{\cvskill}[2]{\hangindent=3cm\hangafter=1\makebox[3cm][l]{\bfseries #1}#2\par\vspace{2pt}}
\newcommand{\cvlang}[2]{#1\cvif{#2}{{\color{muted}\ (#2)}}}
\newcommand{\cvlangsep}{\qquad}
\newcommand{\cvedu}[4]{{\bfseries #1}\hfill{\small\color{muted}#4}\par\cvif{#2}{#2\cvif{#3}{, }}#3\par\vspace{4pt}}
\newcommand{\cvcontact}[2]{#2}
\newcommand{\cvcontactsep}{\quad{\color{muted}/}\quad}
\newenvironment{cvitems}{\begin{itemize}[labelsep=0.5em,leftmargin=1em,itemsep=1pt,parsep=0pt,topsep=2pt,label={\color{muted}\textendash}]}{\end{itemize}}
"""


def render(cv, lang, photo_file=None):
    c = Context(cv, lang, photo_file, accent="111827")
    body = ["{\\fontsize{26}{30}\\selectfont %s \\textbf{%s}}\\par\\vspace{4pt}\n" % (c.first, c.last)]
    if c.label:
        body.append("{\\large\\color{muted} %s}\\par\n" % c.label)
    body.append("\\vspace{8pt}{\\small\\raggedright %s\\par}\\vspace{6pt}\n" % c.contacts())
    body.append("\\begin{list}{}{\\setlength{\\leftmargin}{3.1cm}\\setlength{\\labelwidth}{0pt}"
                "\\setlength{\\labelsep}{0pt}\\setlength{\\itemindent}{0pt}\\setlength{\\topsep}{0pt}\\setlength{\\parsep}{0pt}}\n\\item[]\\small\n")
    if c.summary:
        body.append("\\vspace{4pt}{\\color{ink!85}%s}\\par\n" % c.summary)
    body.append(c.sections("work", "projects", "skills", "education", "languages"))
    body.append("\\end{list}\n")
    return document(c, FONTS, GEOMETRY, MACROS, "".join(body))
