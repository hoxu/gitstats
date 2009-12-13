PREFIX=/usr
BINDIR=$(PREFIX)/bin
RESOURCEDIR=$(PREFIX)/share/gitstats
RESOURCES=gitstats.css sortable.js *.gif
BINARIES=gitstats

all: help

help:
	@echo "Usage:"
	@echo
	@echo "make install                   # install to /usr"
	@echo "make install PREFIX=~     # install to ~"
	@echo

install:
	install -d $(BINDIR) $(RESOURCEDIR)
	install -v $(BINARIES) $(BINDIR)
	install -v -m 644 $(RESOURCES) $(RESOURCEDIR)

.PHONY: all help install
