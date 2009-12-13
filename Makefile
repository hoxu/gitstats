PREFIX=/usr
BINDIR=$(PREFIX)/bin
RESOURCEDIR=$(PREFIX)/share/gitstats
RESOURCES=gitstats.css sortable.js *.gif
BINARIES=gitstats
VERSION=$(shell git rev-parse --short HEAD)

all: help

help:
	@echo "Usage:"
	@echo
	@echo "make install                   # install to /usr"
	@echo "make install PREFIX=~          # install to ~"
	@echo "make release [VERSION=foo]     # make a release tarball"
	@echo

install:
	install -d $(BINDIR) $(RESOURCEDIR)
	install -v $(BINARIES) $(BINDIR)
	install -v -m 644 $(RESOURCES) $(RESOURCEDIR)

release:
	@tar --owner=0 --group=0 --transform 's!^!gitstats/!' -zcf gitstats-$(VERSION).tar.gz $(BINARIES) $(RESOURCES) doc/ Makefile

.PHONY: all help install release
