#!/usr/bin/env python
import Globals
import gtk


def draw_scaled_image(ctx, x, y, pix, w, h):
    """Draws a picture from specified path with a certain width and height"""
    ctx.save()
    ctx.translate(x, y)
    pixbuf = gtk.gdk.pixbuf_new_from_file(pix).scale_simple(w, h, gtk.gdk.INTERP_BILINEAR)

    if Globals.flip != None:
        pixbuf = pixbuf.flip(Globals.flip)

    image = ctx.set_source_pixbuf(pixbuf, 0, 0)
    ctx.paint()
    pixbuf = None
    image = None
    ctx.restore()

def draw_image(ctx, x, y, pix, w, h, flip=True):
    """Draws a picture from specified path with a certain width and height"""

    ctx.save()
    ctx.translate(x, y)
    pixbuf = gtk.gdk.pixbuf_new_from_file(pix).scale_simple(w, h, gtk.gdk.INTERP_BILINEAR)
    if Globals.flip != None and flip is True:
        pixbuf = pixbuf.flip(Globals.flip)
    image = ctx.set_source_pixbuf(pixbuf, 0, 0)
    ctx.paint()
    pixbuf = None
    image = None
    ctx.restore()

def draw_pixbuf(ctx, pixbuf):
    """Draws a picture from specified path with a certain width and height"""

    ctx.save()
    image = ctx.set_source_pixbuf(pixbuf, 0, 0)
    ctx.paint()
    image = None
    ctx.restore()

def draw_enhanced_image(ctx, x, y, pix):
    """Draws a picture from specified path with a certain width and height"""

    ctx.save()
    ctx.translate(x, y)
    pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(pix, Globals.MenuWidth, Globals.MenuHeight )
    #pixbuf = gtk.gdk.pixbuf_new_from_file(pix)
    if Globals.flip != None:
        pixbuf = pixbuf.flip(Globals.flip)
    iw = pixbuf.get_width()
    ih = pixbuf.get_height()
    #We do this so the themes with fully transparent background are still clickable
    pixbuf.composite(pixbuf, 0, 0, iw, ih, 0, 0, 1, 1, gtk.gdk.INTERP_NEAREST, 255)
    pixbuf.composite(pixbuf, 0, 0, iw, ih, 0, 0, 1, 1, gtk.gdk.INTERP_NEAREST, 255)
    image = ctx.set_source_pixbuf(pixbuf, 0, 0)
    #ctx.paint()
    pixbuf = None
    image = None
    ctx.restore()

def draw_background_pixbuf(ctx, pixbuf, flip=True):
    """Draws a picture from specified path with a certain width and height"""
		
    ctx.save()
    if Globals.flip != None and flip is True:
        pixbuf = pixbuf.flip(Globals.flip)
    image = ctx.set_source_pixbuf(pixbuf, 0, 0)
    ctx.paint()
    pixbuf = None
    image = None
    ctx.restore()