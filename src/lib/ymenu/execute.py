# -*- coding:utf-8 -*-
import os
import string

def RemoveArgs(Execline):
	NewExecline = []
        Specials=["\"%c\"", "%f","%F","%u","%U","%d","%D","%n","%N","%i","%c","%k","%v","%m","%M", "-caption", "/bin/sh", "sh", "STARTED_FROM_MENU=yes"]
	for elem in Execline:
		elem = elem.replace("'","")
                elem = elem.replace("\\\\","\\")
		if elem not in Specials:
			NewExecline.append(elem)
	return NewExecline

# Actually execute the command
def Execute(self,cmd ):
        cmd = cmd.split()   
	cmd = RemoveArgs(cmd)
        cmd = string.join(cmd,' ')
        print "cmd = %s" % cmd
        os.system('%s &' % cmd)
		
