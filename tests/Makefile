# project dir
PJDIR = $(abspath ../)
$(shell cd ..)
CURDIR=$(abspath .)
test:
	nosetests-2.7 --config=$(CURDIR)/setup.cfg  \
		--verbose \
		--with-xunit \
		--cov-report=html \
		--cov-report=xml \
		--xunit-file=$(CURDIR)/reports/nosetests.xml \
		--cov=$(PJDIR) \
		--cov-config=$(CURDIR)/.coveragerc

# clean report
.PHONY: clean
clean:
	rm -rf $(CURDIR)/reports/*
