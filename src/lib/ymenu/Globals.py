#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import division
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

DefaultSettings = { "Tab_Efect":1 , "Bind_Key":"Super_L" , "Sound_Theme":"None" , "Num_lock":"on", "flag":0, "Show_Tips":1 , "Distributor_Logo":0, "Menu_Name":"ylmfos" , "IconSize":24 , "ListSize":12 , "SuperL":1 , "Icon_Name":"ylmfos" , "Button_Name":"ylmfos" , "GtkColors":0 , "TabHover":1 , "Control_Panel":"gnome-control-center"  ,"Y_Center":"ycenter" , "Power":"gnome-session-save --shutdown-dialog" , "Logout":"gnome-session-save --logout-dialog" , "User":"gnome-about-me" , "AdminRun":"gksu", "MenuEditor":"gmenu-simple-editor"}

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
        global lowresolution, MenuButtonSize, VLineH, SearchBgSize, width_ratio, height_ratio, m_tabsize, tab_back_size, MFontSize, button_back_size
        MenuButtonSize = []
        MenuButtonSize.append((137, 30))
        MenuButtonSize.append((137, 30))
        MenuButtonSize.append((83, 28))
        MenuButtonSize.append((83, 28))
        
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

        # ----------------------------------------------------------------
        MenuButtonIconSize[0] = 24
        MenuButtonIconSize[1] = 24
        #VLine

        try:
            vlinepic = gtk.gdk.pixbuf_new_from_file(ImageDirectory + VLineImage)
            VLineH = vlinepic.get_height()
            del vlinepic
        except: VLineH = 457

        # Category tab's background m_tab.png
        m_tabsize = []
        try:
            tmppic = gtk.gdk.pixbuf_new_from_file( ImageDirectory + TabBackImage )
            m_tabsize.append(tmppic.get_width())
            m_tabsize.append(tmppic.get_height())
            del tmppic
        except:
            del m_tabsize
            m_tabsize = []
            m_tabsize.append(137)
            m_tabsize.append(30)
            pass
        tab_back_size = []
        try:
            sel = gtk.gdk.pixbuf_get_file_info(ImageDirectory + TabBackImage)
            tab_back_size.append(sel[1])
            tab_back_size.append(sel[2])
            sel = None
        except:
            del tab_back_size
            tab_back_size = []
            tab_back_size.append(137)
            tab_back_size.append(30)

        # App list button background size
        button_back_size = []
        try:
            sel = gtk.gdk.pixbuf_get_file_info(ImageDirectory + ButtonBackImage)
            button_back_size.append(sel[1])
            button_back_size.append(sel[2])
            sel = None
        except:
            del button_back_size
            button_back_size = []
            button_back_size.append(191)
            button_back_size.append(30)

        # SearchBar background
        SearchBgSize = []
        try:
            SearchBg = gtk.gdk.pixbuf_new_from_file(ImageDirectory + SearchBackground)
            SearchBgSize.append(SearchBg.get_width())
            SearchBgSize.append(SearchBg.get_height())
            del SearchBg
        except:
            del SearchBgSize
            SearchBgSize = [] # 防止上个Try有添加过数据
            SearchBgSize.append(191)
            SearchBgSize.append(25)


        # if encounter the low resolution monitor, scaled low the menu size --------------------
        width_ratio = 1
        height_ratio = 1
        MFontSize = 'medium'
        
        myscreensize = gtk.gdk.Screen.get_monitor_geometry(gtk.gdk.screen_get_default(), 0)

        if myscreensize.height < 768:
            orig_menu_width = MenuWidth
            orig_menu_height = MenuHeight
            MenuHeight = int( myscreensize.height / 2 ) # 高度为屏幕 1 / 2

            if MenuHeight < 350:
                    MenuHeight = 350
            
            #-------------------
            MFontSize = 'small'
            MenuWidth  = int( MenuHeight * orig_menu_width / orig_menu_height) # 保持选单宽高比例
            width_ratio  = MenuWidth / orig_menu_width
            height_ratio = MenuHeight / orig_menu_height # 参照菜单，控件缩小比率

            # Icon of Main Menu's size and position
            IconW = int( IconW * width_ratio )
            IconH = int( IconH * height_ratio )
            IconInW = int( IconInW * width_ratio )
            IconInH = int( IconInH * height_ratio )

            IconInX = int( IconInX * width_ratio )
            IconInY = int( IconInY * height_ratio )
            UserIconFrameOffsetX = int( UserIconFrameOffsetX * width_ratio )
            UserIconFrameOffsetY = int( UserIconFrameOffsetY * height_ratio )

            # category_scr size and  position
            PG_tabframe = int(PG_tabframe[0] * width_ratio), int(PG_tabframe[1] * height_ratio)
            PG_tabframedimensions = int(PG_tabframedimensions[0] * width_ratio), int(PG_tabframedimensions[1] * height_ratio)
            PG_iconsize = int( PG_iconsize * width_ratio )

            # Tab Back Icon, Label position
            TabBackNameX = int( TabBackNameX * width_ratio )
            TabBackNameY = int( TabBackNameY * height_ratio )
            TabBackIconX = int( TabBackIconX * width_ratio )
            TabBackIconY = int( TabBackIconY * height_ratio )

            tab_back_size.append(int( tab_back_size[0] * width_ratio ))
            tab_back_size.append(int( tab_back_size[1] * height_ratio ))
            del tab_back_size[0]
            del tab_back_size[0]

            # middle vline position = Category_Src's X + it's Width + 2 , do not change y
            VLineX = int(VLineX * width_ratio)
            VLineY = int(VLineY * height_ratio)
            VLineH = int(VLineH * height_ratio)

            # app_scr size and position
            PG_buttonframedimensions = int(PG_buttonframedimensions[0] * width_ratio), int(PG_buttonframedimensions[1] * height_ratio)
            PG_buttonframe = int(PG_buttonframe[0] * width_ratio), int(PG_buttonframe[1] * height_ratio)
            # the position of button name(label)
            ButtonBackNameX = int( ButtonBackNameX * width_ratio )
            ButtonBackNameY = int( ButtonBackNameY * height_ratio )
            # button size
            button_back_size.append(int(button_back_size[0] * width_ratio))
            button_back_size.append(int(button_back_size[1] * height_ratio))
            del button_back_size[0]
            del button_back_size[0]
            # button pozition
            ButtonBackIconX = int(ButtonBackIconX * width_ratio )
            ButtonBackIconY = int(ButtonBackIconX * height_ratio)

            # four button's size and position
            iconsize = int( MenuWidth * 24 / orig_menu_width )
            MenuButtonIconSize[0] = iconsize
            MenuButtonIconSize[1] = iconsize
            MenuButtonIconX[0] = int( MenuButtonIconX[0] * width_ratio )
            MenuButtonIconX[1] = int( MenuButtonIconX[1] * height_ratio )
            
            MenuButtonNameOffsetX[0] = int( MenuButtonNameOffsetX[0] * width_ratio ) # 四大按钮标签相对坐标偏移
            MenuButtonNameOffsetX[1] = int( MenuButtonNameOffsetX[1] * width_ratio )
            MenuButtonNameOffsetX[2] = int( MenuButtonNameOffsetX[2] * width_ratio )
            MenuButtonNameOffsetX[3] = int( MenuButtonNameOffsetX[3] * width_ratio )

            MenuButtonNameOffsetY[0] = int( MenuButtonNameOffsetY[0] * height_ratio )
            MenuButtonNameOffsetY[1] = int( MenuButtonNameOffsetY[1] * height_ratio )
            MenuButtonNameOffsetY[2] = int( MenuButtonNameOffsetY[2] * height_ratio )
            MenuButtonNameOffsetY[3] = int( MenuButtonNameOffsetY[3] * height_ratio )

            # control panel's position, x= x , y = Category_src's y + its height + 4
            NewMenuButtonSize = []
            NewMenuButtonSize.append((int( MenuButtonSize[0][0] * width_ratio ), int( MenuButtonSize[0][1] * height_ratio )))
            NewMenuButtonSize.append((int( MenuButtonSize[1][0] * width_ratio ), int( MenuButtonSize[1][1] * height_ratio )))
            NewMenuButtonSize.append((int( MenuButtonSize[2][0] * width_ratio ), int( MenuButtonSize[2][1] * height_ratio )))
            NewMenuButtonSize.append((int( MenuButtonSize[3][0] * width_ratio ), int( MenuButtonSize[3][1] * height_ratio )))
            del MenuButtonSize
            MenuButtonSize = NewMenuButtonSize

            MenuButtonX[0] = PG_tabframe[0]
            MenuButtonY[0] = int( MenuButtonY[0] * height_ratio )

            MenuButtonX[1] = MenuButtonX[0]
            MenuButtonY[1] = int( MenuButtonY[1] * height_ratio )

            MenuButtonX[2] = int( MenuButtonX[2] * width_ratio )
            MenuButtonY[2] = int( MenuButtonY[2] * height_ratio )

            MenuButtonX[3] = int( MenuButtonX[3] * width_ratio )
            MenuButtonY[3] = int( MenuButtonY[3] * height_ratio )

            # search bar position

            SearchW = int( SearchW * width_ratio )
            SearchH = int( SearchH * height_ratio )
            SearchBgSize.append(int(SearchBgSize[0] * width_ratio))
            SearchBgSize.append(int(SearchBgSize[1] * height_ratio))
            del SearchBgSize[0]
            del SearchBgSize[0]
            SearchX = PG_buttonframe[0] # 与App_Scr X坐标相同
            SearchY = int( SearchY * height_ratio )

            lowresolution = True


        # ---------------------------------------------------------------------------------------
        
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

        
