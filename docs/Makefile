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
	@echo "\tbuild -- build the documentation."
	@echo "\tfresh -- Clean previous builds and genereated documents; then rebuild."
	@echo "\twipe  -- Wipe out built documentation."

build: api html

fresh: clean build

api:
	$(APIBUILD) -TefM --templatedir $(TEMPLATEDIR) -o $(APIDIR) $(PKGDIR)

html:
	$(SPHINXBUILD) -b html $(SOURCEDIR) $(BUILDDIR)/html $(SPHINXOPTS) 

wipe:
	rm -rf build/*

clean: wipe
	rm -rf source/generated/api/*
