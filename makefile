invoices/%.tex: invoices/%.yml templates/invoice.tex bin/generate-invoice
	@echo "Building LaTeX $@"
	@bin/generate-invoice < $< > $@

invoices/%.pdf: invoices/%.tex
	@rm -rf .texbuild
	@mkdir .texbuild
	@echo "Building PDF $@"
	@texi2pdf -q --tidy --build-dir .texbuild $< -o $@
	@rm -f $<
	@rm -rf .texbuild
