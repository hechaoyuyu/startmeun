#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import cairo
#import pango
import gtk
import gobject
import cairo_drawing

class PanelTopWindow():
	def __init__(self):
		self.aux_window = gtk.Window()
		self.scale = 1
		self.aux_window.set_skip_taskbar_hint(1)
		self.aux_window.set_skip_pager_hint(1)
		self.aux_window.set_app_paintable(True)
		self.aux_window.stick()				 #Make this appear on all desktops
		#Connect graphical events
		self.aux_window.connect("composited-changed", self.composite_changed)
		self.aux_window.connect('expose-event', self.Aux_win_screenchange)
		self.aux_window.connect('screen-changed', self.screen_changed)
		self.aux_window.connect('destroy', self.undestroy)
		
		self.eventbox = gtk.EventBox()
		self.eventbox.set_above_child (0)
		self.eventbox.set_visible_window(0)
		self.aux_window.add(self.eventbox)
		#Set up cairo image objects
		self.icon = None #cairo.ImageSurface
		self.screen_changed(self.aux_window)
		self.aux_window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DOCK)
		
		#Show all gtk widgets
		self.aux_window.resize(1,1)
		self.aux_window.show_all()
		self.aux_window.hide()
		self.opacity = 0
		if self.aux_window.is_composited () :
			self.aux_window.show_all()
			self.aux_window.set_opacity(self.opacity)


	def composite_changed(self,widget):
		self.aux_window.hide()
		self.aux_window.show_all()
		if not self.aux_window.is_composited () :
			self.aux_window.hide()

	def show_window(self):
		self.aux_window.show_all()
		

	def fade(self):
		self.opacity = self.opacity + 0.1
		self.aux_window.set_opacity(self.opacity)
		if self.opacity == 1: return False
		return True

	def hide_window(self):
		self.aux_window.hide()

	def screen_changed(self,widget):
		# Screen change event
		screen = widget.get_screen()
		colormap = screen.get_rgba_colormap()
		widget.set_colormap(colormap)

	def undestroy(self,event):
		#Callback for user window destroy (i.e. sporadic alt-f4 ing by the user)
		#self.parent.auxdestroyed()
		pass #FIXME

	def Aux_win_screenchange(self,widget, event):
		self.timer = gobject.timeout_add(100,self.fade)
		if self.icon:
			self.draw_win()
				

	
	def draw_win(self,image=None):
	   # Orb Top Screen change event
		self.cr = self.aux_window.window.cairo_create()
		self.cr.set_source_rgba(1.0, 1.0, 1.0, 0.0) # Transparent
		self.cr.set_operator(cairo.OPERATOR_SOURCE)
		# Draw the graphics
		if image== None:	
			image = self.image
		try:
			cairo_drawing.draw_scaled_image(self.cr,0,0,image,int(self.w*self.scale),int(self.h*self.scale))
		except:pass

	def move(self,x,y):
		# Relocate the window
		self.aux_window.move(x,y)

	def destroy(self):
		# Remove the window
		self.aux_window.destroy()

	def set_scale(self,scale):
		
		#self.aux_window.resize(int(self.w*scale),int(self.h*scale))
		self.scale = scale

	def update(self):
		# Update the screen profile on request
		self.screen_changed(self.aux_window)
		
	def updateimage(self,image):
		
		# Update the graphic being displayed (first image has size priority)
		self.icon = gtk.gdk.pixbuf_new_from_file(image)
		self.image = image
		self.w = self.icon.get_width()
		self.h = self.icon.get_height()

		self.aux_window.resize(int(self.w*self.scale),int(self.h*self.scale))
		if self.icon:
			self.draw_win(image)


	def get_height(self):
		if self.icon:
			return int(self.icon.get_height()*self.scale)
		else:
			print "!"
			return 0
