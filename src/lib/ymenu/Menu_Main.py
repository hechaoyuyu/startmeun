#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import gtk
import gobject
import cairo
import os
from Menu_Widgets import MenuButton, ProgramClass, SearchLauncher
import Globals
import Launcher
import gconf
import gio
import backend
from math import pi

try:
	has_gst = True
	import gst
except:
	has_gst = False

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

# Class for a button object from menu

try:
	import psyco
        psyco.log(Globals.ConfigDirectory + "/" + "profile")
	psyco.profile()
except:pass

# Load the key binding lib (developped by deskbar-applet, copied into YMenu so we don't end up with an unnecessary dependency)
try:
    from deskbar.core.keybinder import tomboy_keybinder_bind as bind_key
except Exception, cause:
    print "*********** Keybind Driver Load Failure **************"
    print "Error Report : ", str(cause)
    pass

import time

class Main_Menu(gobject.GObject):
	__gsignals__ = {
        'state-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,(gobject.TYPE_INT,gobject.TYPE_INT)),
        }

        BlockSearchFlag = 1
        BlockNotSearchFlag = 2
        UnBlockSearchOpt = 0
       
	first_time = True
	def __init__(self, hide_method):
		gobject.GObject.__init__(self)
		print 'start'
		#self.searchitem = ''
		self.hide_method = hide_method
		#Set the main working directory to home
		os.chdir(Globals.HomeDirectory)
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_title('YMenu')
		self.window.set_focus_on_map(1)
		self.window.set_app_paintable(1)
		self.window.set_skip_taskbar_hint(1)
		self.window.set_skip_pager_hint(1)
		self.window.set_decorated(0)
		#self.window.set_keep_above(0) #Make this always above other windows
		self.window.stick() #Make this appear on all desktops
		#self.window.set_default_size(Globals.MenuWidth,Globals.MenuHeight)
		#在ubuntu11.04中需要下面两句
		#self.window.set_resizable(False)
		self.window.set_size_request(Globals.MenuWidth, Globals.MenuHeight)
		self.window.set_events(gtk.gdk.ALL_EVENTS_MASK)
		#if not self.window.window:
		self.colorpb = None
		self.setup()
		self.window.connect("composited-changed", self.composite_changed)
		self.window.connect("expose_event", self.expose)
		self.window.connect("delete_event", self.delete)
		self.window.connect("focus-out-event", self.lose_focus)
                self.window.connect("focus-in-event", self.get_focus)
		self.window.connect("key-press-event", self.key_down)
		self.gtk_screen = self.window.get_screen()
		colormap = self.gtk_screen.get_rgba_colormap()
		if colormap is None:
			colormap = self.gtk_screen.get_rgb_colormap()
		gtk.widget_set_default_colormap(colormap)  
		if not self.window.is_composited():
			self.supports_alpha = False
		else:
			self.supports_alpha = True
		
		self.w,self.h = self.window.get_size()
		self.leave_focus = True
		self.callback_search = None
		self.GnomeMenu = None
		self.visible = False
                self.Launcher = Launcher.Launcher()
		if Globals.Settings['SuperL'] == 1:
			self.bind_with_keybinder()

	def delete(self,widget,event=None):
	    	return True
			
	def special_command(self,event):
		if not self.GnomeMenu:
			import Gnome_Me
			self.GnomeMenu = Gnome_Me.GnomeMenu()
			self.GnomeMenu.connect_after('unmap',self.GnomeMenu_unmap)
		self.leave_focus = False
		self.GnomeMenu.showmenu()
		self.callback = gobject.timeout_add(1500,self.timeout_callback)

	def GnomeMenu_unmap(self,event):
		if not self.window.is_active():
			self.emit('state-changed',0,0)
			self.hide_window()
	
	def auxdestroyed(self):
		#dummy sub for module compatibility
		pass
	
	def destroy(self):
		# External Obliterator
		self.PGL.destroy()
		
	def internal_destroy(self,widget,event):
		# Internal Obliterator (event driven)
		self.PGL.destroy()

	def ToggleMenu(self):
		print self.visible
		if not self.window.window:
			self.emit('state-changed',2,2)
			self.show_window()
			self.visible = False
		else:
			if not self.visible:
				self.emit('state-changed',2,2)
				self.show_window()
				self.visible = True
			else:
				self.emit('state-changed',0,0)
				self.hide_window()
				self.visible = False

#=================================================================
#Key binding
#=================================================================
	def bindkey_callback(self,keybinding):
		print 'key'
		self.ToggleMenu()

	def bind_with_keybinder(self):
                try:
                    # Binding menu to hotkey
                    print "Binding to Hot Key: " + Globals.Settings['Bind_Key']
                    bind_key( Globals.Settings['Bind_Key'], self.ToggleMenu )
                    bind_key( "<Alt>E", self.open_computer )
                    bind_key( "<Alt>Pause", self.open_monitor )
                    #bind_key( "<Alt>R", self.open_run )
                    bind_key( "Num_Lock", self.numlock)
                except Exception, cause:
                    print "** WARNING ** - Menu Hotkey Binding Error"
                    print "Error Report :\n", str(cause)
                    pass

        def open_computer(self):
                os.system("xdg-open computer:///")

        def open_monitor(self):
                os.system("gnome-system-monitor -s &")

        def open_run(self):
                run = "%sGnome_run_dialog.py" % Globals.ProgramDirectory
                os.system("python -u %s" % run)

        def numlock(self):
                numlock = backend.load_setting("Num_lock")
                if numlock == "on":
                        backend.save_setting("Num_lock","off")
                else:backend.save_setting("Num_lock","on")

#=================================================================
#WINDOW SETUP
#=================================================================

        def special_rectangle(self, ctx, x, y, w, h, lw, r, lcolor, rcolor):

                color = []
                ctx.move_to(x + r, y) # 上  left width
                ctx.line_to(x + lw, y)

                ctx.line_to(x + lw, y + h) # right 

                ctx.line_to(x + r, y + h) # bottom

		ctx.line_to(x, y + h - r)
                ctx.line_to(x, y + r)  # left 

                ctx.arc(x + r, y + r, r, pi, 3 * pi / 2) #左上
                ctx.arc(x + r, y + h - r, r, pi / 2, pi)     # 90 - 0
                color = Globals.color_translate(lcolor)
                ctx.set_source_rgb(color[2], color[1], color[0])
                ctx.fill()

		# 右半部分
		x = x + lw # y = y
		rw = w - lw
		
		ctx.move_to(x, y) # 上  left width
                ctx.line_to(x + rw - r, y)

		ctx.move_to(x + rw, y + r) # 
                ctx.line_to(x + rw, y + h - r) # right 

		ctx.move_to(x + rw - r, y + h) # 
                ctx.line_to(x, y + h) # bottom

                ctx.line_to(x, y)  # left 

                ctx.arc(x + rw - r, y + r, r, 3 * pi / 2, pi * 2) #右上
                ctx.arc(x + rw - r, y + h - r, r, 0, pi / 2)     # 0 - 90
                color = Globals.color_translate(rcolor)
                ctx.set_source_rgb(color[2], color[1], color[0])
                ctx.fill()
                del color

        def expose (self, widget, event):

		self.ctx = widget.window.cairo_create()
		self.ctx.set_operator (cairo.OPERATOR_SOURCE)
		# set a clip region for the expose event
		if self.supports_alpha:
                        self.ctx.set_source_rgba(0.0, 0.0, 0.0, 0.0)
                        self.ctx.paint()

                self.special_rectangle(self.ctx, 2, 0, Globals.MenuWidth - 2, Globals.MenuHeight - 2, \
                                                Globals.PG_tabframedimensions[0], 6.0, \
                                                Globals.PG_bgcolor, Globals.App_bgcolor)
                
	def setup(self):
		self.menuframe = gtk.Fixed()
		self.window.add (self.menuframe)
		
		w,h = self.window.get_size()
		if w==0: w = 100
		if h==0: h = 100
		self.w = w
		self.h = h
		#self.window.set_opacity(0.99)
		
                if Globals.MenuHasTab == 1:
                        # init
                        self.PGL = ProgramClass(self.menuframe) 
                        self.PGL.connect ('menu', self.menu_callback)
			self.PGL.connect ('right-clicked', self.menu_right_clicked)
                        self.search_env_id = self.PGL.connect ('NeedSearch', self.net_Search)
                        self.notsearch_env_id = self.PGL.connect('NotNeedSearch', self.rm_Search)
                        self.PGL.buildButtonList(self.hide_method)
                        self.PGL.buildFavorites()
                        self.PGL.buildRecent()
                        self.PGL.buildPlaces()
                        self.gfile = gio.File(Globals.Favorites)
                        self.monitor = self.gfile.monitor_directory(gio.FILE_MONITOR_NONE, None)
                        self.monitor.connect("changed", self.directory_changed)
                         
                        if has_gst:
                                self.StartEngine()                 
     
		self.MenuButtons = []
		for i in range(0,Globals.MenuButtonCount):
			self.MenuButtons.append(MenuButton(i, self.menuframe))
			self.MenuButtons[i].Button.connect("enter-notify-event", self.Button_enter, i)
			self.MenuButtons[i].Button.connect("leave-notify-event", self.Button_leave, i)
			self.MenuButtons[i].Button.connect("button-release-event", self.Button_click, i)
                
		if Globals.MenuHasSearch:

                        if Globals.SearchWidget.upper() == "GTK":
				from Menu_Widgets import  GtkSearchBar
				gobject.type_register(GtkSearchBar)
				self.SearchBar = GtkSearchBar(Globals.ImageDirectory + Globals.SearchBackground,Globals.SearchW,Globals.SearchH,self.window)
                                self.SearchBar.connect ('right-clicked', self.menu_right_clicked)

			try:
				self.SearchBar.set_size_request(Globals.SearchW, Globals.SearchH)
				self.menuframe.put(self.SearchBar, Globals.SearchX, Globals.SearchY)
	
				self.SearchBar.connect_after("key-release-event", self.SearchBarActivate)
                                self.SearchBar.entry.connect("paste-clipboard", self.searchbar_paste)
			except:print 'wait'
			self.prevsearchitem = ""			

	def directory_changed(self, monitor, file1, file2, evt_type):
                print evt_type
                if evt_type == gio.FILE_MONITOR_EVENT_CREATED or evt_type == gio.FILE_MONITOR_EVENT_DELETED:
                        self.PGL.buildFavorites()
        
        def menu_callback(self,event):
		
		self.leave_focus = False
		if self.leave_focus == False:
			self.callback = gobject.timeout_add(500,self.timeout_callback)

	def menu_clicked(self,event):
		self.PlaySound(2)


	def menu_right_clicked(self, event):
		self.leave_focus = False
		self.callback = gobject.timeout_add(500,self.timeout_callback)

        def timeout_callback(self):
		self.leave_focus = True
		return False

	def Adjust_Window_Dimensions(self, win_x, win_y):
		self.window.move(win_x, win_y)


	def composite_changed(self,widget):
		self.hide_method()
		self.show_window()	
		if not self.window.is_composited():
 
			self.supports_alpha = False
		else:
			self.supports_alpha = True
		self.shape()

	def show_window(self):
		#self.window.set_keep_above(1)
		if not self.window.window:
                        self.window.show_all()
                        self.window.present()
		else: 
			try:
                                self.window.present()
				self.window.present_with_time(int(time.time())/100)
			except:
				self.window.present()
				self.window.window.focus(int(time.time())/100)
		self.window.set_urgency_hint(1)
		self.window.activate_focus()             
                self.window.set_opacity(0.85)
		self.PlaySound(0)


	def lose_focus(self,widget,event):
		print 'focus lost'
		if self.leave_focus is True:
			self.hide_method()

	def get_focus(self, widget, event):
                print 'focus receive'
                self.SearchBar.r_clk = False
                Globals.searchitem = self.SearchBar.entry.get_text()

        def hide_window(self):
		print 'hide'                
		self.window.hide()		
                self.SearchBar.entry.set_text(_('Search'))
                self.SearchBar.r_clk = False
                self.window.set_focus(None)
                self.PGL.emit('NotNeedSearch')
    		if self.PGL.Search_Flag:
                    self.PGL.App_VBox.show_all()
    		    self.PGL.Search_Flag = False

                if self.UnBlockSearchOpt & self.BlockNotSearchFlag:
                    self.PGL.handler_unblock(self.notsearch_env_id)
                    self.UnBlockSearchOpt &= ~self.BlockNotSearchFlag

                if self.UnBlockSearchOpt & self.BlockSearchFlag:
                    self.PGL.handler_unblock(self.search_env_id)
                    self.UnBlockSearchOpt &= ~self.BlockSearchFlag

		if Globals.MenuHasSearch:
			if Globals.searchitem != '':
                                Globals.searchitem = ''
                                self.window.set_focus(None)
                                self.PGL.Restart('previous')
		self.PlaySound(1)
		
	def key_down (self, widget, event):
		key = event.hardware_keycode
                print "key = %s" % key
		if key == 9:	#Escape Key, hides window
			self.hide_method()
		elif key == 98 or key == 104 or key == 102 or key == 100 or key == 36 or key == 116 or key ==111 or key == 113 or key == 114 or key == 23:
			# Menu naviagation keys give focus to program list
			if Globals.MenuHasSearch:
                                if self.SearchBar.entry.is_focus() is True:

                                        if key==36 or key == 104: #and self.PGL.XDG.searchresults!=0: # Enter on searchbar launches first item in search list
                                                self.PGL.CallSpecialMenu(6, None, self.SearchBar)
                                                self.hide_method()
                                        self.PGL.BanFocusSteal = False
                                        self.PGL.SetInputFocus()
                               
			if key == 23 :
				for i in range(0,Globals.MenuTabCount):
					if self.MenuTabs[i].GetSelectedTab():
						c = i+1
						if c > Globals.MenuTabCount-1:
							c = 0
				for i in range(0,Globals.MenuTabCount):
					if i == c:
						self.MenuTabs[i].SetSelectedTab(True)
						if Globals.MenuTabSub[i] == 0:
			
							self.Launcher.Launch(Globals.MenuTabCommands[i])
			
					 	else:
							self.PGL.CallSpecialMenu(int(Globals.MenuTabCommands[i]))
			
						# Close menu if specified by theme
						if Globals.MenuTabClose[i] == 1 and self.leave_focus is True:
							self.hide_method()
						#self.PGL.Restart()
						if self.leave_focus == False:
							self.callback = gobject.timeout_add(3000,self.timeout_callback)
					else:
						self.MenuTabs[i].SetSelectedTab(False)

				self.PlaySound(3)

			if key == 36 or key == 104:

				self.PlaySound(2)

                elif key == 22 or key == 119:# del & backspace
                    if self.SearchBar.r_clk:
                        if self.SearchBar.entry.get_text() == '':
                            self.SearchBar.r_clk = False

                else:	#Any other key passes through to search bar
			if Globals.MenuHasSearch:
                                if self.SearchBar.entry.is_focus() == False:
                                        self.SearchBar.entry.grab_focus()
				self.SearchBarActivate()

#=================================================================
#Menu Buttons
#================================================================= 
	def Button_enter(self,widget,event,i):
		# Change button background
		self.MenuButtons[i].Setimage(Globals.ImageDirectory + Globals.MenuButtonImage[i])
		if Globals.MenuButtonIconSel[i]:
			self.MenuButtons[i].SetIcon(Globals.ImageDirectory + Globals.MenuButtonIconSel[i])

	def Button_leave(self,widget,event,i):
		# Button background
		self.MenuButtons[i].SetBackground()
		if Globals.MenuButtonIcon[i]:
			self.MenuButtons[i].SetIcon(Globals.ImageDirectory + Globals.MenuButtonIcon[i])
	
	def Button_click(self,widget,event,i):
		if Globals.MenuButtonCommands[i] == "search":
                        self.leave_focus = False
                        self.callback = gobject.timeout_add(500,self.timeout_callback)
                        self.searchPopup()                        
                else:
                        if Globals.MenuButtonSub[i] == 0:
                                print Globals.MenuButtonCommands[i]
                                self.Launcher.Launch(Globals.MenuButtonCommands[i])
                        else:
                                self.PGL.CallSpecialMenu(int(Globals.MenuButtonCommands[i]))
	
                        if Globals.MenuButtonClose[i] == 1 and self.leave_focus is True:
                                self.hide_method()
		
                        if self.leave_focus == False:
                                self.callback = gobject.timeout_add(3000,self.timeout_callback)

                        self.PlaySound(2)
	
	def net_Search(self, event):

            self.PGL.handler_block(self.search_env_id)
            self.UnBlockSearchOpt |= self.BlockSearchFlag

            if self.UnBlockSearchOpt & self.BlockNotSearchFlag:
                self.PGL.handler_unblock(self.notsearch_env_id)
                self.UnBlockSearchOpt &= ~self.BlockNotSearchFlag

            icondir = INSTALL_PREFIX + '/share/ymenu/Themes/Icon/ylmfos/'
            self.google_search = SearchLauncher(icondir + 'google.xpm', self.PGL.App_VBox, _("Search Google"))
            self.google_search.connect('button_release_event', self.search_go, 'google')

            self.baidu_search = SearchLauncher(icondir + 'baidu.xpm', self.PGL.App_VBox, _("Search Baidu"))
            self.baidu_search.connect('button_release_event', self.search_go, 'baidu')

            self.ylmf116_search = SearchLauncher(icondir + '116.xpm', self.PGL.App_VBox, _("Search 116") )
            self.ylmf116_search.connect('button_release_event', self.search_go, '116')

            self.wiki_search = SearchLauncher(icondir + 'wikipedia.xpm', self.PGL.App_VBox, _("Search Wikipedia"))
            self.wiki_search.connect('button_release_event', self.search_go, 'wikipedia')


        def rm_Search(self, event):
            self.PGL.handler_block(self.notsearch_env_id)
            self.UnBlockSearchOpt |= self.BlockNotSearchFlag 
            if self.UnBlockSearchOpt & self.BlockSearchFlag:
                self.PGL.handler_unblock(self.search_env_id)
                self.UnBlockSearchOpt &= ~self.BlockSearchFlag
            try:
                self.google_search.destroy()
                self.wiki_search.destroy()
                self.ylmf116_search.destroy()
                self.baidu_search.destroy()
            except:
                pass

        def searchPopup( self ):

                menu = gtk.Menu()   
             
                menuItem = gtk.ImageMenuItem(_("Search Google"))
                img = gtk.Image()
                img.set_from_file(Globals.ImageDirectory + 'google.ico')
                menuItem.set_image(img)
                menuItem.connect("activate", self.search_google)
                menu.append(menuItem)
        
                menuItem = gtk.ImageMenuItem(_("Search Wikipedia"))
                img = gtk.Image()
                img.set_from_file(Globals.ImageDirectory + 'wikipedia.ico')
                menuItem.set_image(img)
                menuItem.connect("activate", self.search_wikipedia)
                menu.append(menuItem)
        
                #menuItem = gtk.SeparatorMenuItem()
                #menu.append(menuItem)
             
                menu.show_all()
                menu.popup( None, None, None, 3, 0)

        def search_go(self, widget, event, searchEn = None):
        	from urllib import unquote
                text = self.SearchBar.entry.get_text()
                text = unquote(str(text))
                if searchEn is None or text is None:
                    return
                elif searchEn == 'google':
                    url = "http://www.google.com.hk/search?q=%s" % text
                elif searchEn == 'wikipedia':
                    url = "http://zh.wikipedia.org/wiki/Special:Search?search=%s" % text
                elif searchEn == '116':
                    url = "http://s.116.com/?q=%s" % text
                elif searchEn == 'baidu':
                    url = "http://www.baidu.com/s?wd=%s&tn=ylmf_3_pg&ch=57" % text
                else:
                    url = "http://www.google.com.hk/search?q=YlmfOS"
                os.system("xdg-open \"%s\" &" % url)
                self.hide_method()

#=================================================================
#PLAY SOUND
#=================================================================			
	def StartEngine(self):
		self.player = gst.element_factory_make("playbin", "player")
		fakesink = gst.element_factory_make('fakesink', "my-fakesink")
		self.player.set_property("video-sink", fakesink)
		self.player_bus = self.player.get_bus()
		self.player_bus.add_signal_watch()
		self.player_bus.connect('message', self.on_message)

	def on_message(self, bus, message):
		t = message.type
		if t == gst.MESSAGE_EOS:
			self.player.set_state(gst.STATE_NULL)
			#self.button.set_label("Start")
		elif t == gst.MESSAGE_ERROR:
			self.player.set_state(gst.STATE_NULL)
			#self.button.set_label("Start")

	def PlaySound(self,sound):
                sound_client = gconf.client_get_default()
                sound_id = sound_client.get_bool("/desktop/gnome/sound/event_sounds")
		if Globals.Settings['Sound_Theme'] != 'None' and sound_id:
			if sound == 0:
				uri = 'file://%s/share/ymenu/Themes/Sound/%s/show-menu.ogg' % (INSTALL_PREFIX, Globals.Settings['Sound_Theme'])
			elif sound == 1:
				uri = 'file://%s/share/ymenu/Themes/Sound/%s/hide-menu.ogg' % (INSTALL_PREFIX, Globals.Settings['Sound_Theme'])
			elif sound == 2:
				uri = 'file://%s/share/ymenu/Themes/Sound/%s/button-pressed.ogg' % (INSTALL_PREFIX, Globals.Settings['Sound_Theme'])
			elif sound == 3:
				uri = 'file://%s/share/ymenu/Themes/Sound/%s/tab-pressed.ogg' % (INSTALL_PREFIX, Globals.Settings['Sound_Theme'])

			if has_gst:
                                #print "has_gst"
				self.player.set_state(gst.STATE_NULL)
				self.player.set_property('uri',uri)
				self.player.set_state(gst.STATE_PLAYING)
			else:
				os.system('mplayer %s &' % uri)

#=================================================================
#SEARCH BAR
#=================================================================
	def SearchBarActivate(self,widget=None,event=None):
		Globals.searchitem = self.SearchBar.entry.get_text()
		if self.prevsearchitem != Globals.searchitem:
			self.PGL.BanFocusSteal = True
			self.prevsearchitem = Globals.searchitem
			if self.callback_search:
					gobject.source_remove(self.callback_search)
			self.callback_search = gobject.timeout_add(500,self.timeout_callback_search)
                        
	def timeout_callback_search(self):
            self.PGL.CallSpecialMenu(5, Globals.searchitem)
            return False

        def searchbar_paste(self, widget):
            Globals.searchitem = self.SearchBar.entry.get_text()
            Globals.searchitem = Globals.searchitem.replace('\r', '')
            Globals.searchitem = Globals.searchitem.replace('\n', '')
            self.PGL.CallSpecialMenu(5, Globals.searchitem)
            

# Code to launch menu standalone of base classes

def destroy():
	hwg.destroy()
	sys.exit()
	
if __name__ == "__main__":
	hwg = Main_Menu(destroy)
	hwg.setup()
	hwg.show_window()
	gtk.main()
	
