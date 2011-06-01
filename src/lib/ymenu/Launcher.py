#!/usr/bin/env python

import Globals
import os
import gobject


class Launcher(gobject.GObject):
	__gsignals__ = {
        'special-command': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        }

	def __init__(self):
		gobject.GObject.__init__(self)
		self.GnomeMenu = None


	def Launch(self,command,tag=0,name=None,path=None):
		if tag == 0:
			c = self.LookUpCommand(command)
			if c != '':
				os.system(c)
	
	def LookUpCommand(self,command):
		
		for i in range(0,len(Globals.MenuActions)):
			if Globals.MenuActions[i]==command:
               			if command == "Search":
                                    return '%s --named=%s --start&' %(Globals.MenuCommands[i],Globals.searchitem)
				return '%s &' % Globals.MenuCommands[i]


