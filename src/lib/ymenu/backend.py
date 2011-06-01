#!/usr/bin/env python

import os

try:
	import gconf
	gconf_client = gconf.client_get_default()
	BACKEND = 'gconf'
	#print "gconf backend"
except:
	BACKEND = 'xml'
	import xml.dom.minidom
	#print "xml backend"

HomeDirectory = os.path.expanduser("~")
ConfigDirectory = HomeDirectory + '/.ymenu'
gconf_app_key = '/apps/ymenu'

def save_setting(name,value):

	if BACKEND == 'gconf':
		if isinstance(value, int) or isinstance(value, float):
			gconf_client.set_int(gconf_app_key + '/' + name , int(value))
		elif isinstance(value, str):
			gconf_client.set_string(gconf_app_key + '/' + name , str(value))
		elif isinstance(value, list):
			gconf_client.set_list(gconf_app_key + '/' + name ,1, value)

	elif BACKEND == 'xml':
		if name == '': return
		if os.path.isfile(ConfigDirectory + "/.YMenu-Settings.xml"):
			XMLSettings = xml.dom.minidom.parse(ConfigDirectory + "/.YMenu-Settings.xml")
			XBase = XMLSettings.getElementsByTagName('YMenu')[0]
		else:
			XMLSettings = xml.dom.minidom.Document()
			XBase = XMLSettings.createElement('YMenu')

		try:
			node = XMLSettings.getElementsByTagName('settings')[0]
		except:
			node = XMLSettings.createElement('settings')
		node.setAttribute(name, str(value))
		XBase.appendChild(node)
		XMLSettings.appendChild(XBase)
		file = open(ConfigDirectory + "/.YMenu-Settings.xml","w")
		XMLSettings.writexml(file, "    ", "", "", "UTF-8")
		XMLSettings.unlink()

	else:
		pass



def load_setting(name):
	if BACKEND == 'gconf':
		try:
			typ =  gconf_client.get_without_default(gconf_app_key + "/" + name).type
			
			if typ == 1:
				return gconf_client.get_string(gconf_app_key + "/" + name)
	
			elif typ == 2:
				return gconf_client.get_int(gconf_app_key + "/" + name)
                        

			elif typ == 6:
				return gconf_client.get_list(gconf_app_key + "/" + name,1)
	
	
			else:
				if name == 'favorites': return []
				return None

		except : 
			if name == 'favorites': return []
		return None



	elif BACKEND == 'xml':
		if os.path.isfile(ConfigDirectory + "/.YMenu-Settings.xml"):
			XMLSettings = xml.dom.minidom.parse(ConfigDirectory + "/.YMenu-Settings.xml")
			#print XMLSettings.getElementsByTagName('YMenu')[0].childNodes[0].localName
			x = XMLSettings.getElementsByTagName('YMenu')[0].getElementsByTagName("settings")[0]
			try:
				x = x.attributes[name].value
				try: 
					a = int(x)
					
				except:
					if str(x).find('[]') != -1 and name == 'favorites': return []
					

					if str(x).find(':') != -1:
						
						x = str(x).replace(" u'","").replace("u'","").replace("[","").replace("]","").replace("'","").replace('&quot;','"')
						a = x.split(',')
						print a				
					else:
						a = str(x)
					
				
				return a


			except: 
				if name == 'favorites': return []
				return None

		else: 
			return None

	else:
		pass


def get_default_mail_client():

	if BACKEND == 'gconf':
		return gconf_client.get_string("/desktop/gnome/url-handlers/mailto/command")
	elif BACKEND == 'xml':
		return "xdg-open mailto:"
	else:
		pass

def get_default_internet_browser():

	if BACKEND == 'gconf':
		return gconf_client.get_string("/desktop/gnome/url-handlers/http/command")#"/desktop/gnome/applications/browser/exec")
	elif BACKEND == 'xml':
		return "xdg-open http:"
	else:
		pass

