#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import os
import gconf
import sys
import pango
import Globals
if len(sys.argv) == 2 and sys.argv[1] == "--welcome":
	Globals.FirstUse = True
import xml.dom.minidom
import backend

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


class YMenuSettings:


	def delete(self, widget, event=None):
		gtk.main_quit()
		return False

	def __init__(self):
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_title(_('YMenu Settings'))
		self.window.set_icon(gtk.gdk.pixbuf_new_from_file(Globals.Applogo))
		self.window.connect("delete_event", self.delete)
		self.window.set_border_width(4)
		self.folder = os.environ['HOME']
		self.notebook = gtk.Notebook()
		self.vbox = gtk.VBox()
		self.vbox.pack_start(self.notebook, True, True)
		self.window.add(self.vbox)
		self.window.set_position(gtk.WIN_POS_CENTER)
		self.notebook.show()
		# TAB 1
		self.add_theme_tab()
		# TAB 2
		self.add_preferences_tab()
		# TAB4
		self.add_about_tab()
		self.hbox1 = gtk.HBox()
		self.vbox.pack_end(self.hbox1, False, False)
		self.button1 = gtk.Button(_('Ok'))
		self.button1.connect("clicked", self.buttonpress,'ok')
		self.button2 = gtk.Button(_('Apply'))
		self.button2.connect('clicked', self.buttonpress,'apply')
		self.button3 = gtk.Button(_('Cancel'))
		self.button3.connect('clicked', self.buttonpress,'cancel')
		self.hbox1.pack_start(self.button3, True, True)
		self.hbox1.pack_end(self.button1, True, True)
		self.label_tab1 = gtk.Label(_('Themes'))
		self.label_tab2 = gtk.Label(_('Preferences'))
		self.label_tab3 = gtk.Label(_('About'))
		self.notebook.append_page(self.vbox_theme,self.label_tab1)
		self.notebook.append_page(self.vbox_prefs,self.label_tab2)
		self.notebook.append_page(self.vbox_about,self.label_tab3)
		self.window.show_all()
		if self.window.size_request()[1] +50 > gtk.gdk.screen_height():
			self.notebook.set_tab_pos(0)
		if len(sys.argv) == 2 and sys.argv[1] == "--about":
			self.notebook.set_current_page(2)


	def add_theme_tab(self):

		self.vbox_theme = gtk.VBox()
		self.vbox_theme2 = gtk.VBox()
		self.hbox_theme = gtk.HBox()

		# MENU 
		self.frame_menu = gtk.Frame('<b>%s</b>' % _('Menu Selection'))
		self.frame_menu.get_label_widget().set_use_markup(1)
		self.vbox_theme.pack_start(self.frame_menu,True,True)
		self.vbox_theme.pack_start(self.vbox_theme2,False,False)
		self.vbox_theme2.pack_start(self.hbox_theme, False,False)
		self.hbox_menu = gtk.HBox()
		self.vbox_menu = gtk.VBox()
		self.vbox_menu3 = gtk.VBox()
		self.frame_menu.add(self.vbox_menu)
		self.image_menu = gtk.Image()

		self.vbox_menu.set_border_width(10)
		self.hbox_menu.pack_start(self.image_menu, True, True)
		self.hbox_menu.pack_start(self.vbox_menu3, 1,1)
	
		self.vbox_menu.pack_start(self.hbox_menu, True, True)
		
		self.combo_menu = gtk.combo_box_new_text()
		
		self.vbox_menu3.pack_start(self.combo_menu, 1,0)
		self.reload_themes('Menu')
		self.redraw_image(self.combo_menu,'Menu')
		self.combo_menu.connect("changed",self.redraw_image, 'Menu')

		# BUTTON
		self.frame_button = gtk.Frame('<b>%s</b>' % _('Button Selection'))
		self.frame_button.get_label_widget().set_use_markup(1)
		self.hbox_theme.pack_start(self.frame_button,True,True)
		self.vbox_button = gtk.VBox()
		self.image_button = gtk.Image()
		self.label_credits_button = gtk.Label()
		self.label_credits_button.set_size_request(10,10)
		self.label_credits_button.set_line_wrap(True)
		self.hbox_button = gtk.HBox()
		self.hbox_button.pack_start(self.image_button, True, True)
		self.hbox_button.pack_start(self.label_credits_button, True, True)
		self.vbox_button.pack_start(self.hbox_button, True, True)
		self.vbox_button.set_border_width(6)
		self.hbox_button2 = gtk.HBox()
		self.combo_button = gtk.combo_box_new_text()
		self.hbox_button2.pack_start(self.combo_button, True, True)
		self.reload_themes('Button')
		self.redraw_image(self.combo_button,'Button')
		self.combo_button.connect("changed",self.redraw_image, 'Button')
		self.vbox_button.pack_start(self.hbox_button2, False, False)
		self.frame_button.add(self.vbox_button)
		self.image_button.set_size_request(64,64)

		#ICON
		self.frame_icon = gtk.Frame('<b>%s</b>' % _('Icon Selection'))
		self.frame_icon.get_label_widget().set_use_markup(1)
		self.hbox_theme.pack_start(self.frame_icon, True,True)
		self.vbox_icon = gtk.VBox()
		self.image_icon = gtk.Image()
		self.hbox_icon = gtk.HBox()
		self.hbox_icon.pack_start(self.image_icon, True, True)
		self.vbox_icon.pack_start(self.hbox_icon, True, True)
		self.vbox_icon.set_border_width(6)
		self.hbox_icon2 = gtk.HBox()
		self.combo_icon = gtk.combo_box_new_text()
		self.hbox_icon2.pack_start(self.combo_icon, True, True)
		self.reload_themes('Icon')
		self.redraw_image(self.combo_icon,'Icon')
		self.combo_icon.connect("changed",self.redraw_image, 'Icon')
		self.vbox_icon.pack_start(self.hbox_icon2, False, False)
		self.frame_icon.add(self.vbox_icon)
		self.image_icon.set_size_request(64,64)

		#SOUND
                self.frame_sound = gtk.Frame('<b>%s</b>' % _('Sound theme'))
                self.frame_sound.get_label_widget().set_use_markup(1)
                self.hbox_theme.pack_start(self.frame_sound, True,True)
                self.vbox_sound = gtk.VBox()
                self.image_sound = gtk.Image()
                self.hbox_sound = gtk.HBox()
		self.hbox_sound.pack_start(self.image_sound, True, True)
		self.vbox_sound.pack_start(self.hbox_sound, True, True)
		self.vbox_sound.set_border_width(6)
		self.hbox_sound2 = gtk.HBox()
                self.combo_sound = gtk.combo_box_new_text()
		self.hbox_sound2.pack_start(self.combo_sound, True, True)
                self.reload_themes('Sound')
		self.redraw_image(self.combo_sound,'Sound')
                self.combo_sound.connect("changed",self.redraw_image, 'Sound')
                self.vbox_sound.pack_start(self.hbox_sound2, False, False)
		self.frame_sound.add(self.vbox_sound)
		self.image_sound.set_size_request(64,64)                

	def add_preferences_tab(self):

		self.vbox_prefs = gtk.VBox()
		self.vbox_prefs.set_border_width(10)
		self.check1 = gtk.CheckButton(_('Bind keyboad key'))
		self.hbox_check1 = gtk.HBox()
		self.entry_check1 = gtk.Entry()
		self.entry_check1.set_text(Globals.Settings['Bind_Key'])		
		self.hbox_check1.pack_start(self.check1,1,1)
		self.hbox_check1.pack_end(self.entry_check1,1,1)
		self.check1.set_active(int(Globals.Settings['SuperL']))
		#self.check3 = gtk.CheckButton(_('Use Gtk Theme Colors in Program List'))
		#self.check3.set_active(int(Globals.Settings['GtkColors']))
		self.check4 = gtk.CheckButton(_('Tab Selection on Mouse Hover'))
		self.check4.set_active(int(Globals.Settings['TabHover']))
		self.hbox12 = gtk.HBox()
		self.hbox13 = gtk.HBox()
		self.hbox16 = gtk.HBox()
		self.label11 = gtk.Label(_('Icon Size in Program List'))
		self.label11.set_justify(gtk.JUSTIFY_LEFT)
		self.label12 = gtk.Label(_('Number of Items in Recent Items List'))
		self.label12.set_justify(gtk.JUSTIFY_LEFT)
		self.spinbutton1 = gtk.SpinButton()
		self.spinbutton1.set_digits(1)
		self.spinbutton1.set_increments(1, int(256))
		self.spinbutton1.set_range(16, 256)
		self.spinbutton1.set_value(Globals.Settings['IconSize'])
		self.spinbutton2 = gtk.SpinButton()
		self.spinbutton2.set_digits(1)
		self.spinbutton2.set_increments(1, int(100))
		self.spinbutton2.set_range(1, 50)
		self.spinbutton2.set_value(Globals.Settings['ListSize'])
		
		self.label14 = gtk.Label(_('Tab hover effect'))
		self.combo6 = gtk.combo_box_new_text()
		self.combo6.append_text(_('None'))
		self.combo6.append_text(_('Grow'))
		self.combo6.append_text(_('Black and White'))
		self.combo6.append_text(_('Blur'))
		self.combo6.append_text(_('Glow'))
		self.combo6.append_text(_('Saturate'))
		self.combo6.set_active(Globals.Settings['Tab_Efect'])

		self.check7 = gtk.CheckButton(_('Show tooltips in program list'))
		self.check7.set_active(int(Globals.Settings['Show_Tips']))

		self.hbox12.pack_start(self.spinbutton1, False, False)
		self.hbox12.pack_start(self.label11, False,False,10)
		self.hbox13.pack_start(self.spinbutton2, False, False)
		self.hbox13.pack_start(self.label12, False, False,10)

		self.hbox16.pack_start(self.combo6, False, False)
		self.hbox16.pack_start(self.label14, False, False,10)

		#self.vbox_prefs.pack_start(self.hbox_check1, False, False,3)
		
		#self.vbox_prefs.pack_start(self.check3, False, False,3)
		self.vbox_prefs.pack_start(self.check4, False, False,3)
		self.vbox_prefs.pack_start(self.check7, False, False,3)
		self.vbox_prefs.pack_start(self.hbox12, False, False,3)
		self.vbox_prefs.pack_start(self.hbox13, False, False,3)
		self.vbox_prefs.pack_start(self.hbox16, False, False,3)

	def add_about_tab(self):

		self.vbox_about = gtk.VBox()
		self.image_logo = gtk.Image()
		self.image_logo.set_size_request(80,80)
		self.Applogo = gtk.gdk.pixbuf_new_from_file_at_size(Globals.Applogo,80,80)
		self.image_logo.set_from_pixbuf(self.Applogo)
		self.label_app = gtk.Label("YMenu %s" % Globals.version)
                self.label_credits = gtk.Label(_("Ylmf OS advanced menu."))
		self.font_desc = pango.FontDescription('sans bold 14')
		self.label_app.modify_font(self.font_desc)
		self.label_credits.set_justify(gtk.JUSTIFY_CENTER)
		self.button5 = gtk.Button(_('Report Bug'))
		self.button5.set_border_width(5)
		self.button5.connect('clicked', self.button_clicked, 'Bug')
		
		self.button7 = gtk.Button(_('Visit Homepage'))
		self.button7.set_border_width(5)
		self.button7.connect('clicked', self.button_clicked, 'Homepage')
                
                #self.Image = gtk.Image()
                #self.Image.set_from_file("%s115.gif" % Globals.GraphicsDirectory)
                #self.vbox_about.pack_start(self.Image, False, False,10)
		self.vbox_about.pack_start(self.image_logo, False, False, 20)
		self.vbox_about.pack_start(self.label_app, False, False,10)
		self.vbox_about.pack_start(self.label_credits, False, False,10)
		self.vbox_about.pack_start(self.button5, False, False)
		self.vbox_about.pack_start(self.button7, False, False)
		

	def buttonpress(self,widget,id):
		if id == 'ok':
			self.SaveSettings()
                        object_name = "ymenu_screen0"
                        object_dir = "/apps/panel/applets/"
                        object_client = gconf.client_get_default()
                        appletidlist = object_client.get_list("/apps/panel/general/applet_id_list", "string")
                        for applet in appletidlist:
                        	bonobo_id = object_client.get_string("/apps/panel/applets/" + applet + "/bonobo_iid")
                                panel_position = object_client.get_int("/apps/panel/applets/" + applet + "/position")
                                if bonobo_id == "OAFIID:GNOME_YMenu":
                                	panel = object_client.get_string("/apps/panel/applets/" + applet + "/toplevel_id")
                                        appletidlist.remove(applet)
                                        object_client.set_list("/apps/panel/general/applet_id_list", gconf.VALUE_STRING, appletidlist)
                                        os.system("sleep 0.3")
                                                
                                        object_client.set_string(object_dir + object_name +"/"+ "action_type", "lock")
                                        object_client.set_bool(object_dir + object_name +"/"+ "locked", True)
                                        object_client.set_int(object_dir + object_name +"/"+ "position", 0)
                                        object_client.set_string(object_dir + object_name +"/"+ "toplevel_id", panel)
                                        object_client.set_string(object_dir + object_name +"/"+ "object_type", "bonobo-applet")
                                        object_client.set_string(object_dir + object_name +"/"+ "bonobo_iid", bonobo_id)
                                                
                                        appletidlist.append(object_name)
                                        object_client.set_list("/apps/panel/general/applet_id_list", gconf.VALUE_STRING, appletidlist)
			gtk.main_quit()

		elif id == 'apply':
			self.SaveSettings()

		elif id == 'cancel':
			gtk.main_quit()
	
	def button_clicked (self, widget, id):

		if id == 'Bug':
			os.system('xdg-open http://feedback.115.com/?ct--feedback--ac--ask--app--105 &')
	
		elif id == 'Homepage':
			os.system('xdg-open http://www.ylmf.org &')


	def reload_themes(self,id):
		if id == 'Menu':
			themes = os.listdir('%s/share/ymenu/Themes/Menu/' % INSTALL_PREFIX)
			themes.sort(key=str.upper)
			x = 0
			self.combo_menu.get_model().clear()
			for folder in themes: 
				self.combo_menu.append_text(folder)	
				if folder == Globals.Settings['Menu_Name']:
					self.combo_menu.set_active(x)
				x = x + 1
		elif id == 'Button':
			themes = os.listdir('%s/share/ymenu/Themes/Button/' % INSTALL_PREFIX)
			themes.sort(key=str.upper)
			x = 0
			self.combo_button.get_model().clear()
			for folder in themes: 
				self.combo_button.append_text(folder)
				if folder == Globals.Settings['Button_Name']:
					self.combo_button.set_active(x)
				x = x + 1
		elif id == 'Icon':
			themes = os.listdir('%s/share/ymenu/Themes/Icon/' % INSTALL_PREFIX)
			themes.sort(key=str.upper)
			x = 0
			self.combo_icon.get_model().clear()
			for folder in themes: 
				self.combo_icon.append_text(folder)
				if folder == Globals.Settings['Icon_Name']:
					self.combo_icon.set_active(x)
				x = x + 1

		elif id == 'Sound':
			themes = os.listdir('%s/share/ymenu/Themes/Sound/' % INSTALL_PREFIX)
                        themes.sort(key=str.upper)
			self.combo_sound.get_model().clear()
			self.combo_sound.append_text('None')
			self.combo_sound.set_active(0)
			x = 0
			for folder in themes: 
				self.combo_sound.append_text(folder)
				if folder == Globals.Settings['Sound_Theme']:
					self.combo_sound.set_active(x)
				x = x + 1

	def redraw_image(self,widget,id):
		if widget.get_active_text() is None: return
		if id == 'Menu':
			try:
				Pixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%sMenu/%s/themepreview.png" % (Globals.ThemeDirectory, widget.get_active_text()),100,200)
			except:
				Pixbuf = gtk.gdk.pixbuf_new_from_file("%stheme.png" % Globals.GraphicsDirectory)
			self.image_menu.set_from_pixbuf(Pixbuf)
			
		elif id == 'Button':
			try:
				Pixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%sButton/%s/themepreview.png" % (Globals.ThemeDirectory, widget.get_active_text()),54,54)
			except:
				Pixbuf = gtk.gdk.pixbuf_new_from_file("%stheme.png" % Globals.GraphicsDirectory)
			self.image_button.set_from_pixbuf(Pixbuf)
			
		elif id == 'Icon':
			try:
				Pixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%sIcon/%s/computer.png" % (Globals.ThemeDirectory, widget.get_active_text()),54,54)
			except:
				Pixbuf = gtk.gdk.pixbuf_new_from_file("%stheme.png" % Globals.GraphicsDirectory)
			self.image_icon.set_from_pixbuf(Pixbuf)

		elif id == 'Sound':
                        try:
				Pixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%sIcon/%s/sound_icon.png" % (Globals.ThemeDirectory, widget.get_active_text()),64,64)
			except:
                                Pixbuf = gtk.gdk.pixbuf_new_from_file_at_size("%sIcon/ylmfos/sound_icon.png" % (Globals.ThemeDirectory),64,64)

			if self.combo_sound.get_active_text() == 'None':
                                self.image_sound.set_from_pixbuf(Pixbuf)         
			else:
                                self.image_sound.set_from_pixbuf(Pixbuf)

	def SaveSettings(self):
		backend.save_setting("Bind_Key",self.entry_check1.get_text())
		backend.save_setting("Show_Tips",int(self.check7.get_active()))
		backend.save_setting("TabHover",int(self.check4.get_active()))
		backend.save_setting("Sound_Theme",self.combo_sound.get_active_text())
		backend.save_setting("Tab_Efect",self.combo6.get_active())
		backend.save_setting("Menu_Name",self.combo_menu.get_active_text())
		backend.save_setting("IconSize",int(self.spinbutton1.get_value()))
		backend.save_setting("ListSize",int(self.spinbutton2.get_value()))
		backend.save_setting("SuperL",int(self.check1.get_active()))
		backend.save_setting("Icon_Name",self.combo_icon.get_active_text())
		backend.save_setting("Button_Name",self.combo_button.get_active_text())
		#backend.save_setting("GtkColors",int(self.check3.get_active()))

def main():
	gtk.main()
	return 0

if __name__ == "__main__":
	YMenuSettings()
	main()

