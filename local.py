#!/usr/bin/python
'''hechao@115.com'''
import os
try:
	INSTALL_PREFIX = open("/etc/ymenu/prefix").read()[:-1] 
except:
	INSTALL_PREFIX = '/usr'

#files = ['src/lib/ymenu/GNOME_YMenu.server','src/share/gnome-do/YMenu.desktop']

f = open('src/lib/ymenu/ymenu.server').read()
r = f.replace('/usr/lib/ymenu/',INSTALL_PREFIX + '/lib/ymenu/')
a = open('src/lib/bonobo/ymenu.server','w')
a.write(r)
a.close()

print 'Preparing to install translation'
podir = os.path.join (os.path.realpath ("."), "po")
print podir
if os.path.isdir (podir):
	print 'installing translations'
	buildcmd = "msgfmt -o src/share/locale/%s/LC_MESSAGES/%s.mo po/%s.po"
	
	for name in os.listdir (podir):		
		if name.endswith('.po'):
			dname = name.split('-')[1].split('.')[0]
			name = name[:-3]
			
			print 'Creating language Binary for : ' + name
			if not os.path.isdir ("src/share/locale/%s/LC_MESSAGES" % dname):
				os.makedirs ("src/share/locale/%s/LC_MESSAGES" % dname)
			os.system (buildcmd % (dname,name.replace('-'+dname,''), name))
			
				

