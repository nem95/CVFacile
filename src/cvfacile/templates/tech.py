# SPDX-License-Identifier: AGPL-3.0-or-later
"""Developer look: monospace accents, Markdown-like headings, skills as tags."""
from __future__ import annotations

from .common import LABELS, Context, columns, document  # noqa: F401  (LABELS is part of the template API)

NAME = "tech"
DESCRIPTION = "Developer look: monospace accents, Markdown-like headings, skills shown as tags. No photo."

FONTS = r"\usepackage[default]{sourcesanspro}" "\n" r"\usepackage{sourcecodepro}"
GEOMETRY = "margin=1.4cm,top=1.1cm,bottom=1.1cm"
MACROS = r"""
\newcommand{\cvsection}[1]{\par\vspace{7pt}{\ttfamily\bfseries\color{accent}\#\#}\ {\bfseries\large #1}\par\vspace{5pt}}
\newcommand{\cvkw}[1]{\tikz[baseline=(t.base)]\node[fill=soft,rounded corners=2pt,inner xsep=3pt,inner ysep=1.2pt,
  font=\ttfamily\scriptsize,text=ink](t){#1};}
\newcommand{\cvkwsep}{\hskip 3pt plus 1pt\relax}
\newcommand{\cvjob}[4]{{\bfseries #1}\cvif{#2}{\ {\color{accent}@}\ {\bfseries\color{accent}#2}}\cvif{#3}{{\color{muted}, #3}}\hfill{\ttfamily\footnotesize\color{muted}#4}\par\vspace{1pt}}
\newcommand{\cvjobsep}{\vspace{5pt}}
\newcommand{\cvproject}[4]{{\bfseries #1}\cvif{#2}{{\color{muted}\ \textbar\ #2}}\par{\small #4}\cvif{#3}{\hskip 6pt #3}\par\vspace{3pt}}
\newcommand{\cvskill}[2]{\hangindent=3.2cm\hangafter=1\makebox[3.2cm][l]{\bfseries\small #1}#2\par\vspace{1pt}}
\newcommand{\cvlang}[2]{{\bfseries #1}\cvif{#2}{{\color{muted}\ -- #2}}}
\newcommand{\cvlangsep}{\par\vspace{2pt}}
\newcommand{\cvedu}[4]{{\bfseries #1}\par\cvif{#2}{{\small #2}\par}{\ttfamily\footnotesize\color{muted}#3\cvif{#3}{\cvif{#4}{ | }}#4}\par\vspace{4pt}}
\newcommand{\cvcontact}[2]{{\color{accent}#1}~#2}
\newcommand{\cvcontactsep}{\quad}
\newenvironment{cvitems}{\small\begin{itemize}[labelsep=0.5em,leftmargin=1.2em,itemsep=1pt,parsep=0pt,topsep=2pt,label={\ttfamily\color{accent}>}]}{\end{itemize}}
"""


def render(cv, lang, photo_file=None):
    c = Context(cv, lang, photo_file, accent="059669", soft="E6F4EE")
    body = ["{\\fontsize{26}{30}\\selectfont\\bfseries %s{\\color{accent}\\ttfamily\\_}}\\par\\vspace{4pt}\n" % c.name]
    if c.label:
        body.append("{\\ttfamily\\color{muted} // %s}\\par\n" % c.label)
    body.append("\\vspace{6pt}{\\small\\raggedright %s\\par}\\vspace{4pt}\n" % c.contacts())
    if c.summary:
        body.append("\\justifying{\\small %s\\par}\\raggedright\n" % c.summary)
    body.append(c.sections("skills", "work", "projects"))
    bottom = (c.section("education"), c.section("languages"))
    if all(bottom):
        body.append(columns(bottom[0], bottom[1], "0.58\\linewidth", "0.38\\linewidth"))
    else:
        body.append("".join(bottom))
    return document(c, FONTS, GEOMETRY, MACROS, "".join(body))
