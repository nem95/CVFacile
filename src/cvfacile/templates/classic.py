# SPDX-License-Identifier: AGPL-3.0-or-later
"""Single column, serif, centered header. Traditional and ATS-friendly."""
from __future__ import annotations

from .common import LABELS, Context, document  # noqa: F401  (LABELS is part of the template API)

NAME = "classic"
DESCRIPTION = "Single column, serif (XCharter), centered header. Traditional and ATS-friendly. No photo."

FONTS = r"\usepackage{XCharter}"
GEOMETRY = "margin=1.5cm,top=1.2cm,bottom=1.2cm"
MACROS = r"""
\newcommand{\cvsection}[1]{\par\vspace{7pt}{\color{accent}\large\bfseries\scshape #1}\par\vspace{1pt}%
  {\color{accent}\rule{\linewidth}{0.6pt}}\par\vspace{5pt}}
\newcommand{\cvjob}[4]{{\bfseries #1}\cvif{#2}{, \textit{#2}}\cvif{#3}{{\color{muted}, #3}}\hfill{\small\itshape #4}\par\vspace{1pt}}
\newcommand{\cvproject}[4]{{\bfseries #1}\cvif{#2}{ \textbar\ #2}\par{\small #4\cvif{#3}{ {\color{muted}\itshape(#3)}}}\par\vspace{3pt}}
\newcommand{\cvskill}[2]{{\small{\bfseries #1:} #2}\par\vspace{1pt}}
\newcommand{\cvlang}[2]{{\bfseries #1}\cvif{#2}{ (#2)}}
\newcommand{\cvlangsep}{\quad\textbullet\quad}
\newcommand{\cvedu}[4]{{\bfseries #1}\cvif{#2}{, #2}\cvif{#3}{{\color{muted}, #3}}\hfill{\small\itshape #4}\par\vspace{3pt}}
\newcommand{\cvcontact}[2]{{\color{accent}#1}~#2}
\newcommand{\cvcontactsep}{\quad}
\newenvironment{cvitems}{\small\begin{itemize}[labelsep=0.5em,leftmargin=1.3em,itemsep=1pt,parsep=0pt,topsep=2pt,label=\textendash]}{\end{itemize}}
"""


def render(cv, lang, photo_file=None):
    c = Context(cv, lang, photo_file, accent="1F3A5F")
    body = ["\\begin{center}\n{\\fontsize{24}{28}\\selectfont\\bfseries %s}\\par\\vspace{4pt}\n" % c.name]
    if c.label:
        body.append("{\\large\\color{muted} %s}\\par\\vspace{6pt}\n" % c.label)
    body.append("{\\small %s}\n\\end{center}\n" % c.contacts())
    if c.summary:
        body.append("\\justifying{\\small %s}\\par\\raggedright\n" % c.summary)
    body.append(c.sections("work", "projects", "education", "skills", "languages"))
    return document(c, FONTS, GEOMETRY, MACROS, "".join(body))
