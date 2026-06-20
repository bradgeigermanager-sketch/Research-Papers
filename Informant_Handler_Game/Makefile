# Simple Makefile for Informant_Handler_Game

TEXMAIN = main
LATEX   = pdflatex
BIBTEX  = bibtex

all: $(TEXMAIN).pdf

$(TEXMAIN).pdf: $(TEXMAIN).tex sections/*.tex macros.tex references.bib
    $(LATEX) $(TEXMAIN)
    $(BIBTEX) $(TEXMAIN) || true
    $(LATEX) $(TEXMAIN)
    $(LATEX) $(TEXMAIN)

clean:
    rm -f *.aux *.bbl *.blg *.log *.out *.toc *.lof *.lot

distclean: clean
    rm -f $(TEXMAIN).pdf
