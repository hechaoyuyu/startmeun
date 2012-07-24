#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import division
import gtk
import gc
import os
import xml.dom.minidom
import backend
import sys
import commands
import re
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

global name,version,appdirname 
name = _("Start")
version = "4.0"
appdirname="ymenu"

HomeDirectory = os.path.expanduser("~")
if not os.path.exists('%s/.%s' % (HomeDirectory, appdirname)) or not os.path.isdir('%s/.%s' % (HomeDirectory,appdirname)):
	os.system('mkdir ~/.%s' % appdirname)

ConfigDirectory = '%s/.%s'  % (HomeDirectory,appdirname)
PanelLauncher = '%s/.gnome2/panel2.d/default/launchers'  % HomeDirectory

Favorites = ConfigDirectory+"/favorites/"
if not os.path.exists(Favorites) or not os.path.isdir(Favorites):
        os.system('mkdir %s' % Favorites)

AutoStartDirectory = '%s/.config/autostart/' % HomeDirectory
ProgramDirectory = "%s/lib/%s/" % (INSTALL_PREFIX, appdirname)
ThemeDirectory = "%s/share/%s/Themes/" % (INSTALL_PREFIX,appdirname)
GraphicsDirectory = "%s/lib/%s/graphics/"  % (INSTALL_PREFIX,appdirname)

ThemeCategories = ["Menu","Icon","Button"]
gconf_app_key = '/apps/%s' % appdirname

FirstUse = False

DefaultSettings = {"Bind_Key":"Super_L" , "Sound_Theme":"None" , "Num_lock":"on", "flag":0, "Show_Tips":1 , "Distributor_Logo":0, "Menu_Name":"startos" , "IconSize":24 , "ListSize":12 , "SuperL":1 , "Icon_Name":"startos" , "Button_Name":"blue-crystal", "TabHover":1 , "Control_Panel":"gnome-control-center"  ,"Y_Center":"softwarecenter" , "Power":"gnome-session-save --shutdown-dialog" , "Logout":"gnome-session-save --logout-dialog" , "User":"gnome-about-me" , "AdminRun":"gksu", "MenuEditor":"gmenu-simple-editor", "MenuHeight":575}

Settings = DefaultSettings.copy()

def SetDefaultSettings():
	"""Sets Default Settings using the backend"""
	for x in DefaultSettings:
		backend.save_setting(x,DefaultSettings[x])
	FirstUse = True

# Load settings stored in XML
def ReloadSettings():

	def SetDefaultSettings():
		for x in DefaultSettings:
			backend.save_setting(x,DefaultSettings[x])
		FirstUse = True

	def GetSettings():
		print 'settings load'
		for x in DefaultSettings:
			Settings[x] = backend.load_setting(x)

        # Loads the main configuration and settings file to their respective values
	global orientation, panel_size, flip, MenuActions, MenuCommands, ImageDirectory, Actions, IconDirectory, MenuButtonDirectory, ThemeColor, ShowTop, FirstUse, StartMenuTemplate, ThemeColorCode,ThemeColorHtml, NegativeThemeColorCode, MenuWidth, MenuHeight, IconW, IconH, IconInX, IconInY, IconInW, IconInH, SearchWidget, SearchWidgetPath, PG_tabframe, PG_tabframedimensions, PG_buttonframe, PG_buttonframedimensions, MenuHasSearch, MenuHasIcon, MenuHasFade, MenuHasTab, CairoSearchTextColor, CairoSearchBackColor, CairoSearchBorderColor, CairoSearchRoundAngle, PG_iconsize,RI_numberofitems, MenuButtonCount, MenuButtonNames, MenuButtonMarkup, MenuButtonNameOffsetX, MenuButtonNameOffsetY, MenuButtonCommands, MenuButtonX,MenuButtonY, MenuButtonImage, MenuButtonImageBack, ButtonBackImage, ButtonBackIconX, ButtonBackIconY, ButtonBackNameX, ButtonBackNameY, TabBackImage, TabBackIconX, TabBackIconY, TabBackNameX, TabBackNameY, MenuButtonIcon, MenuButtonIconSel, MenuButtonIconX,MenuButtonIconY,MenuButtonIconSize, MenuButtonSub, MenuButtonClose, MenuCairoIconButton, ButtonHasTop, ButtonBackground, ButtonTop, StartButton, StartButtonTop, ButtonHasBottom, MenuButtonNameAlignment, GtkColorCode
        global SearchX, SearchY, SearchW, SearchH, SearchIX, SearchIY, SearchInitialText, SearchTextColor, SearchBackground, SearchBgSize
        global SearchPic, SearchPicX, SearchPicY, SearchPicW, SearchPicH
        global lowresolution, width_ratio, height_ratio, tab_back_size, MFontSize, button_back_size, UserMenuHeight
        global App_fgcolor, App_bgcolor, PG_fgcolor, PG_bgcolor, CategoryCommands
        global MenuButtonW, MenuButtonH
        
        lowresolution = False

	menubar = gtk.MenuBar()
	try:
		GtkColorCode = menubar.rc_get_style().bg[gtk.STATE_NORMAL]
	except:
		GtkColorCode = menubar.get_style().bg[gtk.STATE_NORMAL]
	orientation = None
	panel_size = 30
	flip = None
	orientation = backend.load_setting("orientation")
	panel_size = backend.load_setting("size")
	if orientation == 'top':
		flip = False
	elif orientation == 'bottom':
		flip = None
	GetSettings()
	for x in DefaultSettings:
		if Settings[x] is None:
			SetDefaultSettings()
			FirstUse = True
			GetSettings()
			break
	MenuActions = []
	MenuCommands = []
        CategoryCommands = {'Control Panel':Settings['Control_Panel'], 'Y Center':Settings['Y_Center']}

	MenuActions.append('Power')
	MenuCommands.append(Settings['Power'])
	MenuActions.append('Logout')
	MenuCommands.append(Settings['Logout'])
	ThemeColor = 'white'
	ImageDirectory = "%s/share/%s/Themes/Menu/%s/" % (INSTALL_PREFIX, appdirname, Settings['Menu_Name'])
	IconDirectory =  "%s/share/%s/Themes/Icon/%s/" % (INSTALL_PREFIX, appdirname, Settings['Icon_Name'])
	MenuButtonDirectory = "%s/share/%s/Themes/Button/%s/" % (INSTALL_PREFIX, appdirname, Settings['Button_Name'])
	PG_iconsize = int(float(Settings['IconSize']))
	RI_numberofitems = int(float(Settings['ListSize']))

        PG_tabframe = []
        PG_buttonframe = []
	PG_tabframedimensions = []
        PG_buttonframedimensions = []

        # Menu Themes
	try:
		XMLSettings = xml.dom.minidom.parse("%sthemedata.xml" % ImageDirectory)
	except:
		print "Error loading Menu theme, reverting to default"
		SetDefaultSettings()
		XMLSettings = xml.dom.minidom.parse("%sthemedata.xml" % ImageDirectory)
	XContent = XMLSettings.childNodes[0].getElementsByTagName("theme")
	# Identify correct theme style element
	Found = 0
	for node in XContent:
		if node.attributes["color"].value == ThemeColor or node.attributes["color"].value == "All":
			XBase = node
			ThemeColorHtml = node.attributes["colorvalue"].value
			ThemeColorCode = gtk.gdk.color_parse(ThemeColorHtml)
			color = ThemeColorCode
			color_r = 65535 - int(color.red)
			color_g = 65535 - int(color.green)
			color_b = 65535 - int(color.blue)
			NegativeThemeColorCode = gtk.gdk.Color(color_r,color_g,color_b,0)
			Found = 1
			break
	if Found==0:
		print "Error: Failed to find theme color: %s" % ThemeColor
		print "The available values are:"
		for node in XContent:
			print node.attributes["color"].value
		sys.exit()
	
	
	# Load WindowDimensions
	SBase = XBase.getElementsByTagName("WindowDimensions")
	MenuWidth = int(SBase[0].attributes["Width"].value)
	MenuHeight = int(SBase[0].attributes["Height"].value)

	try:
		UserMenuHeight = int(backend.load_setting("MenuHeight"))
	except:
		UserMenuHeight = 575

        if UserMenuHeight > 1000:
            UserMenuHeight = 1000
        elif UserMenuHeight < 350:
            UserMenuHeight = 350

	# Load WindowDimensions end
        
        # Load TabBackground Image
        try:
                SBase = XBase.getElementsByTagName("TabBackground")
                TabBackImage = SBase[0].attributes["Image"].value
                TabBackIconX = int(SBase[0].attributes["TabIconX"].value)
                TabBackIconY = int(SBase[0].attributes["TabIconY"].value)
                TabBackNameX = int(SBase[0].attributes["TextX"].value)
                TabBackNameY = int(SBase[0].attributes["TextY"].value)
        
                # Load ButtonBackground Image
                SBase = XBase.getElementsByTagName("ButtonBackground")
                ButtonBackImage = SBase[0].attributes["Image"].value
                ButtonBackIconX = int(SBase[0].attributes["ButtonIconX"].value)
                ButtonBackIconY = int(SBase[0].attributes["ButtonIconY"].value)
                ButtonBackNameX = int(SBase[0].attributes["TextX"].value)
                ButtonBackNameY = int(SBase[0].attributes["TextY"].value)
        except:pass
        
	# Load SearchBarSettings
	SBase = XBase.getElementsByTagName("SearchBarSettings")
	SearchWidget = SBase[0].attributes["Widget"].value
	if SearchWidget != "None":
		# Load universal values
		SearchX = int(SBase[0].attributes["X"].value)
		SearchW = int(SBase[0].attributes["Width"].value)
		SearchH = int(SBase[0].attributes["Height"].value)
		if orientation == 'bottom':
			SearchY = int(SBase[0].attributes["Y"].value)
		elif orientation == 'top':
			SearchY = MenuHeight -  int(SBase[0].attributes["Y"].value) - SearchH
		else:
			SearchY = int(SBase[0].attributes["Y"].value)
		# Load theme-only values
		if SearchWidget == "Gtk":
                        SearchBackground = SBase[0].attributes["Background"].value
			SearchW = int(SBase[0].attributes["Width"].value)
                        SearchH = int(SBase[0].attributes["Height"].value)

        #load search picture settings
        SBase = XBase.getElementsByTagName("SearchPicSettings")
        try:
            SearchPic = SBase[0].attributes["Image"].value
            SearchPicX = int(SBase[0].attributes["X"].value)
            SearchPicY = int(SBase[0].attributes["Y"].value)
            SearchPicW = int(SBase[0].attributes["Width"].value)
            SearchPicH = int(SBase[0].attributes["Height"].value)
        except:
            print "SearchPicSettings is not correct"

        # Load ProGramTabSettings
        try:
                SBase = XBase.getElementsByTagName("ProgramTabSettings")
                PG_tabframedimensions.append(int(SBase[0].attributes["Width"].value))
                PG_tabframedimensions.append(int(SBase[0].attributes["Height"].value))
                PG_tabframe.append(int(SBase[0].attributes["X"].value))
                PG_tabframe.append(int(SBase[0].attributes["Y"].value))
                PG_fgcolor = SBase[0].attributes["Foreground"].value
                PG_bgcolor = SBase[0].attributes["Background"].value
        except:pass

	# Load ProgramListSettings
	SBase = XBase.getElementsByTagName("ProgramListSettings")
	PG_buttonframedimensions.append(int(SBase[0].attributes["Width"].value))
        PG_buttonframedimensions.append(int(SBase[0].attributes["Height"].value))
	App_fgcolor = SBase[0].attributes["Foreground"].value
        App_bgcolor = SBase[0].attributes["Background"].value
        if orientation == 'botton':
		PG_buttonframe.append(int(SBase[0].attributes["X"].value))
                PG_buttonframe.append(int(SBase[0].attributes["Y"].value))
	elif orientation == 'top':
		PG_buttonframe.append(int(SBase[0].attributes["X"].value))
                PG_buttonframe.append(MenuHeight - int(SBase[0].attributes["Y"].value) - int(PG_buttonframedimensions[1]))
	else:
		PG_buttonframe.append(int(SBase[0].attributes["X"].value))
                PG_buttonframe.append(int(SBase[0].attributes["Y"].value))
	
	# Load Capabilities
	SBase = XBase.getElementsByTagName("Capabilities")
	MenuHasSearch = int(SBase[0].attributes["HasSearch"].value)
	MenuHasIcon = int(SBase[0].attributes["HasIcon"].value)
        try:
                MenuHasTab = int(SBase[0].attributes["HasTab"].value)
        except:
                MenuHasTab = 0

	#Load Menu Button List
	MenuButtons = XBase.getElementsByTagName("Button")
	MenuButtonCount = len(MenuButtons)	
	MenuButtonNames = []
	MenuButtonMarkup = []
	MenuButtonNameOffsetX = []
	MenuButtonNameOffsetY = []
	MenuButtonX = []
	MenuButtonY = []
        MenuButtonW = []
        MenuButtonH = []
	MenuButtonImage = []
	MenuButtonImageBack = []
	MenuButtonIcon = []
	MenuButtonIconX = []
	MenuButtonIconY = []
	MenuButtonIconSize = []
	MenuButtonIconSel = []
	MenuCairoIconButton = []
	MenuButtonSub = []
	MenuButtonCommands = []
	MenuButtonClose = []
	MenuButtonNameAlignment = []

	for node in MenuButtons:
		try:
			im = gtk.gdk.pixbuf_new_from_file(ImageDirectory + node.attributes["Image"].value)
		except:
			print 'Warning - Error loading theme, reverting to defaults'
			SetDefaultSettings()
		h = im.get_height()
		
		MenuButtonNames.append(node.attributes["Name"].value)
		MenuButtonMarkup.append(node.attributes["Markup"].value)
		MenuButtonNameOffsetX.append(int(node.attributes["TextX"].value))
		try:
			MenuButtonNameAlignment.append(int(node.attributes["TextAlignment"].value))
		except:
			MenuButtonNameAlignment.append(0)
		MenuButtonImage.append(node.attributes["Image"].value)    
		try:	    	
			MenuButtonImageBack.append(node.attributes["ImageBack"].value) 
		except: MenuButtonImageBack.append('')
		MenuButtonIcon.append(node.attributes["ButtonIcon"].value)    	    	
		MenuButtonIconSel.append(node.attributes["ButtonIconSel"].value)    	    	
		
		try:
			MenuCairoIconButton.append(node.attributes["Icon"].value)  
		except:
			MenuCairoIconButton.append("")  
		try:    	
			MenuButtonIconX.append(int(node.attributes["ButtonIconX"].value)) 
		except:
			MenuButtonIconX.append(0) 
		try:  
			MenuButtonIconY.append(int(node.attributes["ButtonIconY"].value)) 
		except:
			MenuButtonIconY.append(0) 
		try:
			MenuButtonIconSize.append(int(node.attributes["ButtonIconSize"].value)) 
		except:
			MenuButtonIconSize.append(0)
                try:
                        MenuButtonW.append(int(node.attributes["ButtonW"].value))
                except:
                        MenuButtonW.append(83)
                try:
                        MenuButtonH.append(int(node.attributes["ButtonH"].value))
                except:
                        MenuButtonH.append(28)
                        
		MenuButtonX.append(int(node.attributes["ButtonX"].value))
		if orientation == 'botton':
			MenuButtonNameOffsetY.append(int(node.attributes["TextY"].value))
			MenuButtonY.append(int(node.attributes["ButtonY"].value))
		elif orientation == 'top':
			MenuButtonNameOffsetY.append(int(node.attributes["TextY"].value) )
			MenuButtonY.append(MenuHeight - int(node.attributes["ButtonY"].value) -h )
		else:
			MenuButtonNameOffsetY.append(int(node.attributes["TextY"].value))
			MenuButtonY.append(int(node.attributes["ButtonY"].value))

		MenuButtonCommands.append(node.attributes["Command"].value)
		MenuButtonSub.append(int(node.attributes["SubMenu"].value))
		MenuButtonClose.append(int(node.attributes["CloseMenu"].value))

        #Button Themes
	try:
		XMLSettings = xml.dom.minidom.parse(MenuButtonDirectory+"themedata.xml")
	except:
		print "Error loading Menu button theme, reverting to default"
		SetDefaultSettings()
		XMLSettings = xml.dom.minidom.parse(MenuButtonDirectory+"themedata.xml")
	XBase = XMLSettings.getElementsByTagName("theme")

	ButtonHasTop = int(XBase[0].attributes["Top"].value)
	ShowTop = ButtonHasTop

	try:
		XMLSettings = xml.dom.minidom.parse(MenuButtonDirectory+"themedata.xml")
	except:
		SetDefaultSettings()
		XMLSettings = xml.dom.minidom.parse(MenuButtonDirectory+"themedata.xml")
	XBase = XMLSettings.childNodes[0].childNodes[1]
	
	
	ButtonBackground = XMLSettings.getElementsByTagName("Background")
    
	for node in ButtonBackground:
		StartButton = (MenuButtonDirectory+str(node.attributes["Image"].value),
		        	MenuButtonDirectory+str(node.attributes["ImageHover"].value),
	               		MenuButtonDirectory+str(node.attributes["ImagePressed"].value))

	if not ButtonBackground:
		StartButton = (MenuButtonDirectory+"start-here.png",
			MenuButtonDirectory+"start-here-glow.png",
        		MenuButtonDirectory+"start-here-depressed.png")

	ButtonTop = XMLSettings.getElementsByTagName("Top")
        
	for node in ButtonTop:
		StartButtonTop = (MenuButtonDirectory+str(node.attributes["Image"].value),
	       	       MenuButtonDirectory+str(node.attributes["ImageHover"].value),
        	       MenuButtonDirectory+str(node.attributes["ImagePressed"].value))

	if not ButtonTop:
		StartButtonTop = (MenuButtonDirectory+"start-here-top.png",
                     MenuButtonDirectory+"start-here-top-glow.png",
                     MenuButtonDirectory+"start-here-top-depressed.png")

        # ----------------------------------------------------------------

        # Category tab's background m_tab.png
        tab_back_size = []
        try:
            sel = gtk.gdk.pixbuf_get_file_info( ImageDirectory + TabBackImage )
            tab_back_size.append(sel[1])
            tab_back_size.append(sel[2])
            sel = None
        except:
            tab_back_size.append(137)
            tab_back_size.append(30)
            
        # App list button background size
        button_back_size = []
        try:
            sel = gtk.gdk.pixbuf_get_file_info(ImageDirectory + ButtonBackImage)
            button_back_size.append(sel[1])
            button_back_size.append(sel[2])
            del sel
        except:
            button_back_size.append(191)
            button_back_size.append(30)

        # SearchBar background
        if MenuHasSearch:
            SearchBgSize = []
            try:
                sel = gtk.gdk.pixbuf_get_file_info(ImageDirectory + SearchBackground)
                SearchBgSize.append(sel[1])
                SearchBgSize.append(sel[2])
                del sel
            except:
                SearchBgSize.append(191)
                SearchBgSize.append(25)


        # iconsize 32 | 24
        if PG_iconsize > 28:
            PG_iconsize = 32
            button_back_size[1] += 8
        else:
            PG_iconsize = 24


        # if encounter the low/high resolution monitor, scaling the menu size --------
        width_ratio = 1
        height_ratio = 1
        MFontSize = 'medium'
        orig_menu_width  = MenuWidth
        orig_menu_height = MenuHeight

        if UserMenuHeight != orig_menu_height:
            MenuHeight = UserMenuHeight
            if MenuHeight < 614: # 纵向分辨率768 的 4 / 5
                lowresolution = True
                if MenuHeight <  500:
                    MFontSize = 'small'
      
        else:
            return

        # ------------------scale processing  -----------------------------------------

        height_ratio = MenuHeight * 1.0 / orig_menu_height # 参照菜单，控件缩小比率

        # Category list
        PG_tabframe[1] = int(PG_tabframe[1] * height_ratio)
        PG_tabframedimensions[1] = int(PG_tabframedimensions[1] * height_ratio)

        # Program list
        PG_buttonframe[1] = int(PG_buttonframe[1] * height_ratio)
        PG_buttonframedimensions[1] = int(PG_buttonframedimensions[1] * height_ratio)


        # Search Bar
        SearchY = int( SearchY * height_ratio)

        # Search Picture
        SearchPicY = int( SearchPicY * height_ratio)

	# Menu Button
	for i in range(0, MenuButtonCount): 
	    MenuButtonY[i] = int(MenuButtonY[i] * height_ratio)
	
        # ---------------------低分辨率时--------------------------

        if lowresolution:
            MenuWidth    = int(MenuHeight * orig_menu_width / orig_menu_height) # 保持选单宽高比例
            width_ratio  = MenuWidth * 1.0 / orig_menu_width # 换成浮点数
            # category_scr size and  position
            PG_tabframe[0] = int(PG_tabframe[0] * width_ratio)
            PG_tabframedimensions[0] = int(PG_tabframedimensions[0] * width_ratio)
	    TabBackIconX = int(TabBackIconX * width_ratio)
	    TabBackIconY = int(TabBackIconY * height_ratio)
	    TabBackNameX = int(TabBackNameX * width_ratio)
	    TabBackNameY = int(TabBackNameY * height_ratio)

	    tab_back_size[0] = int(tab_back_size[0] * width_ratio)
	    tab_back_size[1] = int(tab_back_size[1] * height_ratio)

            PG_iconsize = int(PG_iconsize * width_ratio) # PG_iconsize 菜单条目图标，与程序列表共用

            # app_scr size and position
            PG_buttonframedimensions[0] = int(PG_buttonframedimensions[0] * width_ratio)
            PG_buttonframe[0] = int(PG_buttonframe[0] * width_ratio)

	    ButtonBackIconX = int(ButtonBackIconX * width_ratio)
	    ButtonBackIconY = int(ButtonBackIconY * height_ratio)
	    ButtonBackNameX = int(ButtonBackNameX * width_ratio)
	    ButtonBackNameY = int(ButtonBackNameY * height_ratio)

	    button_back_size[0] = int(button_back_size[0] * width_ratio)
	    button_back_size[1] = int(button_back_size[1] * height_ratio)

	    # search bar position
            SearchW = int( SearchW * width_ratio )
            SearchH = int( SearchH * height_ratio )
            SearchBgSize[0] = int(SearchBgSize[0] * width_ratio)
            SearchBgSize[1] = int(SearchBgSize[1] * height_ratio)
            SearchX = int( SearchX * width_ratio)

            # search picture position
            SearchPicW = int( SearchPicW * width_ratio )
            SearchPicH = int( SearchPicH * height_ratio )
            SearchPicX = int( SearchPicX * width_ratio)
	    # Menu Button

            for i in range(0, MenuButtonCount):
                MenuButtonX[i] = int(MenuButtonX[i] * width_ratio)
                MenuButtonW[i] = int(MenuButtonW[i] * width_ratio)
                MenuButtonH[i] = int(MenuButtonH[i] * height_ratio)
		MenuButtonNameOffsetX[i] = int(MenuButtonNameOffsetX[i] * width_ratio)
		MenuButtonNameOffsetY[i] = int(MenuButtonNameOffsetY[i] * height_ratio)
		MenuButtonIconX[i] = int(MenuButtonIconX[i] * width_ratio)
		MenuButtonIconY[i] = int(MenuButtonIconY[i] * height_ratio)
		MenuButtonIconSize[i] = int(MenuButtonIconSize[i] * width_ratio) # 因为其宽高相等, 以宽比率换算，可能会变形
            # --------- scale  processing  end -----------------------------------------
        
searchitem = ''

# color value from html format to decimal format
def color_translate(hexcolor):
    hexcolor = hexcolor.replace("#", "")
    octcolor = int(hexcolor, 16)
    red = (octcolor >> 16) & 0x0000ff
    green = (octcolor >> 8) & 0x0000ff
    blue = octcolor & 0x0000ff
    return red / 255.0, green / 255.0, blue / 255.0


try:
	ReloadSettings()
except:
	print '**WARNING** - Unable to load settings, using defaults'
	print "Traceback: \n" , sys.exc_info()
	SetDefaultSettings()
	ReloadSettings()

# Obtain OS default icon theme
DefaultIconTheme = gtk.settings_get_default().get_property("gtk-icon-theme-name")
GtkIconTheme = gtk.icon_theme_get_default()

distro_logo = gtk.icon_theme_get_default().lookup_icon('distributor-logo',48,gtk.ICON_LOOKUP_FORCE_SVG).get_filename()

#Application logo
Applogo = GraphicsDirectory +"logo.png"
BrokenImage = GraphicsDirectory + "/brokenlink.png"

gc.collect()

        
