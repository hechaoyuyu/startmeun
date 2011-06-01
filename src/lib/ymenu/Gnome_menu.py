#!/usr/bin/env python
 
import sys
try:
	from Xlib import X, display, Xatom
	import Xlib
except:
	import utils
	utils.show_message("Dependency missing: python-xlib not installed.")
	sys.exit ()

def get_atom(display, atom_name):

	atom = XInternAtom(disp, atom_name, False)
	if atom == None:
		print "This action requires python xlib installed, please install it for the menu to appear"
		sys.exit ()
	return atom

# Get display
disp =  Xlib.display.Display()
# Get atoms for panel and run dialog menu
gnome_panel_atom = disp.intern_atom("_GNOME_PANEL_ACTION")
run_atom = disp.intern_atom("_GNOME_PANEL_ACTION_MAIN_MENU") #"_GNOME_PANEL_ACTION_RUN_DIALOG"

args = [0,0,0]
time = X.CurrentTime
data = (32,([run_atom,time]+args))
event = Xlib.protocol.event.ClientMessage(window = disp.screen().root,client_type = gnome_panel_atom, data = data)
# Send event to display
disp.send_event(disp.screen().root,event, event_mask=X.StructureNotifyMask, propagate=0)
# Show menu
disp.sync()
