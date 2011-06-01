#!/usr/bin/env python

import gtk
import os
import gobject
import Globals
import xdg.BaseDirectory as bd


Icontype = ["png", "xpm", "svg"]

try:
	INSTALL_PREFIX = open("/etc/ymenu/prefix").read()[:-1]
except:
	INSTALL_PREFIX = '/usr'

import gettext
gettext.textdomain('ymenu')
gettext.install('ymenu', INSTALL_PREFIX +  '/share/locale')
gettext.bindtextdomain('ymenu', INSTALL_PREFIX +  '/share/locale')

def _(s):
	return gettext.gettext(s)

def GetSystemIcon(icon):
	for n in Icontype:
		icon = str(icon).replace('.' + n,'')
	ico = Globals.GtkIconTheme.lookup_icon(icon,96,gtk.ICON_LOOKUP_FORCE_SVG)
	if ico:
		ico = ico.get_filename()
	else:
		ico = None
	return ico

class IconFactory(gobject.GObject):
	__gsignals__ = {"icons-changed" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        }
	def __init__(self):
		gobject.GObject.__init__(self)

		##### looksup icon theme in gtk, we could also use : gconf.client_get_default().get_string('/desktop/gnome/interface/icon_theme')
		self.gtkicontheme = gtk.icon_theme_get_default()
		self.icontheme = Globals.DefaultIconTheme
		self.old_icontheme = self.icontheme
		###### Check if icon theme is stored in cache#################
		#self.LoadIconCache()


	def Icon_change(self):
		"""Icons have changed"""

		print 'icons changed'
		self.icontheme = gtk.settings_get_default().get_property("gtk-icon-theme-name")
		self.gtkicontheme = gtk.icon_theme_get_default()

	def getgicon(self,gico):
		"""Returns gio icon"""
		try:
			names = gico.get_names()
			for x in range(0,len(names)):
				if self.gtkicontheme.has_icon(names[x]):
					return names[x]
		except:pass
		return 'gtk-execute'

	def geticonfile(self,icon):
			if self.gtkicontheme.has_icon(icon):
				pix = self.gtkicontheme.load_icon(icon,Globals.PG_iconsize,gtk.ICON_LOOKUP_FORCE_SIZE)
				return pix
			# lockup icon in xdg icon theme
			else:
				for dir_ in bd.xdg_data_dirs:
					for subdir in ('pixmaps', 'icons'):
						path = os.path.join(dir_, subdir, icon)
						if os.path.isfile(path):
							pix = gtk.gdk.pixbuf_new_from_file_at_size(path,Globals.PG_iconsize,Globals.PG_iconsize)
							return pix
			if os.path.isfile(icon):
				pix = gtk.gdk.pixbuf_new_from_file_at_size(icon, Globals.PG_iconsize, Globals.PG_iconsize)
				return pix
			pix = self.gtkicontheme.load_icon('gtk-missing-image',Globals.PG_iconsize,gtk.ICON_LOOKUP_FORCE_SIZE)
			return pix


