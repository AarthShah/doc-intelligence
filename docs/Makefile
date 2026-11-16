# Minimal Makefile for Sphinx documentation
#

# Variables for Sphinx build
SPHINXBUILD   ?= sphinx-build
SOURCEDIR      = .
BUILDDIR       = _build

# Put your Sphinx build commands here
all: html

html:
	$(SPHINXBUILD) -b html $(SOURCEDIR) $(BUILDDIR)

clean:
	rm -rf $(BUILDDIR)
