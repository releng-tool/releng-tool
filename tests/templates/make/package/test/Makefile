.PHONY: all
all:

ifndef ROOT_DIR
$(error 'ROOT_DIR' is not set)
endif

.PHONY: configure
configure:
	touch $(ROOT_DIR)/test-make-configure

.PHONY: build
build:
	touch $(ROOT_DIR)/test-make-build
all: build

.PHONY: install
install:
	test $(DESTDIR)
	touch $(DESTDIR)/test-make-install
