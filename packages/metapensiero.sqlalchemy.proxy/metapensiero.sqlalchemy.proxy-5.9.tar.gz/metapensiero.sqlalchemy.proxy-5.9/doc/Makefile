# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.proxy -- Makefile for Sphinx documentation
# :Created:   ven 30 dic 2016 18:35:57 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
PAPER         =
BUILDDIR      = _build

ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(SPHINXOPTS) .

.PHONY: clean
clean:
	@rm -rf $(BUILDDIR)/*

.PHONY: html
html:
	@$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html
