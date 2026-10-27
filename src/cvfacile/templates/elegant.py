# SPDX-License-Identifier: AGPL-3.0-or-later
"""Centered, small caps and Garamond: a classic book-like look."""
from __future__ import annotations

from ..latex import escape
from .common import LABELS, Context, document  # noqa: F401

NAME = "elegant"
DESCRIPTION = "Centered layout, small caps and EB Garamond, ornamental section rules. No photo."

FONTS = r"\usepackage{ebgaramond}"
GEOMETRY = "margin=1.6cm,top=1.2cm,bottom=1.1cm"
MACROS = r"""
\newcommand{\cvmidrule}{{\color{accent}\leaders\hrule height 3.1pt depth -2.7pt\hfill}}
\newcommand{\cvsection}[1]{\par\vspace{5pt}\noindent\cvmidrule\quad{\large\scshape\color{accent}#1}\quad\cvmidrule\par\vspace{4pt}}
\newcommand{\cvjob}[4]{{\bfseries #1}\cvif{#2}{, \textit{#2}}\hfill{\itshape #4}\par\cvif{#3}{{\small\color{muted}\itshape #3}\par}\vspace{1pt}}
\newcommand{\cvproject}[4]{{\scshape\bfseries #1}\cvif{#2}{, \textit{#2}}\par{\small #4\cvif{#3}{ {\color{muted}\itshape(#3)}}}\par\vspace{4pt}}
\newcommand{\cvskill}[2]{{\small\hangindent=3.2cm\hangafter=1\makebox[3.2cm][l]{\scshape #1}#2\par}\vspace{1pt}}
\newcommand{\cvlang}[2]{#1\cvif{#2}{ \textit{(#2)}}}
\newcommand{\cvlangsep}{\enspace\textperiodcentered\enspace}
\newcommand{\cvedu}[4]{{\bfseries #1}\cvif{#2}{, \textit{#2}}\hfill{\itshape #4}\par\cvif{#3}{{\small\color{muted}\itshape #3}\par}\vspace{3pt}}
\newcommand{\cvcontact}[2]{#2}
\newcommand{\cvcontactsep}{\enspace\textperiodcentered\enspace}
\newenvironment{cvitems}{\small\begin{itemize}[labelsep=0.5em,leftmargin=1.2em,itemsep=1pt,parsep=0pt,topsep=2pt,label={\color{accent}\textendash}]}{\end{itemize}}
"""


def render(cv, lang, photo_file=None):
    c = Context(cv, lang, photo_file, accent="7F1D1D")
    body = ["\\begin{center}\n{\\fontsize{26}{30}\\selectfont\\scshape %s}\\par\\vspace{3pt}\n" % c.name]
    if c.label:
        body.append("{\\large\\itshape\\color{accent} %s}\\par\\vspace{5pt}\n" % c.label)
    body.append("%s\\par\\vspace{4pt}\n{\\color{accent}\\rule{\\linewidth}{0.8pt}}\\par\\vspace{-7.5pt}"
                "{\\color{accent}\\rule{\\linewidth}{0.3pt}}\n\\end{center}\n" % c.contacts())
    if c.summary:
        body.append("\\justifying{\\small %s}\\par\\raggedright\n" % c.summary)
    body.append(c.sections("work", "projects", "education", "skills"))
    if c.cv.get("languages"):
        body.append("\\cvsection{%s}\n\\begin{center}%s\\end{center}\n" % (escape(c.labels["languages"]), c.block("languages")))
    return document(c, FONTS, GEOMETRY, MACROS, "".join(body))
