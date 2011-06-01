#!/usr/bin/env python

if len(sys.argv) < 2 or sys.argv[1] == "--help":
	print "YMenu session manager HELP====================="
	print "Command:		 What it does:\n"
	print "shutdown		 Shutdown the PC"
	print "reboot		 Reboot the PC"
	print "hibernate	 Hibernate the PC"
	print "suspend		 Suspend the PC"
	print "================================================="

else:

	import dbus
	bus = dbus.SessionBus()
	bus2 = dbus.SystemBus()
	power = None
	power2 = None
	power4 = None
	try:
		devobj = bus.get_object('org.gnome.PowerManagement', 'org/gnome/PowerManagement')
		power = dbus.Interface(devobj, "org/gnome/PowerManagement")
		print "using gnome < 2.28"
	except:
		try:
			# patched version http://www.electric-spoon.com/doc/gnome-session/dbus/gnome-session.html#org.gnome.SessionManager.RequestReboot
			# normal version http://people.gnome.org/~mccann/gnome-session/docs/gnome-session.html
			devobj = bus.get_object('org.gnome.SessionManager', '/org/gnome/SessionManager')
			power2 = dbus.Interface(devobj, "org.gnome.SessionManager")
			print "using gnome >= 2.28"
		except:
			devobj = bus.get_object('org.kde.ksmserver', '/KSMServer')
			power4 = dbus.Interface(devobj, "org.kde.KSMServerInterface")	
			print "using kde"
		try:
			#http://hal.freedesktop.org/docs/DeviceKit-power/Power.html
			devobj2 = bus2.get_object('org.freedesktop.DeviceKit.Power', '/org/freedesktop/DeviceKit/Power')
			power3 = dbus.Interface(devobj2, "org.freedesktop.DeviceKit.Power")
			print "using Devicekit.Power"
		except:
			#http://upower.freedesktop.org/docs/UPower.html
			devobj2 = bus2.get_object('org.freedesktop.UPower', '/org/freedesktop/UPower')
			power3 = dbus.Interface(devobj2, "org.freedesktop.UPower")
			print "using UPower"



	if power:
		if sys.argv[1] == "suspend":
			power.Suspend()
		elif sys.argv[1] == "hibernate":
			power.Hibernate()
		elif sys.argv[1] == "reboot":
			power.Reboot()
		elif sys.argv[1] == "shutdown":
			power.Shutdown()

	if power2:

		if sys.argv[1] == "suspend":
			power3.Suspend()
		elif sys.argv[1] == "hibernate":
			power3.Hibernate()
		elif sys.argv[1] == "reboot":
			try:
				power2.RequestReboot() #this works only for a pathed version ...
			except:
				power2.Shutdown() #if it doesnt have the patched version show
		elif sys.argv[1] == "shutdown":
			try:
				power2.RequestShutdown() #this works only for a pathed version ...
			except:
				power2.Shutdown() #if it doesnt have the patched version show

	if power4:

		if sys.argv[1] == "suspend":
			power3.Suspend()
		elif sys.argv[1] == "hibernate":
			power3.Hibernate()
		elif sys.argv[1] == "reboot":
			power4.logout(0,1,0)
		elif sys.argv[1] == "shutdown":
			power4.logout(0,2,0)
