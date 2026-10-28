# SPDX-License-Identifier: AGPL-3.0-or-later
"""Experience shown as a vertical timeline, dates in the left margin."""
from __future__ import annotations

from .common import LABELS, Context, document, photo_circle  # noqa: F401  (LABELS is part of the template API)

NAME = "timeline"
DESCRIPTION = "Experience as a vertical timeline with dates in the margin. Fira Sans, optional photo."

FONTS = r"\usepackage[sfdefault]{FiraSans}"
GEOMETRY = "margin=1.4cm,top=1.2cm,bottom=1.1cm"
MACROS = r"""
\newcommand{\cvmargin}[1]{\leavevmode\llap{\parbox[t]{2.3cm}{\raggedleft\leavevmode\footnotesize\color{muted}#1}\hspace{0.85cm}}}
\newcommand{\cvsection}[1]{\par\vspace{8pt}\leavevmode\hspace*{-3.2cm}{\color{accent}\bfseries\large\MakeUppercase{#1}}\par\vspace{5pt}}
\newsavebox{\cvbox}
\newlength{\cvh}
\newenvironment{cventry}[1]{\def\cvdates{#1}\begin{lrbox}{\cvbox}\begin{minipage}[t]{\linewidth}}{\end{minipage}\end{lrbox}%
  \setlength{\cvh}{\dimexpr\ht\cvbox+\dp\cvbox\relax}%
  \par\noindent\cvmargin{\cvdates}%
  \tikz[overlay]{\draw[accent!35,line width=1.2pt] (-0.45cm,0.1cm) -- ++(0,-\cvh-6pt);
    \fill[white] (-0.45cm,0.1cm) circle (4.2pt); \fill[accent] (-0.45cm,0.1cm) circle (3pt);}%
  \usebox{\cvbox}\par}
\newcommand{\cvjob}[4]{{\bfseries #1}\par{\color{accent}\bfseries\small #2}\cvif{#3}{{\small\color{muted}\ \textbullet\ #3}}\par\vspace{1pt}}
\newcommand{\cvjobsep}{\vspace{6pt}}
\newcommand{\cvproject}[4]{{\bfseries #1}\cvif{#2}{{\color{muted}\ \textbar\ #2}}\par #4\cvif{#3}{ {\footnotesize\color{muted}(#3)}}\par\vspace{3pt}}
\newcommand{\cvskill}[2]{{\bfseries #1:} #2\par\vspace{1pt}}
\newcommand{\cvlang}[2]{{\bfseries #1}\cvif{#2}{{\color{muted}\ (#2)}}}
\newcommand{\cvlangsep}{\quad\textbullet\quad}
\newcommand{\cvedu}[4]{\cvmargin{#4}{\bfseries #1}\par\cvif{#2}{{\color{accent}#2}\cvif{#3}{{\color{muted}, #3}}\par}\vspace{3pt}}
\newcommand{\cvcontact}[2]{{\color{accent}#1}~#2}
\newcommand{\cvcontactsep}{\quad}
"""


def render(cv, lang, photo_file=None):
    c = Context(cv, lang, photo_file, accent="7C3AED")
    c.job_env = "cventry"
    photo = photo_circle(c, 1.25, "accent, line width=1.5pt")
    width = "\\dimexpr\\linewidth-3.2cm\\relax" if photo else "\\linewidth"
    body = ["\\noindent\\begin{minipage}[c]{%s}\n{\\fontsize{28}{32}\\selectfont\\bfseries %s \\textcolor{accent}{%s}}\\par\\vspace{4pt}\n"
            % (width, c.first, c.last)]
    if c.label:
        body.append("{\\large\\color{muted} %s}\\par\n" % c.label)
    body.append("\\vspace{6pt}{\\small\\raggedright %s\\par}\n\\end{minipage}" % c.contacts())
    if photo:
        body.append("\\hfill\n" + photo)
    body.append("\\par\\vspace{6pt}\n")
    if c.summary:
        body.append("\\justifying{\\small %s\\par}\\raggedright\n" % c.summary)
    body.append("\\begin{list}{}{\\setlength{\\leftmargin}{3.2cm}\\setlength{\\labelwidth}{0pt}"
                "\\setlength{\\labelsep}{0pt}\\setlength{\\itemindent}{0pt}\\setlength{\\topsep}{0pt}\\setlength{\\parsep}{0pt}}\n\\item[]\\small\n")
    body.append(c.sections("work", "projects", "education", "skills", "languages"))
    body.append("\\end{list}\n")
    return document(c, FONTS, GEOMETRY, MACROS, "".join(body))
