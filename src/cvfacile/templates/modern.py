# SPDX-License-Identifier: AGPL-3.0-or-later
"""Full-width colored header band, then a main column and a side column."""
from __future__ import annotations

from .common import LABELS, Context, document, paracol, photo_circle  # noqa: F401  (LABELS is part of the template API)

NAME = "modern"
DESCRIPTION = "Colored header band with photo, main column and side column. Source Sans."

FONTS = r"\usepackage[default]{sourcesanspro}" "\n" r"\usepackage{paracol}"
GEOMETRY = "left=1.6cm,right=1.6cm,top=1.2cm,bottom=1.2cm"
MACROS = r"""
\newcommand{\cvsection}[1]{\par\vspace{8pt}{\color{accent}\bfseries\large\MakeUppercase{#1}}\par\vspace{3pt}%
  {\color{accent}\rule{1.4cm}{2pt}}\par\vspace{5pt}}
\newcommand{\cvjob}[4]{{\bfseries #1}\par{\color{accent}\bfseries #2}\cvif{#3}{{\color{muted}\ \textbullet\ #3}}%
  \hfill{\small\color{muted}#4}\par\vspace{2pt}}
\newcommand{\cvjobsep}{\vspace{5pt}}
\newenvironment{cvitems}{\small\begin{itemize}[labelsep=0.5em,leftmargin=1.1em,itemsep=1pt,parsep=0pt,topsep=1pt,label={\color{accent}\textbullet}]}{\end{itemize}}
\newcommand{\cvproject}[4]{{\bfseries #1}\cvif{#2}{{\color{accent}\ \textbar\ #2}}\par{\small #4}\par%
  \cvif{#3}{{\footnotesize\color{muted}#3}\par}\vspace{5pt}}
\newcommand{\cvskill}[2]{{\bfseries\small #1}\par{\small #2}\par\vspace{5pt}}
\newcommand{\cvlang}[2]{{\small\bfseries #1}\cvif{#2}{{\small\color{muted}\ -- #2}}}
\newcommand{\cvlangsep}{\par\vspace{2pt}}
\newcommand{\cvedu}[4]{{\small\bfseries #1}\par\cvif{#2}{{\footnotesize\color{accent}#2}\par}%
  {\footnotesize\color{muted}#3\cvif{#3}{\cvif{#4}{ \textbullet\ }}#4}\par\vspace{5pt}}
\newcommand{\cvcontact}[2]{#1~#2}
\newcommand{\cvcontactsep}{\quad}
"""


def render(cv, lang, photo_file=None):
    c = Context(cv, lang, photo_file, accent="0F766E")
    photo = photo_circle(c, 1.4, "white, line width=2pt")
    width = "\\dimexpr\\linewidth-3.6cm\\relax" if photo else "\\linewidth"
    body = [
        "\\begin{tikzpicture}[remember picture,overlay]\n"
        "\\fill[accent] (current page.north west) rectangle ([yshift=-4.6cm]current page.north east);\n"
        "\\end{tikzpicture}%\n",
        "\\noindent\\begin{minipage}[t][3.4cm][c]{\\linewidth}\\color{white}\n",
        "\\begin{minipage}{%s}\n{\\fontsize{30}{34}\\selectfont\\bfseries %s}\\par\\vspace{4pt}\n" % (width, c.name),
    ]
    if c.label:
        body.append("{\\Large %s}\\par\\vspace{8pt}\n" % c.label)
    body.append("{\\small\\raggedright %s\\par}\n\\end{minipage}" % c.contacts())
    if photo:
        body.append("\\hfill\n" + photo)
    body.append("\n\\end{minipage}\\par\\vspace{0.7cm}\n")
    if c.summary:
        body.append("\\justifying{\\small %s\\par}\\raggedright\n" % c.summary)
    body.append(paracol(c.sections("work", "projects"), c.sections("skills", "languages", "education"), 0.67))
    return document(c, FONTS, GEOMETRY, MACROS, "".join(body))
