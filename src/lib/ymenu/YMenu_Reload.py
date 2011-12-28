#!/usr/bin/env python

import gconf
import os
object_name = "ymenu_screen0"
object_dir  = "/apps/panel/applets/"
object_client = gconf.client_get_default()
appletidlist = object_client.get_list("/apps/panel/general/applet_id_list", "string")
for applet in appletidlist:
    applet_id = object_client.get_string("/apps/panel/applets/" + applet + "/applet_iid")
    panel_position = object_client.get_int("/apps/panel/applets/" + applet + "/position")
    if applet_id == "OAFIID:GNOME_YMenu":
        panel = object_client.get_string("/apps/panel/applets/" + applet + "/toplevel_id")
        appletidlist.remove(applet)
        object_client.set_list("/apps/panel/general/applet_id_list", gconf.VALUE_STRING, appletidlist)
        os.system("sleep 0.3")

        object_client.set_string(object_dir + object_name +"/"+ "action_type", "lock")
        object_client.set_bool(object_dir + object_name +"/"+ "locked", True)
        object_client.set_int(object_dir + object_name +"/"+ "position", 0)
        object_client.set_string(object_dir + object_name +"/"+ "toplevel_id", panel)
        object_client.set_string(object_dir + object_name +"/"+ "object_type", "bonobo-applet")
        object_client.set_string(object_dir + object_name +"/"+ "applet_iid", applet_id)

        appletidlist.append(object_name)
        object_client.set_list("/apps/panel/general/applet_id_list", gconf.VALUE_STRING, appletidlist)
os.system("sleep 0.3")
