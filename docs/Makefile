# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
APIBUILD			= sphinx-apidoc
SOURCEDIR     = source
APIDIR				= $(SOURCEDIR)/generated/api
BUILDDIR      = build
TEMPLATEDIR		= source/_templates
PKGDIR				= ../src/comsar

help:
	@echo "Use \`make <target>' with one of the following:"
	@echo "\thtml  -- build the documentation in HTML."
	@echo "\tfresh -- Clean previous builds then rebuild."

html:
	$(SPHINXBUILD) -b html $(SOURCEDIR) $(BUILDDIR)/html $(SPHINXOPTS) 

fresh: clean html

clean:
	rm -rf build/*

# api:
#    $(APIBUILD) -TefM --templatedir $(TEMPLATEDIR) -o $(APIDIR) $(PKGDIR)
