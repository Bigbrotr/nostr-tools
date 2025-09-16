# Minimal makefile for Sphinx documentation

SPHINXOPTS    ?=
SPHINXBUILD  ?= sphinx-build
SOURCEDIR    = .
BUILDDIR     = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# =====================================================
# Essential custom targets
# =====================================================

# Build and open in browser
open: html
	@echo "Opening documentation in browser..."
	@if command -v xdg-open >/dev/null 2>&1; then \
		xdg-open "$(BUILDDIR)/html/index.html"; \
	elif command -v open >/dev/null 2>&1; then \
		open "$(BUILDDIR)/html/index.html"; \
	else \
		echo "Please open $(BUILDDIR)/html/index.html manually"; \
	fi

# Serve documentation locally
serve: html
	@echo "Serving at http://localhost:8000"
	@cd $(BUILDDIR)/html && python3 -m http.server 8000

# Auto-rebuild on changes (requires sphinx-autobuild)
watch:
	@if command -v sphinx-autobuild >/dev/null 2>&1; then \
		sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)/html" --port 8000; \
	else \
		echo "sphinx-autobuild not found. Install with: pip install sphinx-autobuild"; \
	fi

# Clean everything
clean-all:
	rm -rf $(BUILDDIR)/*
