%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Medium Length Professional CV - RESUME CLASS FILE
%
% This template has been downloaded from:
% http://www.LaTeXTemplates.com
%
% This class file defines the structure and design of the template. 
%
% Original header:
% Copyright (C) 2010 by Trey Hunner
%
% Copying and distribution of this file, with or without modification,
% are permitted in any medium without royalty provided the copyright
% notice and this notice are preserved. This file is offered as-is,
% without any warranty.
%
% Created by Trey Hunner and modified by www.LaTeXTemplates.com
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\ProvidesClass{resume}[2010/07/10 v0.9 Resume class]

\LoadClass[11pt,letterpaper]{article} % Font size and paper type
\usepackage[default]{sourcesanspro}
\usepackage[parfill]{parskip} % Remove paragraph indentation
\usepackage{array} % Required for boldface (\bf and \bfseries) tabular columns
\usepackage{ifthen} % Required for ifthenelse statements
\usepackage{xcolor}

\definecolor{headerprimary}{HTML}{3A3A3A}
\definecolor{headeraccent}{HTML}{2C6E91}
\definecolor{headermuted}{HTML}{666666}
\definecolor{sectionrule}{HTML}{C8D4E0}

\usepackage{hyperref}
\hypersetup{
    colorlinks=true,
    linkcolor=black,
    filecolor=black,
    urlcolor=black,
    pdfborder={0 0 0},
}

\pagestyle{empty} % Suppress page numbers

%----------------------------------------------------------------------------------------
%	HEADINGS COMMANDS: Commands for printing name and address
%----------------------------------------------------------------------------------------

\def \name#1{\def\@name{#1}} % Defines the \name command to set name
\def \@name {} % Sets \@name to empty by default
\def \headline#1{\def\@headline{#1}} % Defines an optional headline below the name
\def \@headline {} % Sets \@headline to empty by default

\def \addressSep {\hspace{0.55em}{\color{headermuted}\textbar}\hspace{0.55em}} % Compact separator for header details

% One, two or three address lines can be specified 
\def \@addressone {}
\def \@addresstwo {}
\def \@addressthree {}

% \address command can be used to set the first, second, and third address (last 2 optional)
\def \address #1{
  \ifx\@addressone\@empty
    \def \@addressone {#1}
  \else\ifx\@addresstwo\@empty
    \def \@addresstwo {#1}
  \else
    \def \@addressthree {#1}
  \fi\fi
}

% \printaddress is used to style an address line (given as input)
\def \printaddress #1{
  \begingroup
    \def \\ {\addressSep}
    \noindent{\contactsize\color{headermuted}#1\par}
  \endgroup
  \addressskip
}

% \printname is used to print the name as a page header
\def \printname {
  \begingroup
    \noindent{\namesize\bfseries\color{headerprimary}\@name\par}
    \nameskip
  \endgroup
}

% \printheadline prints an optional professional headline below the name
\def \printheadline {
  \ifx\@headline\@empty\else
    \begingroup
      \noindent{\small\color{headeraccent}\@headline\par}
      \vspace{0.15em}
    \endgroup
  \fi
}

%----------------------------------------------------------------------------------------
%	PRINT THE HEADING LINES
%----------------------------------------------------------------------------------------

\let\ori@document=\document
\renewcommand{\document}{
  \ori@document  % Begin document
  \printname % Print the name specified with \name
  \printheadline % Print the optional headline if specified
  \ifx\@addressone\@empty\else \printaddress{\@addressone}\fi
  \ifx\@addresstwo\@empty\else \printaddress{\@addresstwo}\fi
  \ifx\@addressthree\@empty\else \printaddress{\@addressthree}\fi
  \vspace{0.45em}
}

%----------------------------------------------------------------------------------------
%	SECTION FORMATTING
%----------------------------------------------------------------------------------------

% Defines the rSection environment for the large sections within the CV
\newenvironment{rSection}[1]{ % 1 input argument - section name
  \sectionskip
  \MakeUppercase{{\bf #1}} % Section title
  \sectionlineskip
  {\color{sectionrule}\hrule height 0.8pt} % Horizontal line
  \begin{list}{}{ % List for each individual item in the section
    \setlength{\leftmargin}{0em} % Margin within the section
  }
  \item[]
}{
  \end{list}
}

%----------------------------------------------------------------------------------------
%	WORK EXPERIENCE FORMATTING
%----------------------------------------------------------------------------------------

\newenvironment{rSubsection}[4]{ % 4 input arguments - company name, year(s) employed, job title and location
 {\bf #1} \hfill {#2} % Bold company name and date on the right
 \ifthenelse{\equal{#3}{}}{}{ % If the third argument is not specified, don't print the job title and location line
  \\
  {\em #3} \hfill {\em #4} % Italic job title and location
  }\smallskip
  \begin{list}{$\cdot$}{\leftmargin=0em} % \cdot used for bullets, no indentation
   \itemsep -0.5em \vspace{-0.5em} % Compress items in list together for aesthetics
  }{
  \end{list}
  \vspace{0.5em} % Some space after the list of bullet points
}

% The below commands define the whitespace after certain things in the document - they can be \smallskip, \medskip or \bigskip
\def\namesize{\fontsize{28}{26}\selectfont} % Size of the name at the top of the document
\def\contactsize{\small} % Size of the contact details in the header
\def\addressskip{\vspace{0.04em}} % The space between the two address (or phone/email) lines
\def\sectionlineskip{\medskip} % The space above the horizontal line for each section 
\def\nameskip{\vspace{0.12em}} % The space after your name at the top
\def\sectionskip{\medskip} % The space after the heading section
