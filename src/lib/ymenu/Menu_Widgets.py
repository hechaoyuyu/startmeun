#!/usr/bin/env python
# -*- coding:utf-8 -*-

import pygtk
pygtk.require("2.0")
import gtk
import cairo
import gobject
import pango
import os
import commands
import Globals
import IconFactory
import cairo_drawing
import time
import gconf
from Popup_Menu import add_menuitem, add_image_menuitem
import gc
import gio
import urllib
import xdg.DesktopEntry
import xdg.Menu
from execute import *
from user import home

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
gettext.install('ymenu', INSTALL_PREFIX + '/share/locale')
gettext.bindtextdomain('ymenu', INSTALL_PREFIX + '/share/locale')

def _(s):
    return gettext.gettext(s)

class MenuButton:
    def __init__(self, i, base, backimage):
        # base > EventBox > Fixed > All the rest
        self.i = i
        self.backimagearea = None
        self.Button = gtk.EventBox()
        self.Frame = gtk.Fixed()
        if not self.Button.is_composited(): 
            self.supports_alpha = False
        else:
            self.supports_alpha = True
        self.Button.connect("composited-changed", self.composite_changed)
        self.Button.connect("enter_notify_event", self.enter, self.i)
        self.Button.connect("leave_notify_event", self.leave, self.i)
        self.Frame.connect("expose_event", self.expose)
        self.Button.add(self.Frame)

        if Globals.MenuButtonIcon[i]:
            self.Icon = gtk.Image()
            self.SetIcon(Globals.ImageDirectory + Globals.MenuButtonIcon[i])
		
        self.Image = gtk.Image()

        self.Setimage(Globals.ImageDirectory + Globals.MenuButtonImage[i])
        self.w = self.pic.get_width()
        self.h = self.pic.get_height()
        if self.backimagearea is None:
            if Globals.flip == False:
                self.backimagearea = backimage.subpixbuf(Globals.MenuButtonX[i], Globals.MenuHeight - Globals.MenuButtonY[i] - self.h, self.w, self.h)
                self.backimagearea = self.backimagearea.flip(Globals.flip)
            else:
                self.backimagearea = backimage.subpixbuf(Globals.MenuButtonX[i], Globals.MenuButtonY[i], self.w, self.h)
        # Set the background which is always present
        self.BackgroundImage = gtk.Image()
        if Globals.MenuButtonImageBack[i] != '':
            self.BackgroundImage.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(Globals.ImageDirectory + Globals.MenuButtonImageBack[i]))
        else:
            self.BackgroundImage.set_from_pixbuf(None)
        self.Image.set_size_request(self.w, self.h)
        self.Frame.set_size_request(self.w, self.h)
        self.SetBackground()

        self.Frame.put(self.BackgroundImage, 0, 0)
        self.Frame.put(self.Image, 0, 0)
        if Globals.MenuButtonIcon[i]:
            self.Frame.put(self.Icon, Globals.MenuButtonIconX[i], Globals.MenuButtonIconY[i])
        self.Label = gtk.Label()
        self.txt = Globals.MenuButtonMarkup[i]
        try:
            self.txt = self.txt.replace(Globals.MenuButtonNames[i], _(Globals.MenuButtonNames[i]))
        except:pass
        self.Label.set_markup(self.txt)

        self.Frame.put(self.Label, Globals.MenuButtonNameOffsetX[i], Globals.MenuButtonNameOffsetY[i])
        if self.Label.get_text() == '' or Globals.Settings['Show_Tips']:
            self.Frame.set_tooltip_text(_(Globals.MenuButtonNames[i]))
        base.put(self.Button, Globals.MenuButtonX[i], Globals.MenuButtonY[i])
        #gc.collect()

    def composite_changed(self, widget):
		
        if not self.Button.is_composited():	 
            self.supports_alpha = False
        else:
            self.supports_alpha = True

    def expose (self, widget, event):
        self.ctx = widget.window.cairo_create()
        # set a clip region for the expose event
        if self.supports_alpha == False:
            self.ctx.set_source_rgb(1, 1, 1)
        else:
            self.ctx.set_source_rgba(1, 1, 1, 0)
        self.ctx.set_operator (cairo.OPERATOR_SOURCE)
        self.ctx.paint()
        cairo_drawing.draw_pixbuf(self.ctx, self.backimagearea)
	  
    def SetIcon(self, filename):
        # If the menu has an icon on top, then add that
        try:
            if Globals.MenuButtonIconSize[self.i] != 0:
                self.ww = Globals.MenuButtonIconSize[self.i]
                self.hh = self.ww
                self.Pic = gtk.gdk.pixbuf_new_from_file_at_size(filename, self.ww, self.hh)
            else:
                self.ww = self.hh = 24
			
            if Globals.MenuButtonIcon[self.i]:
                self.ico = IconFactory.GetSystemIcon(Globals.MenuButtonIcon[self.i])
                if not self.ico:
                    self.ico = filename
                self.Pic = gtk.gdk.pixbuf_new_from_file_at_size(self.ico, self.ww, self.hh)
            self.Icon.set_from_pixbuf(self.Pic)
        except:print 'error on button seticon'  + filename
				
    def enter (self, widget, event, i):

        if Globals.Settings['Tab_Efect'] != 0 and Globals.MenuButtonIcon[i]:
            #增大
            if Globals.Settings['Tab_Efect'] == 1: #grow
                self.Pic = gtk.gdk.pixbuf_new_from_file_at_size(self.ico, self.ww + 2, self.hh + 2)

            #黑白
            elif Globals.Settings['Tab_Efect'] == 2:#bw
                self.Pic = gtk.gdk.pixbuf_new_from_file_at_size(self.ico, self.ww, self.hh)
                self.Pic.saturate_and_pixelate(self.Pic, 0.0, False)
            #模糊
            elif Globals.Settings['Tab_Efect'] == 3:#Blur

                colorpb = gtk.gdk.pixbuf_new_from_file_at_size(self.ico, self.ww, self.hh)
                alpha = 255#int(int(70) * 2.55 + 0.2)
                tk = 2
                bg = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, self.ww, self.hh)
                bg.fill(0x00000000)
                glow = bg.copy()
                # Prepare the glow that should be put bind the icon
                tk1 = tk - int(tk / 2)
                for x, y in ((-tk1, -tk1), (-tk1, tk1), (tk1, -tk1), (tk1, tk1)):
                    colorpb.composite(glow, 0, 0, self.ww, self.hh, x, y, 1, 1, gtk.gdk.INTERP_BILINEAR, 170)
                for x, y in ((-tk, -tk), (-tk, tk), (tk, -tk), (tk, tk)):
                    colorpb.composite(glow, 0, 0, self.ww, self.hh, x, y, 1, 1, gtk.gdk.INTERP_BILINEAR, 70)
                glow.composite(bg, 0, 0, self.ww, self.hh, 0, 0, 1, 1, gtk.gdk.INTERP_BILINEAR, alpha)
                self.Pic = bg
				
            #醒目
            elif Globals.Settings['Tab_Efect'] == 4:#glow
                r = 255
                g = 255
                b = 0
                self.Pic = gtk.gdk.pixbuf_new_from_file_at_size(self.ico, self.ww, self.hh)
                colorpb = self.Pic.copy()
                for row in colorpb.get_pixels_array():
                    for pix in row:
                        pix[0] = r
                        pix[1] = g
                        pix[2] = b
	
                alpha = 255#int(int(70) * 2.55 + 0.2)
                tk = 2
                bg = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, self.ww, self.hh)
                bg.fill(0x00000000)
                glow = bg.copy()
                # Prepare the glow that should be put bind the icon
                tk1 = tk - int(tk / 2)
                for x, y in ((-tk1, -tk1), (-tk1, tk1), (tk1, -tk1), (tk1, tk1)):
                    colorpb.composite(glow, 0, 0, self.ww, self.hh, x, y, 1, 1, gtk.gdk.INTERP_BILINEAR, 170)
                for x, y in ((-tk, -tk), (-tk, tk), (tk, -tk), (tk, tk)):
                    colorpb.composite(glow, 0, 0, self.ww, self.hh, x, y, 1, 1, gtk.gdk.INTERP_BILINEAR, 70)
                glow.composite(bg, 0, 0, self.ww, self.hh, 0, 0, 1, 1, gtk.gdk.INTERP_BILINEAR, alpha)
                self.Pic.composite(bg, 0, 0, self.ww, self.hh, 0, 0, 1, 1, gtk.gdk.INTERP_BILINEAR, 255)
                self.Pic = bg

            #加深
            elif Globals.Settings['Tab_Efect'] == 5:#saturate
                self.Pic = gtk.gdk.pixbuf_new_from_file_at_size(self.ico, self.ww, self.hh)
                self.Pic.saturate_and_pixelate(self.Pic, 6.0, False)
					
            self.Icon.set_from_pixbuf(self.Pic)

    def leave (self, widget, event, i):
        if Globals.Settings['Tab_Efect'] != 0 and Globals.MenuButtonIcon[i]:
            self.Pic = gtk.gdk.pixbuf_new_from_file_at_size(self.ico, self.ww, self.hh)
            self.Icon.set_from_pixbuf(self.Pic)
                
    def Setimage(self, imagefile):
        # The image is background when it's not displaying the overlay
        self.pic = gtk.gdk.pixbuf_new_from_file(imagefile)
        self.Image.set_from_pixbuf(self.pic)

    def SetBackground(self):
        self.Image.set_from_pixbuf(None)


class MenuImage:
    def __init__(self, i, base, backimage):
        self.backimagearea = None
        self.Frame = gtk.Fixed()
        if not self.Frame.is_composited():
	 
            self.supports_alpha = False
        else:
            self.supports_alpha = True
        self.Frame.connect("composited-changed", self.composite_changed)
        self.Image = gtk.Image()
        self.Pic = gtk.gdk.pixbuf_new_from_file(Globals.ImageDirectory + Globals.MenuImage[i])
        self.w = self.Pic.get_width()
        self.h = self.Pic.get_height()
		
        ico = IconFactory.GetSystemIcon(Globals.MenuImage[i])
        if not ico:
            ico = Globals.ImageDirectory + Globals.MenuImage[i]
        self.Pic = gtk.gdk.pixbuf_new_from_file_at_size(ico, self.w, self.h)

        if self.backimagearea is None:
            if Globals.flip == False:
                self.backimagearea = backimage.subpixbuf(Globals.MenuImageX[i], Globals.MenuHeight - Globals.MenuImageY[i] - self.h, self.w, self.h)
                self.backimagearea = self.backimagearea.flip(Globals.flip)
            else:
                self.backimagearea = backimage.subpixbuf(Globals.MenuImageX[i], Globals.MenuImageY[i], self.w, self.h)
        self.Pic.composite(self.backimagearea, 0, 0, self.w, self.h, 0, 0, 1, 1, gtk.gdk.INTERP_BILINEAR, 255)
        # Set the background which is always present
        self.Image.set_from_pixbuf(self.backimagearea)
        self.Image.set_size_request(self.w, self.h)
        self.Frame.set_size_request(self.w, self.h)
        self.Frame.put(self.Image, 0, 0)
        base.put(self.Frame, Globals.MenuImageX[i], Globals.MenuImageY[i])
        #gc.collect()

    def composite_changed(self, widget):
		
        if not self.Frame.is_composited():
	 
            self.supports_alpha = False
        else:
            self.supports_alpha = True


    def expose (self, widget, event):
		
        self.ctx = widget.window.cairo_create()
        # set a clip region for the expose event
        if self.supports_alpha == False:
            self.ctx.set_source_rgb(1, 1, 1)
        else:
            self.ctx.set_source_rgba(1, 1, 1, 0)
        self.ctx.set_operator (cairo.OPERATOR_SOURCE)
        self.ctx.paint()


class ImageFrame:
    def __init__(self, w, h, ix, iy, iw, ih, base, backimage):
        self.backimagearea = None
        self.w = w
        self.h = h
        #print w,h,iw,ih,ix,iy
        self.ix = ix
        self.iy = iy
        self.iw = iw
        self.ih = ih
        self.base = base
        self.timer = None
        self.icons = [None, None, None, None]
        self.iconopacity = [0, 0, 0, 0]
        self.step = [0, 0, 0, 0]
        self.intrans = False
        self.Pic = None
        self.frame_window = gtk.EventBox()
        if not self.frame_window.is_composited():
	 
            self.supports_alpha = False
        else:
            self.supports_alpha = True
        self.Frame = gtk.Fixed()
        self.Image = gtk.Image()
        self.frame_window.set_tooltip_text(_('About Me'))
        self.frame_window.connect("button-press-event", self.but_click)
        self.frame_window.connect("composited-changed", self.composite_changed)
        self.Frame.connect('expose-event', self.expose)
        self.frame_window.add(self.Frame)
        self.frame_window.set_size_request(w, h)
        # Grab the background pixels from under the location of the menu button

        #self.backimagearea = self.backimagearea.add_alpha(True, chr(0xff), chr(0xff), chr(0xff))
        if self.backimagearea is None:
	
            if Globals.flip == False:

                self.backimagearea = backimage.subpixbuf(Globals.UserIconFrameOffsetX, Globals.MenuHeight - Globals.UserIconFrameOffsetY - self.h, self.w, self.h)
                self.backimagearea = self.backimagearea.flip(Globals.flip)
	
            else:
                self.backimagearea = backimage.subpixbuf(Globals.UserIconFrameOffsetX, Globals.UserIconFrameOffsetY, self.w, self.h)
        # Set the background which is always present
        self.Image.set_size_request(self.w, self.h)
        self.Frame.set_size_request(self.w, self.h)
        self.SetBackground()
        self.Frame.put(self.Image, 0, 0)
        self.base.put(self.frame_window, self.ix, self.iy)
        self.Pic = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, self.w, self.h)
        self.Pic.fill(0x00000000)
        #gc.collect()


    def expose (self, widget, event):
        self.ctx = widget.window.cairo_create()
        # set a clip region for the expose event
        if self.supports_alpha == False:
            self.ctx.set_source_rgb(1, 1, 1)
        else:
            self.ctx.set_source_rgba(1, 1, 1, 0)
        self.ctx.set_operator (cairo.OPERATOR_SOURCE)
        self.ctx.paint()
        cairo_drawing.draw_pixbuf(self.ctx, self.backimagearea)

    def composite_changed(self, widget):
        print self.frame_window.is_composited()

    def screen_changed(self, widget):
        # Screen change event
        screen = widget.get_screen()
        colormap = screen.get_rgba_colormap()
        widget.set_colormap(colormap)

    def Setimage(self):
        # The image is background when it's not displaying the overlay
        self.Image.set_from_pixbuf(None)
        self.Pic = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, self.w, self.h)
        self.Pic.fill(0x00000000)
        bg = self.Pic.copy()
        for i in range(0, len(self.iconopacity)):
            if self.icons[i] != None and self.iconopacity[i] > 0:
                if i == 1:
                    self.icons[i].composite(self.Pic, self.ix, self.iy, self.icons[i].get_width(), self.icons[i].get_height(), self.ix, self.iy, 1, 1, gtk.gdk.INTERP_BILINEAR, int(self.iconopacity[i] * 255))
                else:
                    self.icons[i].composite(self.Pic, 0, 0, self.icons[i].get_width(), self.icons[i].get_height(), 0, 0, 1, 1, gtk.gdk.INTERP_BILINEAR, int(self.iconopacity[i] * 255))
        #print "#"*10,self.Pic,"#"*10,len(self.iconopacity)
        self.Image.set_from_pixbuf(self.Pic)

    def SetBackground(self):
        self.Image.set_from_pixbuf(None)


    def but_click(self, widget, event):
        os.system(Globals.Settings['User'] + ' &')


    def move(self, x, y):
        # Relocate the window
        self.base.move(self.frame_window, x, y)

    def transition(self, step, speed, rate, termination_event):
        if self.timer:
            gobject.source_remove(self.timer)
            self.intrans = False
            self.Pic = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, self.w, self.h)
            self.Pic.fill(0x00000000)
		
        if step != self.step:
            if self.timer:
                gobject.source_remove(self.timer)
                self.intrans = False
        self.step = step
        if self.intrans == False:
            self.intrans = True
            # Add timer
            self.Pic = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, self.w, self.h)
            self.Pic.fill(0x00000000)
            self.timer = gobject.timeout_add(speed, self.updatefade, termination_event, rate)

    def updatefade(self, termination_event, rate):

        if self.step == [0, 0, 0, 0]:
            self.intrans = False
            if termination_event:
                termination_event()
            return False
        for i in range(0, len(self.iconopacity)):
            self.iconopacity[i] = self.iconopacity[i] + round((rate * self.step[i]), 2)
            if self.iconopacity[i] < 0: self.iconopacity[i] = 0
            if self.iconopacity[i] > 1: self.iconopacity[i] = 1
            if (self.iconopacity[i] <= 0 or self.iconopacity[i] >= 1) and self.step[i] != 0:
                self.step[i] = 0
				
                self.iconopacity[i] = int(self.iconopacity[i])
            self.iconopacity[i] = round(self.iconopacity[i], 2)
		
        self.Setimage()
        if self.step == [0, 0, 0, 0]:
            self.Pic = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, self.w, self.h)
            self.Pic.fill(0x00000000)
            self.intrans = False
            if termination_event:
                termination_event()
            return False
        return True


    def updateimage(self, index, imagefile):
        #print "##"*10,imagefile,"##"*10
            # All .face files will load through this routine, even though they may be 'png' format

        if index == 1:

            self.temp = gtk.gdk.pixbuf_new_from_file(imagefile).scale_simple(self.iw, self.ih, gtk.gdk.INTERP_BILINEAR)

        elif index == 0:

            self.temp = gtk.gdk.pixbuf_new_from_file(imagefile)
            self.w = self.temp.get_width()
            self.h = self.temp.get_height()
        else:
            try:
                self.temp = gtk.gdk.pixbuf_new_from_file_at_size(imagefile, self.w, self.h)
            except:
                print 'Warning: icon %s not found in ymenu icons, trying system icons instead!' % imagefile
                image = IconFactory.GetSystemIcon(imagefile.split('/').pop())
                if not image:
                    print 'Warning: icon %s was not found in system icons either!' % imagefile
                    image = IconFactory.GetSystemIcon('gtk-missing-image')
				
                self.temp = gtk.gdk.pixbuf_new_from_file_at_size(image, self.w, self.h)
        if index == 0:
            #FRAME
            self.icons[0] = self.temp
        if index == 1:
            #.FACE
            self.icons[1] = self.temp
        if index == 2:
            #1ST ICON
            self.icons[2] = self.temp
        if index == 3:
            #2ND ICON
            self.icons[3] = self.temp

class GtkSearchBar(gtk.EventBox, gobject.GObject):
    __gsignals__ = {
        'right-clicked': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
    }
        
    def __init__(self, BackImageFile, W, H, win):
        gtk.EventBox.__init__(self)
        gobject.GObject.__init__(self)

        self.Frame = gtk.Fixed()
        self.set_visible_window(0)
        self.add(self.Frame)

        self.win = win
        self.entry = gtk.Entry()
        self.entry.set_inner_border(None)
        self.back = gtk.Image()

        self.entry.set_size_request(W, H)

        sel = gtk.gdk.pixbuf_new_from_file(BackImageFile)
        self.back.set_from_pixbuf(sel)

        if Globals.Settings['GtkColors'] == 0:
            self.entry.modify_base(gtk.STATE_NORMAL, Globals.ThemeColorCode)
                        
        self.entry.set_text(_('Search'))
        self.entry.set_has_frame(False)
        self.entry.set_max_length(20)
                
        self.entry.connect("button-press-event", self.enter)
        self.entry.connect("leave_notify_event", self.leave)
                
        if Globals.Settings['GtkColors'] == 0:
            self.entry.modify_text(gtk.STATE_NORMAL, Globals.NegativeThemeColorCode)

        self.Frame.put(self.back, 0, 0)
        self.Frame.put(self.entry, 6, 3)

    def enter(self, widget, event):
        print event.type
        if event.type == gtk.gdk.BUTTON_PRESS:event_button = event.button
        elif event.type == gtk.gdk.BUTTON_RELEASE:event_button = event.button
        else:event_button = event.button
        if event_button == 1:
            if widget.get_text() == _('Search'):
                widget.set_text("")
    
        if event_button == 3:
            self.emit('right-clicked')
                
        if widget.get_text() == _('Search'):
            widget.set_text("")
                        
    def leave(self, widget, event):
        if widget.get_text() == '':
            self.win.set_focus(None)
            widget.set_text(_('Search'))
				
class IconManager(gobject.GObject):

    __gsignals__ = {
        "changed": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
    }

    def __init__(self):
        gobject.GObject.__init__(self)
        self.icons = {}
        self.count = 0

        # Some apps don't put a default icon in the default theme folder, so we will search all themes
        def createTheme(d):
            theme = gtk.IconTheme()
            theme.set_custom_theme(d)
            return theme

        # This takes to much time and there are only a very few applications that use icons from different themes
        #self.themes = map(  createTheme, [ d for d in os.listdir( "/usr/share/icons" ) if os.path.isdir( os.path.join( "/usr/share/icons", d ) ) ] )

        defaultTheme = gtk.icon_theme_get_default()
        defaultKdeTheme = createTheme("kde.default")

        # Themes with the same content as the default them aren't needed
        #self.themes = [ theme for theme in self.themes if  theme.list_icons() != defaultTheme.list_icons() ]

        self.themes = [defaultTheme, defaultKdeTheme]

        self.cache = {}

        # Listen for changes in the themes
        for theme in self.themes:
            theme.connect("changed", self.themeChanged)


    def getIcon(self, iconName, iconSize):
        if not iconName:
            return None

        try:
            #[ iconWidth, iconHeight ] = self.getIconSize( iconSize )
            if iconSize <= 0:
                return None

            if iconName in self.cache and iconSize in self.cache[iconName]:
                iconFileName = self.cache[iconName][iconSize]
            elif os.path.isabs(iconName):
                iconFileName = iconName
            else:
                if iconName[-4:] in [".png", ".xpm", ".svg", ".gif"]:
                    realIconName = iconName[:-4]
                else:
                    realIconName = iconName
                tmp = None
                for theme in self.themes:
                    if theme.has_icon(realIconName):
                        tmp = theme.lookup_icon(realIconName, iconSize, 0)
                        if tmp:
                            break

                if tmp:
                    iconFileName = tmp.get_filename()
                else:
                    iconFileName = ""

            if iconFileName and os.path.exists(iconFileName):
                icon = gtk.gdk.pixbuf_new_from_file_at_size(iconFileName, iconSize, iconSize)
            else:
                icon = None


            # if the actual icon size is to far from the desired size resize it
            if icon and ((icon.get_width() - iconSize) > 5 or (icon.get_height() - iconSize) > 5):
                if icon.get_width() > icon.get_height():
                    newIcon = icon.scale_simple(iconSize, icon.get_height() * iconSize / icon.get_width(), gtk.gdk.INTERP_BILINEAR)
                else:
                    newIcon = icon.scale_simple(icon.get_width() * iconSize / icon.get_height(), iconSize, gtk.gdk.INTERP_BILINEAR)
                del icon
                icon = newIcon

            if iconName in self.cache:
                self.cache[iconName][iconSize] = iconFileName
            else:
                self.cache[iconName] = {iconSize: iconFileName}

            return icon
        except Exception, e:
            print "Exception " + e.__class__.__name__ + ": " + e.message
            return None

    def themeChanged(self, theme):
        self.cache = {}
        self.emit("changed")

gobject.type_register(IconManager)

class CategoryTab(gtk.EventBox):
    #CategoryTab(i,addedCategories[i]["icon"],Globals.PG_iconsize,addedCategories[i]["name"],addedCategories[i]["tooltip"])
    def __init__(self, iconName, iconSize, name):
        gtk.EventBox.__init__(self)
        
        self.Name = name
        self.connections = []
        self.Frame = gtk.Fixed()
        self.set_visible_window(0)
        self.add(self.Frame)
        
        #Tab背景
        self.Image = gtk.Image()
        sel = gtk.gdk.pixbuf_get_file_info(Globals.ImageDirectory + Globals.TabBackImage)
	self.w = sel[1]
	self.h = sel[2]
	sel = None
        self.Image.set_from_pixbuf(None)
        self.Image.set_size_request(self.w, self.h)
        self.Frame.set_size_request(self.w, self.h)
        self.Frame.put(self.Image, 0, 0)
        
        #Tab上的图标
        self.iconName = iconName
        self.iconSize = iconSize
        icon = self.getIcon(self.iconSize)
        self.buttonImage = gtk.Image()
        if icon:
            self.buttonImage.set_from_pixbuf(icon)
            del icon
        else:
            self.buttonImage.set_size_request(self.iconSize, self.iconSize)
        self.Frame.put(self.buttonImage, Globals.TabBackIconX, Globals.TabBackIconY)

        #Tab上的文字
        self.Label = gtk.Label()
        self.txt = "<span foreground=\"#FFFFFF\">%s</span>" % name
        self.Label.set_alignment(0, 0)
        self.Label.set_markup(self.txt)
	self.Frame.put(self.Label, Globals.TabBackNameX, Globals.TabBackNameY)
        
        self.connectSelf("destroy", self.onDestroy)
        self.connectSelf("enter_notify_event", self.enter)
        self.connectSelf("leave_notify_event", self.leave)
        self.themeChangedHandlerId = iconManager.connect("changed", self.themeChanged)
      
    def connectSelf(self, event, callback):
        self.connections.append(self.connect(event, callback))    
        
    def getIcon (self, iconSize):
        #if not self.iconName:
        #    return None

        icon = iconManager.getIcon(self.iconName, iconSize)
        if not icon:
            icon = iconManager.getIcon("application-default-icon", iconSize)

        return icon

    def enter (self, widget, event):
        icon = self.getIcon(self.iconSize)
        if Globals.Settings['Tab_Efect'] != 0:
            #增大
            if Globals.Settings['Tab_Efect'] == 1: #grow
                icon = self.getIcon(self.iconSize + 2)

            #黑白
            elif Globals.Settings['Tab_Efect'] == 2:#bw
                icon.saturate_and_pixelate(icon, 0.0, False)
            
            #模糊
            elif Globals.Settings['Tab_Efect'] == 3:#Blur
		alpha = 255#int(int(70) * 2.55 + 0.2)
		tk = 2
		bg = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, self.w, self.h)
		bg.fill(0x00000000)
		glow = bg.copy()
		# Prepare the glow that should be put bind the icon
		tk1 = tk - int(tk / 2)
		for x, y in ((-tk1, -tk1), (-tk1, tk1), (tk1, -tk1), (tk1, tk1)):
                    icon.composite(glow, 0, 0, self.w, self.h, x, y, 1, 1, gtk.gdk.INTERP_BILINEAR, 170)
		for x, y in ((-tk, -tk), (-tk, tk), (tk, -tk), (tk, tk)):
                    icon.composite(glow, 0, 0, self.w, self.h, x, y, 1, 1, gtk.gdk.INTERP_BILINEAR, 70)
		glow.composite(bg, 0, 0, self.w, self.h, 0, 0, 1, 1, gtk.gdk.INTERP_BILINEAR, alpha)
		icon = bg
                
            #醒目
            elif Globals.Settings['Tab_Efect'] == 4:#glow
                r = 255
                g = 255
                b = 0
                colorpb = icon.copy()
                for row in colorpb.get_pixels_array():
                    for pix in row:
                        pix[0] = r
                        pix[1] = g
                        pix[2] = b
	
                alpha = 255#int(int(70) * 2.55 + 0.2)
                tk = 2
                bg = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, self.w, self.h)
                bg.fill(0x00000000)
                glow = bg.copy()
                # Prepare the glow that should be put bind the icon
                tk1 = tk - int(tk / 2)
                for x, y in ((-tk1, -tk1), (-tk1, tk1), (tk1, -tk1), (tk1, tk1)):
                    colorpb.composite(glow, 0, 0, self.w, self.h, x, y, 1, 1, gtk.gdk.INTERP_BILINEAR, 170)
                for x, y in ((-tk, -tk), (-tk, tk), (tk, -tk), (tk, tk)):
                    colorpb.composite(glow, 0, 0, self.w, self.h, x, y, 1, 1, gtk.gdk.INTERP_BILINEAR, 70)
                glow.composite(bg, 0, 0, self.w, self.h, 0, 0, 1, 1, gtk.gdk.INTERP_BILINEAR, alpha)
                icon.composite(bg, 0, 0, self.w, self.h, 0, 0, 1, 1, gtk.gdk.INTERP_BILINEAR, 255)
                icon = bg
                       
            #加深
            elif Globals.Settings['Tab_Efect'] == 5:#saturate
                icon.saturate_and_pixelate(icon, 6.0, False)
					
            self.buttonImage.set_from_pixbuf(icon)

	if Globals.Settings['Tab_Efect'] == 1:
            self.Frame.move(self.buttonImage, Globals.TabBackIconX-2, Globals.TabBackIconY-2)
	else:
            self.Frame.move(self.buttonImage, Globals.TabBackIconX, Globals.TabBackIconY)

    def leave (self, widget, event):
        icon = self.getIcon(self.iconSize)
	if Globals.Settings['Tab_Efect'] != 0:		
            self.Frame.move(self.buttonImage, Globals.TabBackIconX, Globals.TabBackIconY)
            self.buttonImage.set_from_pixbuf(icon)
    
    def setIcon (self, iconName):
        self.iconName = iconName
        self.iconChanged()

    # IconTheme changed, setup new button icons
    def themeChanged(self, theme):
        self.iconChanged()

    def iconChanged(self):
        icon = self.getIcon(self.iconSize)
        self.buttonImage.clear()
        if icon:
            self.buttonImage.set_from_pixbuf(icon)
            self.buttonImage.set_size_request(-1, -1)
            del icon
        else:
            #[iW, iH ] = iconManager.getIconSize( self.iconSize )
            self.buttonImage.set_size_request(self.iconSize, self.iconSize)

    def setIconSize(self, size):
        self.iconSize = size
        icon = self.getIcon(self.iconSize)
        self.buttonImage.clear()
        if icon:
            self.buttonImage.set_from_pixbuf(icon)
            self.buttonImage.set_size_request(-1, -1)
            del icon
        elif self.iconSize:
            #[ iW, iH ] = iconManager.getIconSize( self.iconSize )
            self.buttonImage.set_size_request(self.iconSize, self.iconSize)
    
    def onDestroy(self, widget):
        self.buttonImage.clear()
        iconManager.disconnect(self.themeChangedHandlerId)
        for connection in self.connections:
            self.disconnect(connection)
        del self.connections                
            
    def setSelectedTab(self, tab):
	if tab == False:
            self.Image.set_from_pixbuf(None)
        else:
            self.pic = gtk.gdk.pixbuf_new_from_file(Globals.ImageDirectory + Globals.TabBackImage)
            self.Image.set_from_pixbuf(self.pic)
	    del self.pic
            
#AppButton.__init__( self, self.appIconName, iconSize )
class AppButton(gtk.EventBox):
    
    def __init__(self, iconName, iconSize):
        gtk.EventBox.__init__(self)
        
        self.connections = []
        self.Frame = gtk.Fixed()
        self.set_visible_window(0)
        self.add(self.Frame)
        
        #self.Label = gtk.Label()
        
        #Button背景
        self.Image = gtk.Image()
        sel = gtk.gdk.pixbuf_get_file_info(Globals.ImageDirectory + Globals.ButtonBackImage)
	self.w = sel[1]
	self.h = sel[2]
	sel = None
        self.Image.set_from_pixbuf(sel)
        self.set_size_request(self.w, self.h)
        self.Image.set_size_request(self.w, self.h)
        self.Frame.set_size_request(self.w, self.h)
        self.Frame.put(self.Image, 0, 0)
        
        #Button上的图标
        self.iconName = iconName
        self.iconSize = iconSize
        icon = self.getIcon(self.iconSize)
        self.buttonImage = gtk.Image()
        if icon:
            self.buttonImage.set_from_pixbuf(icon)
            del icon
        else:
            self.buttonImage.set_size_request(self.iconSize, self.iconSize)
        self.Frame.put(self.buttonImage, Globals.ButtonBackIconX, Globals.ButtonBackIconY)
            
        self.connectSelf("destroy", self.onDestroy)
        self.connectSelf("enter_notify_event", self.enter)
        self.connectSelf("leave_notify_event", self.leave)
        self.themeChangedHandlerId = iconManager.connect("changed", self.themeChanged)
    
    def connectSelf(self, event, callback):
        self.connections.append(self.connect(event, callback))
    
    def setSelectedTab(self, flag):
        if flag == True:
            self.pic = gtk.gdk.pixbuf_new_from_file(Globals.ImageDirectory + Globals.ButtonBackImage)
            self.Image.set_from_pixbuf(self.pic)  
	    del self.pic
        else:
            self.Image.set_from_pixbuf(None)
        
    def getIcon (self, iconSize):
        #if not self.iconName:
        #    return None

        icon = iconManager.getIcon(self.iconName, iconSize)
        if not icon:
            icon = iconManager.getIcon("application-default-icon", iconSize)

        return icon
    
    def enter (self, widget, event):
        icon = self.getIcon(self.iconSize)
        if Globals.Settings['Tab_Efect'] != 0:
            #增大
            if Globals.Settings['Tab_Efect'] == 1: #grow
                icon = self.getIcon(self.iconSize + 2)

            #黑白
            elif Globals.Settings['Tab_Efect'] == 2:#bw
                icon.saturate_and_pixelate(icon, 0.0, False)
            
            #模糊
            elif Globals.Settings['Tab_Efect'] == 3:#Blur
		alpha = 255#int(int(70) * 2.55 + 0.2)
		tk = 2
		bg = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, self.w, self.h)
		bg.fill(0x00000000)
		glow = bg.copy()
		# Prepare the glow that should be put bind the icon
		tk1 = tk - int(tk / 2)
		for x, y in ((-tk1, -tk1), (-tk1, tk1), (tk1, -tk1), (tk1, tk1)):
                    icon.composite(glow, 0, 0, self.w, self.h, x, y, 1, 1, gtk.gdk.INTERP_BILINEAR, 170)
		for x, y in ((-tk, -tk), (-tk, tk), (tk, -tk), (tk, tk)):
                    icon.composite(glow, 0, 0, self.w, self.h, x, y, 1, 1, gtk.gdk.INTERP_BILINEAR, 70)
		glow.composite(bg, 0, 0, self.w, self.h, 0, 0, 1, 1, gtk.gdk.INTERP_BILINEAR, alpha)
		icon = bg
                
            #醒目
            elif Globals.Settings['Tab_Efect'] == 4:#glow
                r = 255
                g = 255
                b = 0
                colorpb = icon.copy()
                for row in colorpb.get_pixels_array():
                    for pix in row:
                        pix[0] = r
                        pix[1] = g
                        pix[2] = b
	
                alpha = 255#int(int(70) * 2.55 + 0.2)
                tk = 2
                bg = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, self.w, self.h)
                bg.fill(0x00000000)
                glow = bg.copy()
                # Prepare the glow that should be put bind the icon
                tk1 = tk - int(tk / 2)
                for x, y in ((-tk1, -tk1), (-tk1, tk1), (tk1, -tk1), (tk1, tk1)):
                    colorpb.composite(glow, 0, 0, self.w, self.h, x, y, 1, 1, gtk.gdk.INTERP_BILINEAR, 170)
                for x, y in ((-tk, -tk), (-tk, tk), (tk, -tk), (tk, tk)):
                    colorpb.composite(glow, 0, 0, self.w, self.h, x, y, 1, 1, gtk.gdk.INTERP_BILINEAR, 70)
                glow.composite(bg, 0, 0, self.w, self.h, 0, 0, 1, 1, gtk.gdk.INTERP_BILINEAR, alpha)
                icon.composite(bg, 0, 0, self.w, self.h, 0, 0, 1, 1, gtk.gdk.INTERP_BILINEAR, 255)
                icon = bg
                       
            #加深
            elif Globals.Settings['Tab_Efect'] == 5:#saturate
                icon.saturate_and_pixelate(icon, 6.0, False)					

            self.buttonImage.set_from_pixbuf(icon)

	if Globals.Settings['Tab_Efect'] == 1:
            self.Frame.move(self.buttonImage, Globals.ButtonBackIconX-2, Globals.ButtonBackIconY-2)
	else:
            self.Frame.move(self.buttonImage, Globals.ButtonBackIconX, Globals.ButtonBackIconY)

    def leave (self, widget, event):
        icon = self.getIcon(self.iconSize)
	if Globals.Settings['Tab_Efect'] != 0:		
            self.Frame.move(self.buttonImage, Globals.ButtonBackIconX, Globals.ButtonBackIconY)
            self.buttonImage.set_from_pixbuf(icon)
    
    def setIcon (self, iconName):
        self.iconName = iconName
        self.iconChanged()

    # IconTheme changed, setup new button icons
    def themeChanged(self, theme):
        self.iconChanged()

    def iconChanged(self):
        icon = self.getIcon(self.iconSize)
        self.buttonImage.clear()
        if icon:
            self.buttonImage.set_from_pixbuf(icon)
            self.buttonImage.set_size_request(-1, -1)
            del icon
        else:
            #[iW, iH ] = iconManager.getIconSize( self.iconSize )
            self.buttonImage.set_size_request(self.iconSize, self.iconSize)

    def setIconSize(self, size):
        self.iconSize = size
        icon = self.getIcon(self.iconSize)
        self.buttonImage.clear()
        if icon:
            self.buttonImage.set_from_pixbuf(icon)
            self.buttonImage.set_size_request(-1, -1)
            del icon
        elif self.iconSize:
            #[ iW, iH ] = iconManager.getIconSize( self.iconSize )
            self.buttonImage.set_size_request(self.iconSize, self.iconSize)
            
    def addLabel(self, text, styles=None):
        self.Label = gtk.Label()
        if "<b>" in text:
            text = "<span foreground=\"#FFFF00\">%s</span>" % text
            text = "<b>%s</b>" % text
            self.Label.set_markup(text) # don't remove our pango
        else:
            text = "<span foreground=\"#FFFFFF\">%s</span>" % text
            self.Label.set_markup(text)

        self.Label.set_alignment(0.0, 0.0)
        self.Label.set_width_chars(21)
        self.Label.set_ellipsize(pango.ELLIPSIZE_END)
        self.Label.show()
        self.Frame.put(self.Label, Globals.ButtonBackNameX, Globals.ButtonBackNameY)

    def onDestroy(self, widget):
        self.buttonImage.clear()
        iconManager.disconnect(self.themeChangedHandlerId)
        for connection in self.connections:
            self.disconnect(connection)
        del self.connections
        
#ApplicationLauncher.__init__( self, desktopFile, iconSize )
class ApplicationLauncher(AppButton):

    def __init__(self, desktopFile, iconSize):
        
        if isinstance(desktopFile, xdg.Menu.MenuEntry):
            desktopItem = desktopFile.DesktopEntry
            desktopFile = desktopItem.filename
            self.appDirs = desktop.desktopFile.AppDirs
            
        elif isinstance(desktopFile, xdg.Menu.DesktopEntry):
            desktopItem = desktopFile
            desktopFile = desktopItem.filename
            self.appDirs = [os.path.dirname(desktopItem.filename)]
            
        else:
            desktopItem = xdg.DesktopEntry.DesktopEntry(desktopFile)
            self.appDirs = [os.path.dirname(desktopFile)]

        self.desktopFile = desktopFile
        self.loadDesktopEntry(desktopItem)

        self.drag = True

        AppButton.__init__(self, self.appIconName, iconSize)
        self.setupLabels()
        
        self.connectSelf("drag_data_get", self.dragDataGet)
        self.drag_source_set(gtk.gdk.BUTTON1_MASK, [("text/plain", 0, 100), ("text/uri-list", 0, 101)], gtk.gdk.ACTION_COPY)
        self.connectSelf("drag_begin", self.dragBegin)

    def loadDesktopEntry(self, desktopItem):
        try:
            self.appName = desktopItem.getName()
            self.appGenericName = desktopItem.getGenericName()
            self.appComment = desktopItem.getComment()
            self.appExec = desktopItem.getExec()
            self.appIconName = desktopItem.getIcon()
            self.appCategories = desktopItem.getCategories()
            self.appGnomeDocPath = desktopItem.get("X-GNOME-DocPath") or ""
            self.useTerminal = desktopItem.getTerminal()

            if not self.appGnomeDocPath:
                self.appKdeDocPath      = desktopItem.getDocPath() or ""

            self.appName            = self.appName.strip()
            self.appGenericName     = self.appGenericName.strip()
            self.appComment         = self.appComment.strip()

        except Exception, e:
            #print e
            self.appName            = ""
            self.appGenericName     = ""
            self.appComment         = ""
            self.appExec            = ""
            self.appIconName        = ""
            self.appCategories      = ""
            self.appDocPath         = ""

    def setupLabels(self):
        self.addLabel(self.appName)

    def filterText(self, text):
        keywords = text.lower().split()
        appName = self.appName.lower()
        appGenericName = self.appGenericName.lower()
        appComment = self.appComment.lower()
        appExec = self.appExec.lower()
        for keyword in keywords:
            keyw = keyword
            if keyw != "" and appName.find(keyw) == -1 and appGenericName.find(keyw) == -1 and appComment.find(keyw) == -1 and appExec.find(keyw) == -1:
                self.hide()
                return False

        self.show()
        return True
        
    def getTooltip(self, highlight=None):
               
        tooltip = self.appName
        if self.appComment != "" and self.appComment != self.appName:
            tooltip = self.appComment

        return tooltip

    def dragBegin(self, widget, drag_context):
        self.drag = False
        icon = self.getIcon(self.iconSize)
        if icon:
            self.drag_source_set_icon_pixbuf(icon)
            del icon

    def dragDataGet(self, widget, context, selection, targetType, eventTime):
        if targetType == 100: # text/plain
            selection.set_text("'" + self.desktopFile + "'", -1)
        elif targetType == 101: # text/uri-list
            if self.desktopFile[0:7] == "file://":
                selection.set_uris([self.desktopFile])
            else:
                selection.set_uris(["file://" + self.desktopFile])
                
    def execute(self):
        if self.appExec:
            if self.useTerminal:
                cmd = "x-terminal-emulator -e \"" + self.appExec + "\""
                Execute(self, cmd)
            else:
                Execute(self, self.appExec)

    # IconTheme changed, setup new icons for button and drag 'n drop
    def iconChanged(self):
        AppButton.iconChanged(self)

        icon = self.getIcon(gtk.ICON_SIZE_DND)
        if icon:
            self.drag_source_set_icon_pixbuf(icon)
            del icon

    def onDestroy(self, widget):
        AppButton.onDestroy(self, widget)

class MenuApplicationLauncher(ApplicationLauncher):

    def __init__(self, desktopFile, iconSize, category, showComment, highlight=False):
        
        self.showComment = showComment
        self.appCategory = category
        self.highlight = highlight
        
        ApplicationLauncher.__init__(self, desktopFile, iconSize)

    def filterCategory(self, category):
        if self.appCategory == category or category == "":
            self.show()
        else:
            self.hide()

    def setupLabels(self):        
        appName = self.appName
        appComment = self.appComment
        if self.highlight: 
            try:
                appName = "<b>%s</b>" % (appName)
                appComment = "<b>%s</b>" % (appComment)
                print appComment
            except Exception, detail:
                print detail
                pass
        self.addLabel(appName)
        
    def execute(self, * args):
        if self.highlight == True:
            self.highlight = False
            self.Label.destroy()
            self.setupLabels()
        return super(MenuApplicationLauncher, self).execute(*args)

class FavApplicationLauncher(ApplicationLauncher):

    def __init__(self, desktopFile, iconSize):
        self.category = _("Favorites")
        self.Name = desktopFile
        ApplicationLauncher.__init__(self, desktopFile, iconSize)

    def setupLabels(self):    
        self.addLabel(self.appName)
        
    def filterCategory(self, category):
        if category == self.category:
            self.show()
        else:
            self.hide()

    def filterText(self, text):
     	pass

class PlaApplicationLauncher(gtk.EventBox):

    def __init__(self, Name, RecentImage, ExceString, Png):
        gtk.EventBox.__init__(self)
        
        self.drag = True
        self.connections = []
        self.category = _("My Computer")
        self.cmd = ExceString
        self.path = Name
        self.png = Png
        
        self.Frame = gtk.Fixed()
        self.set_visible_window(0)
        self.add(self.Frame)

        self.Image = gtk.Image()
        sel = gtk.gdk.pixbuf_get_file_info(Globals.ImageDirectory + Globals.ButtonBackImage)
	self.w = sel[1]
	self.h = sel[2]
	sel = None
        self.Image.set_from_pixbuf(sel)
        self.set_size_request(self.w, self.h)
        self.Image.set_size_request(self.w, self.h)
        self.Frame.set_size_request(self.w, self.h)
        self.Frame.put(self.Image, 0, 0)

        self.buttonImage = gtk.Image()
        self.buttonImage.set_from_pixbuf(RecentImage)
        self.Frame.put(self.buttonImage, Globals.ButtonBackIconX, Globals.ButtonBackIconY)

        self.addLabel(os.path.basename(Name))
        
        self.connectSelf("enter_notify_event", self.enter)
        self.connectSelf("leave_notify_event", self.leave)
        
    def execute(self):
        command = self.cmd
        if command == "nautilus-connect-server":
            os.system('%s &' % command)
        else:
            if command == '':
                command = "computer:///"
            os.system("xdg-open '%s' &" % command)
        
    def connectSelf(self, event, callback):
        self.connections.append(self.connect(event, callback))
    
    def setSelectedTab(self, flag):
        if flag == True:
            self.pic = gtk.gdk.pixbuf_new_from_file(Globals.ImageDirectory + Globals.ButtonBackImage)
            self.Image.set_from_pixbuf(self.pic)  
	    del self.pic
        else:
            self.Image.set_from_pixbuf(None)
        
    def addLabel(self, text):
        self.Label = gtk.Label()
        
        text = "<span foreground=\"#FFFFFF\">%s</span>" % text
        self.Label.set_markup(text)

        self.Label.set_alignment(0.0, 0.0)
        self.Label.set_width_chars(21)
        self.Label.set_ellipsize(pango.ELLIPSIZE_END)
        self.Frame.put(self.Label, Globals.ButtonBackNameX, Globals.ButtonBackNameY)
    
    def enter (self, widget, event):
        self.setSelectedTab(True)

    def leave (self, widget, event):
        self.setSelectedTab(False)  
        
    def filterCategory(self, category):
        if category == self.category:
            self.show_all()
        else:
            self.hide()
            
    def filterText(self, text):
        keywords = text.lower().split()
        appName = (os.path.basename(self.path).lower())
        appGenericName = (self.path.lower())
        appComment = (self.path.lower())
        appExec = (self.cmd.lower())
        for keyword in keywords:
            keyw = (keyword)
            if keyw != "" and appName.find(keyw) == -1 and appGenericName.find(keyw) == -1 and appComment.find(keyw) == -1 and appExec.find(keyw) == -1:
                self.hide()
                return False

        self.show()
        return True

class RecApplicationLauncher(gtk.EventBox):

    def __init__(self, Name, RecentImage, ExceString):
        gtk.EventBox.__init__(self)
        
        self.drag = True
        self.connections = []
        self.category = _("Recent")
        self.cmd = ExceString
        self.path = Name
        
        command = urllib.unquote(str(self.cmd))
        if os.path.isfile(self.path) or os.path.isdir(command.replace('file://', '')):
            self.flag = True
        else:self.flag = False
        
        self.Frame = gtk.Fixed()
        self.set_visible_window(0)
        self.add(self.Frame)

        self.Image = gtk.Image()
        sel = gtk.gdk.pixbuf_get_file_info(Globals.ImageDirectory + Globals.ButtonBackImage)
	self.w = sel[1]
	self.h = sel[2]
	sel = None
        self.Image.set_from_pixbuf(sel)
        self.set_size_request(self.w, self.h)
        self.Image.set_size_request(self.w, self.h)
        self.Frame.set_size_request(self.w, self.h)
        self.Frame.put(self.Image, 0, 0)
        
        self.buttonImage = gtk.Image()
        self.buttonImage.set_from_pixbuf(RecentImage)
        self.Frame.put(self.buttonImage, Globals.ButtonBackIconX, Globals.ButtonBackIconY)
        
        self.addLabel(os.path.basename(Name))
        
        self.connectSelf("enter_notify_event", self.enter)
        self.connectSelf("leave_notify_event", self.leave)
        
    def execute(self):
        if self.flag:
            os.system("xdg-open '%s' &" % self.cmd)

    def connectSelf(self, event, callback):
        self.connections.append(self.connect(event, callback))
    
    def setSelectedTab(self, flag):
        if flag == True:
            self.pic = gtk.gdk.pixbuf_new_from_file(Globals.ImageDirectory + Globals.ButtonBackImage)
            self.Image.set_from_pixbuf(self.pic)  
	    del self.pic
        else:
            self.Image.set_from_pixbuf(None)
        
    def addLabel(self, text):
        self.Label = gtk.Label()        
        if self.flag:
            text = "<span foreground=\"#FFFFFF\">%s</span>" % text
        else:text = "<span foreground=\"#A52A2A\">%s</span>" % text
        self.Label.set_markup(text)

        self.Label.set_alignment(0.0, 0.0)
        self.Label.set_width_chars(21)
        self.Label.set_ellipsize(pango.ELLIPSIZE_END)
        self.Frame.put(self.Label, Globals.ButtonBackNameX, Globals.ButtonBackNameY)
    
    def enter (self, widget, event):
        self.setSelectedTab(True)

    def leave (self, widget, event):
        self.setSelectedTab(False)  
        
    def filterCategory(self, category):
        if category == self.category:
            self.show_all()
        else:
            self.hide()
            
    def filterText(self, text):
        keywords = text.lower().split()
        appName = (os.path.basename(self.path).lower())
        appGenericName = (self.path.lower())
        appComment = (self.path.lower())
        appExec = (self.cmd.lower())
        for keyword in keywords:
            keyw = (keyword)
            if keyw != "" and appName.find(keyw) == -1 and appGenericName.find(keyw) == -1 and appComment.find(keyw) == -1 and appExec.find(keyw) == -1:
                self.hide()
                return False

        self.show()
        return True
    
iconManager = IconManager()

class ProgramClass(gobject.GObject):
    __gsignals__ = {
        'activate': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'menu': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'clicked': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'right-clicked': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
        }
    
    def __init__(self, Frame, usericon, usericonstate, LastUserPicName):
        gobject.GObject.__init__ (self)
       
        self.MenuWin = Frame
        self.usericon = usericon
        self.usericonstate = usericonstate
        self.LastUserPicName = LastUserPicName

        # app category list
        self.Category_Scr = gtk.ScrolledWindow()
        self.Category_VBox = gtk.VBox(False)
        
        self.Category_Scr.set_size_request(Globals.PG_tabframedimensions[0], Globals.PG_tabframedimensions[1])
	self.Category_Scr.set_shadow_type(gtk.SHADOW_NONE)
	self.Category_Scr.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        
        self.Category_Scr.add_with_viewport(self.Category_VBox)
        self.Category_Scr.get_children()[0].set_shadow_type(gtk.SHADOW_NONE)
        if Globals.Settings['GtkColors'] == 0:
            self.Category_Scr.get_children()[0].modify_bg(gtk.STATE_NORMAL, Globals.ThemeColorCode)
        self.MenuWin.put(self.Category_Scr, Globals.PG_tabframe[0], Globals.PG_tabframe[1])

        # middle vline
        self.seperator = gtk.Image()
        self.seperatorImage = gtk.gdk.pixbuf_new_from_file(Globals.ImageDirectory + Globals.VLineImage)  
        self.seperator.set_from_pixbuf(self.seperatorImage)
        self.MenuWin.put(self.seperator, Globals.VLineX, Globals.VLineY)

        # app list
        self.App_Scr = gtk.ScrolledWindow()
        self.App_VBox = gtk.VBox(False)
        
        self.App_Scr.set_size_request(Globals.PG_buttonframedimensions[0], Globals.PG_buttonframedimensions[1])
	self.App_Scr.set_shadow_type(gtk.SHADOW_NONE)
	self.App_Scr.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        
        self.App_Scr.add_with_viewport(self.App_VBox)
        self.App_Scr.get_children()[0].set_shadow_type(gtk.SHADOW_NONE)
        if Globals.Settings['GtkColors'] == 0:
            self.App_Scr.get_children()[0].modify_bg(gtk.STATE_NORMAL, Globals.ThemeColorCode)
        self.MenuWin.put(self.App_Scr, Globals.PG_buttonframe[0], Globals.PG_buttonframe[1])
                
        self.filterTimer = None
        self.menuChangedTimer = None

        self.buildingButtonList = False
        self.stopBuildingButtonList = False

        self.categoryList = []
        self.applicationList = []
        self.suggestions = []
        self.favorites = []
        self.FileList = []
        self.RecentList = []
        self.PlacesList = []
        
        self.rebuildLock = False
        self.activeFilter = (1, "")
	self.cate_button = None
        self.adminMenu = None
        
        self.IconFactory = IconFactory.IconFactory()

        self.user_app = gio.File("/usr/share/applications").monitor_directory()
        self.user_app.connect_after("changed", self.menuChanged)

        self.wine_app = gio.File("%s/.local/share/applications" % Globals.HomeDirectory).monitor_directory(gio.FILE_MONITOR_NONE, None)
        self.wine_app.connect("changed", self.menuChanged)
        
        self.wine = gio.File("/etc/xdg/menus/applications-merged").monitor_directory(gio.FILE_MONITOR_NONE, None)
        self.wine.connect("changed", self.menuChanged, 100)
        
        self.recent_manager = gtk.recent_manager_get_default()
	self.recent_manager.connect("changed", self.buildRecent)

        self.monitor = gio.volume_monitor_get()
        self.monitor.connect("mount-removed", self.buildPlaces)
        self.monitor.connect("mount-added", self.buildPlaces)

    def destroy(self):
        self.App_VBox.destroy()
        self.Category_VBox.destroy()
    
    def Restart(self, data=None):
        pass

    def SetInputFocus(self):
	pass

    def buildPlaces (self, * args, ** kargs):
        self.NameList, self.IconsList, self.PathList, self.PngList = self.getDrive()
        loc = 0
        if self.PlacesList != None:
            for item in self.PlacesList:
                item.destroy() 
        self.PlacesList = []
	for Name in self.NameList:
            if Name != None:
                plaButton = PlaApplicationLauncher(Name, self.IconsList[loc], self.PathList[loc], self.PngList[loc])
                plaButton.connect("button-release-event", self.activateButton)
                if Globals.Settings['Show_Tips']:
                    plaButton.Frame.set_tooltip_text(Name)
                self.App_VBox.pack_start(plaButton, False)
                self.PlacesList.append(plaButton)
            loc = loc + 1
    
    def getDrive(self):
        NameList = []
        IconsList = []
        PathList = []
        PngList = []
        
        NameList.append(_("File System"))
        IconsList.append(self.IconFactory.geticonfile("drive-harddisk"))
        PathList.append("/")
        PngList.append("drive-harddisk")
        
        self.drives = self.monitor.get_connected_drives()
	for drive in self.drives:
            if drive.has_media():
		self.mounts = drive.get_volumes()
		for mount in self.mounts:
                    ico = mount.get_icon()
                    a = self.IconFactory.getgicon(ico)
                    NameList.append(mount.get_name())
                    IconsList.append(self.IconFactory.geticonfile(a))
                    try:
			PathList.append(str(mount.get_mount().get_root().get_uri()))
                    except:
                        PathList.append("")
                    PngList.append(a)

        NameList.append(_('Network'))
        IconsList.append(self.IconFactory.geticonfile("gtk-network"))
        PathList.append('network:///')
        PngList.append("network")

        NameList.append(_('Connect to Server'))
        IconsList.append(self.IconFactory.geticonfile("applications-internet"))
        PathList.append('nautilus-connect-server')
        PngList.append("applications-internet")

        NameList.append(_('Home Folder'))
        IconsList.append(self.IconFactory.geticonfile("user-home"))
        PathList.append(Globals.HomeDirectory)
        PngList.append("user-home")

        if os.path.isfile("%s/.gtk-bookmarks" % Globals.HomeDirectory):
            f = open("%s/.gtk-bookmarks" % Globals.HomeDirectory, "r")
            data = f.readlines(600)
            f.close()
            f = None
            for i in data:		
		self.bm = str(i).replace("\n", "")
		if self.bm.find(' ') != -1:
                    self.folder = urllib.url2pathname(self.bm[:self.bm.find(' ')])
                    self.name = urllib.url2pathname(self.bm[self.bm.find(' ') + 1:])
		else: 
                    self.folder = self.bm
                    self.name = urllib.url2pathname(str(self.bm).split("/").pop()) 
		try:
                    Gfile = gio.File(self.folder)
                    tuble = [Gfile, Gfile.query_info("standard::*"), []]
                    ico = tuble[1].get_icon()
                    NameList.append(self.name)
                    IconsList.append(self.IconFactory.geticonfile(self.IconFactory.getgicon(ico)))
                    PathList.append(self.folder)
                    PngList.append(self.IconFactory.getgicon(ico))
                except:pass

        NameList.append(_('Trash'))
        IconsList.append(self.IconFactory.geticonfile("user-trash"))
        PathList.append('trash:///')
        PngList.append("user-trash")

        return NameList, IconsList, PathList, PngList     
    
    def buildRecent(self, * args, ** kargs):
        self.FileList, self.IconList, self.ExceList = self.getRecent()
	loc = 0
	if self.RecentList != None:
            for item in self.RecentList:
                item.destroy()
     	self.RecentList = []
	for Name in self.FileList:
            if Name != None:
                recButton = RecApplicationLauncher(Name, self.IconList[loc], self.ExceList[loc])
                recButton.connect("button-release-event", self.activateButton, recButton.flag)
                if Globals.Settings['Show_Tips']:
		    if not recButton.flag:
                        txt = _(':The path is invalid')
                        recButton.Frame.set_tooltip_text(Name + txt)
                    else:recButton.Frame.set_tooltip_text(Name)	
                self.App_VBox.pack_start(recButton, False)
                self.RecentList.append(recButton)
            loc = loc + 1
        return True 
    
    def getRecent(self):
	FileString = []
	IconString = []
        ExceString = []
	RecentInfo = self.recent_manager.get_items()
	# print RecentInfo[0].get_icon(gtk.ICON_SIZE_MENU)
	count = 0
	MaxEntries = Globals.RI_numberofitems
	for items in RecentInfo:
            FileString.append(items.get_uri_display())
            IconString.append(items.get_icon(Globals.PG_iconsize))
            ExceString.append(items.get_uri())
            count += 1
            if count >= MaxEntries:
		break
	return FileString, IconString, ExceString
    
    def do_recent_applications_file(self):
    
        pass
    def buildFavorites(self):
        try:
            filedir = Globals.Favorites
            addedFavorites = []
            newFavorites = []
            removeFavorites = []
            
            for filename in os.listdir(filedir):
                newFavorites.append(filedir + filename)
            
            if not self.favorites:
                addedFavorites = newFavorites
            else:
                for filename in newFavorites:
                    found = False
                    for filename2 in self.favorites:
                        if filename == filename2.Name:
                            found = True
                            break
                    if not found:
                        addedFavorites.append(filename)
                        
                key = 0        
                for filename in self.favorites:
                    found = False
                    for filename2 in newFavorites:
                        if filename.Name == filename2:
                            found = True
                            break
                    if not found:
                        print filename.Name
                        removeFavorites.append(key)
                    else:
                        key += 1
            for key in removeFavorites:
            	self.favorites[key].destroy()
                del self.favorites[key]
            
            for filename in addedFavorites:
                favButton = FavApplicationLauncher(filename, Globals.PG_iconsize)
                if favButton.appExec:
                    favButton.connect("enter-notify-event", self.Button_enter, True)
                    favButton.connect("leave-notify-event", self.Button_leave, False)
                    favButton.connect("button-release-event", self.activateButton)
                    favButton.show_all()
                    if Globals.Settings['Show_Tips']:
                        favButton.Frame.set_tooltip_text(favButton.getTooltip())
                    self.favorites.append(favButton)    
                    self.App_VBox.pack_start(favButton, False)
        except Exception, e:
            print u"File in favorites not found: '", e
    
    def buildButtonList(self, hide_method):
        self.hide_method = hide_method
        if self.buildingButtonList:
            self.stopBuildingButtonList = True
            gobject.timeout_add(100, self.buildButtonList)
            return

        self.stopBuildingButtonList = False

        self.updateBoxes(False)
    
    def menuChanged(self, monitor=None, Gfile=None, data=None, event=None, timer=2000):
        file = Gfile.get_path()
        if file.endswith("desktop"):
            i = 0
            while event == gio.FILE_MONITOR_EVENT_CREATED and i <= 180:
                if os.path.isfile(file):
                    break
                time.sleep(1)
                print i
                i += 1

            if self.menuChangedTimer:
                gobject.source_remove(self.menuChangedTimer)

            self.menuChangedTimer = gobject.timeout_add(timer, self.updateBoxes, True)    
        
    def updateBoxes(self, menu_has_changed):        
        # FIXME: This is really bad!
        if self.rebuildLock:            
            return

        self.rebuildLock = True

        self.menuChangedTimer = None
        
        self.loadMenuFiles()

        # Find added and removed categories than update the category list
        newCategoryList = self.buildCategoryList()
        addedCategories = []
        removedCategories = []
        
        if not self.categoryList:
            addedCategories = newCategoryList
            
        else:
            for item in newCategoryList:
                found = False
                for item2 in self.categoryList:
                    if item["name"] == item2["name"] and item["icon"] == item2["icon"] and item["tooltip"] == item2["tooltip"] and item["index"] == item2["index"]:
                        found = True
                        break
                if not found:
                    addedCategories.append(item)
            
            key = 0
            for item in self.categoryList:
                found = False
                for item2 in newCategoryList:
                    if item["name"] == item2["name"] and item["icon"] == item2["icon"] and item["tooltip"] == item2["tooltip"] and item["index"] == item2["index"]:
                        found = True
                        break
                if not found:
                    print key
                    removedCategories.append(key)
                else:
                    key += 1

        for key in removedCategories:
            print self.activeFilter[1], self.categoryList[key]["name"]
            if self.activeFilter[1] == self.categoryList[key]["name"]:
                self.Select_install("")
                self.categoryList[0]["button"].setSelectedTab(True)
                
            self.categoryList[key]["button"].destroy()
            del self.categoryList[key]
          
        if addedCategories:
            sortedCategoryList = []
            for item in self.categoryList[0:-3]:
                self.Category_VBox.remove(item["button"])
                sortedCategoryList.append((item["name"], item["button"]))
            
            for item in addedCategories:
                item["button"] = CategoryTab(item["icon"], Globals.PG_iconsize, item["name"])
                
                if Globals.Settings['Show_Tips']:
                    item["button"].Frame.set_tooltip_text(item["tooltip"])
                    
                if Globals.Settings['TabHover']:
                    item["button"].connect("enter-notify-event", self.StartFilter, item["filter"], item["icon"])
                    item["button"].connect("leave-notify-event", self.StopFilter)
                else:
                    item["button"].connect("button-release-event", self.Filter, item["filter"], item["icon"])
                
                item["button"].show_all()
                
                if item["filter"] == "" and not menu_has_changed:
                    self.all_app = item["button"]
                    item["button"].setSelectedTab(True)
		elif menu_has_changed:
                    for id in self.categoryList:
                        id["button"].setSelectedTab(False)
                    item["button"].setSelectedTab(True)
                    
                self.categoryList.append(item)
                sortedCategoryList.append((item["name"], item["button"]))

            if has_gst:
		self.StartEngine()
   
            if menu_has_changed == True:
                for item in sortedCategoryList:
                    self.Category_VBox.pack_start(item[1], False)
            
            else:
                for item in sortedCategoryList[0:-3]:
                    self.Category_VBox.pack_start(item[1], False)
                for item in sortedCategoryList[-3:]:
                    self.Category_VBox.pack_end(item[1], False)
            
            
        # Find added and removed applications add update the application list
        newApplicationList = self.buildApplicationList()
        addedApplications = []
        removedApplications = []
        
        if not self.applicationList:
            addedApplications = newApplicationList
            
        else:
            for item in newApplicationList:
                found = False
                for item2 in self.applicationList:
                    
                    if item["entry"].DesktopEntry.getFileName() == item2["entry"].DesktopEntry.getFileName() and item["category"] == item2["category"]:
                        found = True
                        break
                if not found:
                    print "item[entry]==", item["entry"].DesktopEntry.getFileName()
                    addedApplications.append(item)

            key = 0
            for item in self.applicationList:
                found = False
                for item2 in newApplicationList:
                    if item["entry"].DesktopEntry.getFileName() == item2["entry"].DesktopEntry.getFileName() and item["category"] == item2["category"]:
                        found = True
                        break
                if not found:
                    print key
                    removedApplications.append(key)
                else:
                    # don't increment the key if this item is going to be removed
                    # because when it is removed the index of all later items is
                    # going to be decreased
                    key += 1
        
        for key in removedApplications:
            self.applicationList[key]["button"].destroy()
            del self.applicationList[key] 
          
        if addedApplications:
            sortedApplicationList = []
            for item in self.applicationList:
                self.App_VBox.remove(item["button"])
                sortedApplicationList.append((item["button"].appName, item["button"]))
                
            for item in addedApplications:
                item["button"] = MenuApplicationLauncher(item["entry"].DesktopEntry.getFileName(), Globals.PG_iconsize, item["category"], True, highlight=(True and menu_has_changed))
                
                if item["button"].appExec:
                    if Globals.Settings['Show_Tips']:
                        item["button"].Frame.set_tooltip_text(item["button"].getTooltip())

                    item["button"].connect("enter-notify-event", self.Button_enter, True)
                    item["button"].connect("leave-notify-event", self.Button_leave, False)
                    
                    if menu_has_changed:
                        item["button"].setSelectedTab(True)
                        self.categoryid = item["category"]

                    item["button"].connect("button-release-event", self.activateButton)
                    item["button"].show_all()    
                    sortedApplicationList.append((item["button"].appName.upper(), item["button"]))
                    self.applicationList.append(item)
                else:
                    item["button"].destroy()
                     
            sortedApplicationList.sort() 
            for item in sortedApplicationList:     
                self.App_VBox.pack_start(item[1], False)
            if menu_has_changed:
                for id in self.categoryList:
                    if id["filter"] == self.categoryid: 
                        id["button"].setSelectedTab(True)
                    else:id["button"].setSelectedTab(False)  
                self.Select_install(self.categoryid)
                     
        self.rebuildLock = False
        gc.collect()
    
    def activateButton(self, widget, event, date=True):
        if event.type == gtk.gdk.KEY_PRESS:event_button = 1
	elif event.type == gtk.gdk.BUTTON_PRESS:event_button = event.button
	elif event.type == gtk.gdk.BUTTON_RELEASE:event_button = event.button

        if event_button == 1 and widget.drag and date == True:
            self.hide_method()
            widget.execute()
        widget.drag = True
 
        if event_button == 3:
            mouse = widget.get_pointer()
            x = 0
            y = 0
 
            w = x + widget.get_allocation().width
            h = y + widget.get_allocation().height

            if mouse[0] > x and mouse[0] < w and mouse[1] > y and mouse[1] < h:
                self.emit('right-clicked')
                self.emit('menu')
                self.menuPopup(widget, event)
            
    def menuPopup(self, widget, event):
        mTree = gtk.Menu() 
           
        if isinstance(widget, RecApplicationLauncher):
            f = widget.path
            if os.path.isfile(f):
                openwith = add_image_menuitem(mTree, gtk.STOCK_OPEN, _("Open with"))
                Gfile = gio.File(f)
                tuble = [Gfile, Gfile.query_info("standard::*"), []]
                                                
                apps = gio.app_info_get_all_for_type(tuble[1].get_content_type())
                if apps != []:
                    submenu = gtk.Menu()
                    openwith.set_submenu(submenu)
                    add_menuitem(mTree, "-")
                for app in apps:
                    add_menuitem(submenu, app.get_name(), self.custom_launch, "'" + f + "'", app.get_executable())
            add_image_menuitem(mTree, gtk.STOCK_CLEAR, _("Clear recent documents"), self.del_to_rec, widget)
            
        elif isinstance(widget, PlaApplicationLauncher):
            f = widget.cmd.replace('file://', '')
            f = urllib.unquote(str(f))
            name = widget.path
            def searchfolder(folder, me):
                dirs = os.listdir(folder)
		dirs.sort(key=str.upper)
                                                
		for item in dirs:
                    if not item.startswith('.'):
                        if os.path.isdir(os.path.abspath(folder) + '/' + item):
                            add_image_menuitem(me, gtk.STOCK_DIRECTORY, item, self.launch_item, os.path.abspath(folder.replace('file://', '')) + '/' + item)
			else:   
                            submenu_item = gtk.MenuItem(item, use_underline=False)
                            me.append(submenu_item)
                            submenu_item.connect("button-press-event", self.launch_item, os.path.abspath(folder) + '/' + item)
                            submenu_item.show()
            
            if os.path.isdir(f):
                submenu = gtk.Menu()
                thismenu = add_image_menuitem(mTree, gtk.STOCK_REDO, name, None, None)
		if os.listdir(f) != []:
                    thismenu.set_submenu(submenu)
                    searchfolder(f, submenu)
                add_menuitem(mTree, "-")
            add_image_menuitem(mTree, gtk.STOCK_HOME, _("Create Desktop Shortcut"), self.add_to_desktop, widget)
                    
        else:    
            if (os.path.basename(widget.desktopFile)) in os.listdir(Globals.PanelLauncher):
                add_image_menuitem(mTree, gtk.STOCK_REMOVE, _("Remove from Panel"), self.del_to_panel, widget)
            else:
                add_image_menuitem(mTree, gtk.STOCK_ADD, _("Add to Panel"), self.add_to_panel, widget)
            
            add_image_menuitem(mTree, gtk.STOCK_HOME, _("Create Desktop Shortcut"), self.add_to_desktop, widget)
            add_menuitem(mTree, "-")    
        
            if (os.path.basename(widget.desktopFile)) in os.listdir(Globals.Favorites):
                add_image_menuitem(mTree, gtk.STOCK_REMOVE, _("Remove from Favorites"), self.del_to_fav, widget)
            else:
                add_image_menuitem(mTree, gtk.STOCK_ADD, _("Add to Favorites"), self.add_to_fav, widget)
            
            if not os.path.isdir(Globals.AutoStartDirectory):
                os.system('mkdir %s' % Globals.AutoStartDirectory)
            if (os.path.basename(widget.desktopFile)) in os.listdir(Globals.AutoStartDirectory):
                add_image_menuitem(mTree, gtk.STOCK_REMOVE, _("Remove from System Startup"), self.remove_autostarter, widget)
            else:
		add_image_menuitem(mTree, gtk.STOCK_ADD, _("Add to System Startup"), self.create_autostarter, widget)
            add_menuitem(mTree, "-")

            add_image_menuitem(mTree, gtk.STOCK_DIALOG_AUTHENTICATION, _("Open as Administrator"), self.runasadmin, widget)
        mTree.popup(None, None, None, event.button, event.time)

    def create_autostarter (self, widget, event, desktopEntry):
	if not os.path.isdir(Globals.AutoStartDirectory):
            os.system('mkdir %s' % Globals.AutoStartDirectory)
        os.system("cp \"%s\" \"%s\"" % (desktopEntry.desktopFile, Globals.AutoStartDirectory))

    def remove_autostarter (self, widget, event, desktopEntry):
	os.system('rm "%s%s"' % (Globals.AutoStartDirectory, os.path.basename(desktopEntry.desktopFile)))

    def runasadmin(self, widget, event, desktopEntry):
	os.system('%s "%s" &' % (Globals.Settings['AdminRun'], desktopEntry.appExec))

    def del_to_rec(self, widget, event, desktopEntry):
        self.recent_manager.purge_items()

    def custom_launch(self, widget, event, uri, app):
        os.system('%s %s &' % (app, uri))
        self.hide_method()
        
    def launch_item(self, button, event, uri):
        os.system('xdg-open %s &' % uri)
        self.hide_method()		
	
    def del_to_fav(self, widget, event, desktopEntry):
        os.system("rm %s%s" % (Globals.Favorites, os.path.basename(desktopEntry.desktopFile)))

    def add_to_fav(self, widget, event, desktopEntry):
        os.system("cp \"%s\" \"%s\"" % (desktopEntry.desktopFile, Globals.Favorites))  

    def add_to_desktop(self, widget, event, desktopEntry):
        if isinstance(desktopEntry, PlaApplicationLauncher):
            path = desktopEntry.path
            icon = desktopEntry.png
            cmd = desktopEntry.cmd
            import utils
            tmpdesktopDir = utils.xdg_dir("XDG_DESKTOP_DIR")
            print tmpdesktopDir
            starter = '%s/%s.desktop' % (tmpdesktopDir, path)
            code = ['#!/usr/bin/env xdg-open', '[Desktop Entry]']
            code.append('Name=%s' % path)
            code.append('StartupNotify=true')
            code.append('Terminal=false')
            code.append('Version=1.0')
            code.append('Icon=%s' % icon)
            code.append('Type=Application')
		
            code.append('Exec= xdg-open %s' % cmd)
            code.append('X-GNOME-Autostart-enabled=true')
		
            f = open(starter, 'w')
            if f:
                for l in code:
                    f.write(l + '\n')
		f.close()
                
            os.system("chmod a+rx \'%s\'" % starter)
        
        else:    
            # Determine where the Desktop folder is (could be localized)
            from configobj import ConfigObj
            config = ConfigObj(home + "/.config/user-dirs.dirs")
            desktopDir = home + "/Desktop"
            tmpdesktopDir = config['XDG_DESKTOP_DIR']
            tmpdesktopDir = commands.getoutput("echo " + tmpdesktopDir)
            if os.path.exists(tmpdesktopDir):
                desktopDir = tmpdesktopDir
            # Copy the desktop file to the desktop
            os.system("cp \"%s\" \"%s/\"" % (desktopEntry.desktopFile, desktopDir))
            os.system("chmod a+rx %s/*.desktop" % (desktopDir))
            
    
    def add_to_panel (self, widget, event, desktopEntry):
        """Add Panel"""
        import random
        object_name = "object_" + ''.join([random.choice('0123456789') for x in xrange(2)])
        object_dir = "/apps/panel/objects/"
                
        object_client = gconf.client_get_default()
        appletidlist = object_client.get_list("/apps/panel/general/applet_id_list", "string")
        for applet in appletidlist:
            bonobo_id = object_client.get_string("/apps/panel/applets/" + applet + "/bonobo_iid")
            if bonobo_id == "OAFIID:GNOME_YMenu":
                self.panel = object_client.get_string("/apps/panel/applets/" + applet + "/toplevel_id")
                self.panel_position = object_client.get_int("/apps/panel/applets/" + applet + "/position") + 4
        if not os.path.isdir(Globals.PanelLauncher):
            os.system('mkdir %s' % Globals.PanelLauncher)
    
        os.system("cp \"%s\" \"%s/\"" % (desktopEntry.desktopFile, Globals.PanelLauncher))
        panel_file = Globals.PanelLauncher + "/" + os.path.basename(desktopEntry.desktopFile)
        os.system("chmod a+rx %s" % (panel_file))        
            
        object_client.set_string(object_dir + object_name + "/" + "menu_path", "applications:/")
        object_client.set_bool(object_dir + object_name + "/" + "locked", False)
        object_client.set_int(object_dir + object_name + "/" + "position", self.panel_position)
        object_client.set_string(object_dir + object_name + "/" + "object_type", "launcher-object")
        object_client.set_bool(object_dir + object_name + "/" + "panel_right_stick", False)
        object_client.set_bool(object_dir + object_name + "/" + "use_menu_path", False)
        object_client.set_string(object_dir + object_name + "/" + "launcher_location", panel_file)
        object_client.set_string(object_dir + object_name + "/" + "custom_icon", "")
        object_client.set_string(object_dir + object_name + "/" + "tooltip", "")
        object_client.set_string(object_dir + object_name + "/" + "action_type", "lock")
        object_client.set_bool(object_dir + object_name + "/" + "use_custom_icon", False)
        object_client.set_string(object_dir + object_name + "/" + "attached_toplevel_id", "")
        object_client.set_string(object_dir + object_name + "/" + "bonobo_iid", "")
        object_client.set_string(object_dir + object_name + "/" + "toplevel_id", self.panel)

        launchers_list = object_client.get_list("/apps/panel/general/object_id_list", "string")
        launchers_list.append(object_name)
        object_client.set_list("/apps/panel/general/object_id_list", gconf.VALUE_STRING, launchers_list)
        
    
    def del_to_panel(self, widget, event, desktopEntry):
        object_client = gconf.client_get_default()
        launchers_list = object_client.get_list("/apps/panel/general/object_id_list", "string")
        for object in launchers_list:
            object_id = object_client.get_string("/apps/panel/objects/" + object + "/launcher_location")
            if object_id == "%s/%s" % (Globals.PanelLauncher, os.path.basename(desktopEntry.desktopFile)):
                launchers_list.remove(object)
                object_client.set_list("/apps/panel/general/object_id_list", gconf.VALUE_STRING, launchers_list)

    def Button_enter(self, widget, event, flag):
        widget.setSelectedTab(flag)
        
    def Button_leave(self, widget, event, flag):
        widget.setSelectedTab(flag)
      
    def CallSpecialMenu(self, command, data=None):
    	if self.cate_button != None:
            self.cate_button.setSelectedTab(False)
        self.all_app.setSelectedTab(True)
    	
        if command == 6:
            fulltext = "gnome-search-tool --named=%s &" % Globals.searchitem
            os.system(fulltext)
        else:
            for i in self.App_VBox.get_children():
                i.filterText(data)
      
    def StartFilter(self, widget, event, category, icon):
        if self.filterTimer:
            gobject.source_remove(self.filterTimer)
        self.filterTimer = gobject.timeout_add(115, self.Filter, widget, event, category, icon)

    def StopFilter(self, widget, event):
        if self.filterTimer:
            gobject.source_remove(self.filterTimer)
            self.filterTimer = None

    def Filter(self, widget, event, category, icon):
        
        self.UpdateUserImage(widget, event, icon)
        
        for item in self.categoryList:
            item["button"].setSelectedTab(False)
        widget.setSelectedTab(True)
        
        self.activeFilter = (1, category)
        self.cate_button = widget
        for i in self.App_VBox.get_children():
            i.filterCategory(category)
        self.PlaySound(3)

    def UpdateUserImage(self, widget, event, icon):
	ico = IconFactory.GetSystemIcon(icon)
	if ico == None:
	    ico = icon
	self.UserPicName = ico
        
	if self.LastUserPicName != self.UserPicName:
            self.LastUserPicName = self.UserPicName
            if self.usericonstate == 0:
                self.usericon.updateimage(2, self.UserPicName)
		self.usericon.transition([-1, -1, 1, -1], Globals.TransitionS, Globals.TransitionQ, None)
            elif self.usericonstate == 1:
		self.usericon.updateimage(3, self.UserPicName)
		self.usericon.transition([-1, -1, -1, 1], Globals.TransitionS, Globals.TransitionQ, None)
            elif self.usericonstate == 2:
		self.usericon.updateimage(2, self.UserPicName)
		self.usericon.transition([-1, -1, 1, -1], Globals.TransitionS, Globals.TransitionQ, None)
            if self.usericonstate == 1:
		self.usericonstate = 2
            else:
		self.usericonstate = 1  
        
    def Select_install(self, category=""):
        for i in self.App_VBox.get_children():
            i.filterCategory(category)
        
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
  
	elif t == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL) 
     
    def PlaySound(self, sound):
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
                self.player.set_state(gst.STATE_NULL)
                self.player.set_property('uri', uri)
                self.player.set_state(gst.STATE_PLAYING)
            else:
                os.system('mplayer %s &' % uri)

    def loadMenuFiles(self):
        self.tree = xdg.Menu.parse("applications.menu")
        self.directory = self.tree.getEntries()
            
    def buildCategoryList(self):
        newCategoryList = [{"name": _("All Applications"), "icon": "application-x-executable", "tooltip": _("Show all applications"), "filter":"", "index": 0}]
        
        num = 1

        for child in self.directory:#.get_contents():
            if isinstance(child, xdg.Menu.Menu):
                newCategoryList.append({"name": child.getName(), "icon": child.getIcon(), "tooltip": child.getComment(), "filter": child.getName(), "index": num})            
        num += 1
        
        newCategoryList.append({"name": _("My Computer"), "icon": "computer", "tooltip": _("Show all Places"), "filter": _("My Computer"), "index": num})          
        newCategoryList.append({"name": _("Recent"), "icon": "document-open-recent", "tooltip": _("Recent All"), "filter": _("Recent"), "index": num + 1})
        newCategoryList.append({"name": _("Favorites"), "icon": "emblem-favorite", "tooltip": _("Show all Favorites"), "filter": _("Favorites"), "index": num + 2})
        return newCategoryList

    # Build a list containing the DesktopEntry object and the category of each application in the menu
    def buildApplicationList(self):

        newApplicationsList = []
        self.directory = self.tree.getEntries()
        
        def find_applications_recursively(app_list, directory, catName):
            for item in directory.getEntries():
                if isinstance(item, xdg.Menu.MenuEntry):
                    app_list.append({"entry": item, "category": catName})
                elif isinstance(item, xdg.Menu.Menu):
                    find_applications_recursively(app_list, item, catName)
        
        for entry in self.directory:#.get_contents():
            if isinstance(entry, xdg.Menu.Menu):
                for item in entry.getEntries():
                    if isinstance(item, xdg.Menu.Menu):
                        find_applications_recursively(newApplicationsList, item, entry.getName())
                    elif isinstance(item, xdg.Menu.MenuEntry):
                        newApplicationsList.append({"entry": item, "category": entry.getName()})                    
        return newApplicationsList        