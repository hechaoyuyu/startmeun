#!/usr/bin/env python
# -*- coding:utf-8 -*-

import gtk
import gc
import os
import xml.dom.minidom
import backend
import sys
try:
	INSTALL_PREFIX = open("/etc/ymenu/prefix").read()[:-1]
except:
	INSTALL_PREFIX = '/usr'

try:
	import numpy
	Has_Numpy = True
except:
	Has_Numpy = False
	print 'python numpy not installed , some effects and gtk native colors wont be available'
        
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
TransitionS = 	25 #step update speed in miliseconds
TransitionQ = 0.05 #step update transparency 0 to 1
FirstUse = False

DefaultSettings = { "Tab_Efect":1 , "Bind_Key":"Super_L" , "Sound_Theme":"None" , "Num_lock":"on", "Show_Tips":1 , "Distributor_Logo":0, "Menu_Name":"ylmfos" , "IconSize":24 , "ListSize":12 , "SuperL":1 , "Icon_Name":"ylmfos" , "Button_Name":"ylmfos" , "GtkColors":0 , "TabHover":1 , "Control_Panel":"gnome-control-center"  ,"Y_Center":"ycenter" , "Power":"gnome-session-save --shutdown-dialog" , "Logout":"gnome-session-save --logout-dialog" , "User":"gnome-about-me" , "AdminRun":"gksu", "MenuEditor":"gmenu-simple-editor"}

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
	global orientation, panel_size, flip, MenuActions, MenuCommands, ImageDirectory, Actions, IconDirectory, MenuButtonDirectory, ThemeColor, ShowTop, FirstUse, StartMenuTemplate, ThemeColorCode,ThemeColorHtml, NegativeThemeColorCode, MenuWidth, MenuHeight, IconW, IconH, IconInX, IconInY, IconInW, IconInH, SearchX, SearchY, SearchW, SearchH, SearchIX, SearchIY, SearchInitialText,SearchTextColor, SearchBackground, SearchWidget, SearchWidgetPath, UserIconFrameOffsetX, UserIconFrameOffsetY, UserIconFrameOffsetH, UserIconFrameOffsetW, PG_tabframe, PG_tabframedimensions, PG_buttonframe, PG_buttonframedimensions, MenuHasSearch, MenuHasIcon, MenuHasFade, MenuHasTab, CairoSearchTextColor, CairoSearchBackColor, CairoSearchBorderColor, CairoSearchRoundAngle, PG_iconsize,RI_numberofitems, MenuButtonCount, MenuButtonNames, MenuButtonMarkup, MenuButtonNameOffsetX, MenuButtonNameOffsetY, MenuButtonCommands, MenuButtonX,MenuButtonY, MenuButtonImage, MenuButtonImageBack, ButtonBackImage, ButtonBackIconX, ButtonBackIconY, ButtonBackNameX, ButtonBackNameY, TabBackImage, TabBackIconX, TabBackIconY, TabBackNameX, TabBackNameY, VLineImage, VLineX, VLineY, MenuButtonIcon, MenuButtonIconSel, MenuButtonIconX,MenuButtonIconY,MenuButtonIconSize, MenuButtonSub,MenuButtonClose, MenuCairoIconButton, ButtonHasTop, ButtonBackground, ButtonTop, StartButton, StartButtonTop, ButtonHasBottom, MenuButtonNameAlignment, GtkColorCode

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
	MenuActions.append('Control Panel')
	MenuCommands.append(Settings['Control_Panel'])
        MenuActions.append('Y Center')
	MenuCommands.append(Settings['Y_Center'])
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
		
	# Load Background Image
	SBase = XBase.getElementsByTagName("Background")
	StartMenuTemplate = SBase[0].attributes["Image"].value
	
	try:
		im = gtk.gdk.pixbuf_new_from_file('%s%s' % (ImageDirectory, StartMenuTemplate))
		MenuWidth = im.get_width()
		MenuHeight = im.get_height()
	except:
	# Load WindowDimensions
		SBase = XBase.getElementsByTagName("WindowDimensions")
		MenuWidth = int(SBase[0].attributes["Width"].value)
		MenuHeight = int(SBase[0].attributes["Height"].value)

	# Load WindowDimensions

	SBase = XBase.getElementsByTagName("IconSettings")
	try:
		UserIconFrameOffsetX = int(SBase[0].attributes["X"].value)
		UserIconFrameOffsetW = int(SBase[0].attributes["Width"].value)
		UserIconFrameOffsetH = int(SBase[0].attributes["Height"].value)
		if orientation == 'botton':
			UserIconFrameOffsetY = int(SBase[0].attributes["Y"].value)
	
		elif orientation == 'top':
	
			UserIconFrameOffsetY =  MenuHeight - int(SBase[0].attributes["Y"].value) - UserIconFrameOffsetH
		else:
			UserIconFrameOffsetY = int(SBase[0].attributes["Y"].value)
	
		IconW = int(SBase[0].attributes["Width"].value)
		IconH = int(SBase[0].attributes["Height"].value)
		IconInX = int(SBase[0].attributes["InsetX"].value)
		IconInY = int(SBase[0].attributes["InsetY"].value)
		IconInW = int(SBase[0].attributes["InsetWidth"].value)
		IconInH = int(SBase[0].attributes["InsetHeight"].value)
	except:pass
        
        # Load TabBackground Image
        try:
                SBase = XBase.getElementsByTagName("TabBackground")
                TabBackImage = SBase[0].attributes["Image"].value
                TabBackIconX = int(SBase[0].attributes["TabIconX"].value)
                TabBackIconY = int(SBase[0].attributes["TabIconY"].value)
                TabBackNameX = int(SBase[0].attributes["TextX"].value)
                TabBackNameY = int(SBase[0].attributes["TextY"].value)
        
                # Load VLine Image
                SBase = XBase.getElementsByTagName("VLine")
                VLineImage = SBase[0].attributes["Image"].value
                VLineX = int(SBase[0].attributes["X"].value)
                VLineY = int(SBase[0].attributes["Y"].value)
        
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
			
        # Load ProGramTabSettings
        try:
                SBase = XBase.getElementsByTagName("ProgramTabSettings")
                PG_tabframedimensions = int(SBase[0].attributes["Width"].value),int(SBase[0].attributes["Height"].value)
                PG_tabframe = int(SBase[0].attributes["X"].value),int(SBase[0].attributes["Y"].value)
        except:pass
        
	# Load ProgramListSettings
	SBase = XBase.getElementsByTagName("ProgramListSettings")
	PG_buttonframedimensions = int(SBase[0].attributes["Width"].value),int(SBase[0].attributes["Height"].value)
	if orientation == 'botton':
		PG_buttonframe = int(SBase[0].attributes["X"].value),int(SBase[0].attributes["Y"].value)
	elif orientation == 'top':
		PG_buttonframe = int(SBase[0].attributes["X"].value),MenuHeight - int(SBase[0].attributes["Y"].value) - int(PG_buttonframedimensions[1])
	else:
		PG_buttonframe = int(SBase[0].attributes["X"].value),int(SBase[0].attributes["Y"].value)
	
	# Load Capabilities
	SBase = XBase.getElementsByTagName("Capabilities")
	MenuHasSearch = int(SBase[0].attributes["HasSearch"].value)
	MenuHasIcon = int(SBase[0].attributes["HasIcon"].value)
	MenuHasFade = int(SBase[0].attributes["HasFadeTransition"].value)
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
                     
searchitem = ''

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

#User Image
UserImageFrame = ImageDirectory+"user-image-frame.png"
DefaultUserImage = IconDirectory+"gtk-missing-image.png"
UserFace = UserImage = HomeDirectory + "/.face"
if os.path.isfile(UserImage) == 0 or os.path.exists(UserImage) == 0:
    UserImage=DefaultUserImage

#Application logo
Applogo = GraphicsDirectory +"logo.png"
BrokenImage = GraphicsDirectory + "/brokenlink.png"

gc.collect()

        
