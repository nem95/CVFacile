# SPDX-License-Identifier: AGPL-3.0-or-later
"""Dense single column with small margins: fits a lot on one page."""
from __future__ import annotations

from .common import LABELS, Context, document  # noqa: F401  (LABELS is part of the template API)

NAME = "compact"
DESCRIPTION = "Dense single column with small margins, for long careers. Libertinus serif. No photo."

FONTS = r"\usepackage{libertinus}"
GEOMETRY = "margin=1.2cm,top=1.1cm"
MACROS = r"""
\newcommand{\cvsection}[1]{\par\vspace{6pt}\leavevmode{\color{accent}\bfseries\scshape #1}\ {\color{accent!40}\hrulefill}\par\vspace{3pt}}
\newcommand{\cvjob}[4]{{\bfseries #1}\cvif{#2}{ \textbullet\ {\color{accent}#2}}\cvif{#3}{{\color{muted}, #3}}\hfill{\small\color{muted}#4}\par}
\newcommand{\cvjobsep}{\vspace{3pt}}
\newcommand{\cvproject}[4]{{\bfseries #1}\cvif{#2}{ {\color{muted}(#2)}}: #4\cvif{#3}{ {\small\color{muted}\itshape[#3]}}\par\vspace{2pt}}
\newcommand{\cvskill}[2]{{\bfseries #1:} #2\par}
\newcommand{\cvlang}[2]{{\bfseries #1}\cvif{#2}{ (#2)}}
\newcommand{\cvlangsep}{\ \textbullet\ }
\newcommand{\cvedu}[4]{{\bfseries #1}\cvif{#2}{, #2}\cvif{#3}{{\color{muted}, #3}}\hfill{\small\color{muted}#4}\par}
\newcommand{\cvcontact}[2]{#2~{\color{accent}#1}}
\newcommand{\cvcontactsep}{\par}
\newenvironment{cvitems}{\begin{itemize}[labelsep=0.5em,leftmargin=1em,itemsep=0pt,parsep=0pt,topsep=1pt,label={\color{accent}\small\textbullet}]}{\end{itemize}}
"""


def render(cv, lang, photo_file=None):
    c = Context(cv, lang, photo_file, accent="0F4C81")
    body = ["\\noindent\\begin{minipage}[b]{0.6\\linewidth}\n{\\fontsize{24}{28}\\selectfont\\bfseries %s}\\par\n" % c.name]
    if c.label:
        body.append("\\vspace{2pt}{\\large\\color{accent} %s}\n" % c.label)
    body.append("\\end{minipage}\\hfill\\begin{minipage}[b]{0.38\\linewidth}\\raggedleft\\small\n%s\n\\end{minipage}\\par\n" % c.contacts())
    body.append("\\vspace{4pt}{\\color{accent}\\rule{\\linewidth}{1pt}}\\par\\vspace{2pt}\n")
    if c.summary:
        body.append("\\justifying %s\\par\\raggedright\n" % c.summary)
    body.append(c.sections("work", "projects", "skills", "education", "languages"))
    return document(c, FONTS, GEOMETRY, MACROS, "".join(body))
