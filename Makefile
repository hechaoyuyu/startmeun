#(c) StartOS 2010/11 <hechao@ivali.com>
#
# A simple makefile to allow installing/uninstalling 
# Part of the YMenu

PREFIX = /usr
AWNPREFIX = $(PREFIX)
CAIRODOCKPREFIX = $(PREFIX)
DOCKYPREFIX = $(PREFIX)
INSTALL_LOG = install.log
LIBDIR = $(PREFIX)/lib

.PHONY : install
.PHONY : uninstall

all:
	@echo "Makefile: Available actions: install, uninstall,"
	@echo "Makefile: Available variables: PREFIX, DESTDIR, AWNPREFIX, CAIRODOCKPREFIX"
	
# install
install:

	-install -d $(DESTDIR)/etc/ymenu $(DESTDIR)$(PREFIX)/bin/ $(DESTDIR)$(LIBDIR) \
	$(DESTDIR)$(PREFIX)/share $(DESTDIR)$(LIBDIR)/bonobo/servers 
	@echo $(PREFIX) > $(DESTDIR)/etc/ymenu/prefix
	python -u local.py
	
	-cp -r src/lib/ymenu $(DESTDIR)$(LIBDIR)
	-cp -r src/share/ymenu $(DESTDIR)$(PREFIX)/share
	-cp -r src/share/locale $(DESTDIR)$(PREFIX)/share
	-install src/bin/ymenu $(DESTDIR)$(PREFIX)/bin/
	-install src/lib/bonobo/ymenu.server $(DESTDIR)$(LIBDIR)/bonobo/servers
	@echo "Makefile: YMenu installed."


# uninstall
uninstall:

	rm -rf $(LIBDIR)/ymenu
	rm -rf $(PREFIX)/share/ymenu
	rm -rf $(PREFIX)/bin/ymenu
	rm -rf $(LIBDIR)/bonobo/servers/ymenu.server
	rm -rf /etc/ymenu/prefix
	


