#!/usr/bin/env python

from autopilot import introspection
from autopilot.display import Display
from autopilot.input import Pointer, Touch
import dbus
import os
import sys


def help():
    print "Usage:"
    print "Run the script without any argument to unlock with assertion"
    print ""
    print "option -q:"
    print "Execute with parameter -q to unlock the screen quickly without introspection"


def start_unity_in_testability():
    override_file = "~/.config/upstart/unity8.override"

    os.system('echo "exec unity8 -testability" > ~/.config/upstart/unity8.override')
    os.system('echo "kill timeout 30" >> ~/.config/upstart/unity8.override')    

    print "----------------------------------------------------------------------"
    print "Stopping Unity"
    os.system('/sbin/stop unity8')
    print "Unity stopped"
    os.system('rm -f /tmp/mir_socket')

    print "----------------------------------------------------------------------"
    print "Taking screen lock (#1235000)"
    bus = dbus.SystemBus()
    powerd = bus.get_object('com.canonical.powerd', '/com/canonical/powerd')
    powerd_cookie = powerd.requestSysState("autopilot-lock", 1, dbus_interface='com.canonical.powerd')
    print "----------------------------------------------------------------------"
    print "Starting Unity with testability"
    os.system('/sbin/start unity8')
    print "Unity started"
    print "----------------------------------------------------------------------"
    print "Releasing screen lock (#1235000)"
    powerd.clearSysState(powerd_cookie, dbus_interface='com.canonical.powerd')

    print "----------------------------------------------------------------------"
    if os.path.exists(override_file):
        os.remove(override_file)
    print "Cleaned up upstart override"
    print "----------------------------------------------------------------------"

    print "Turning on the screen"
    print ""


def unlock_screen():
    input_device = Touch.create()
    pointing_device = Pointer(input_device)
    conn = "com.canonical.Shell.BottomBarVisibilityCommunicator"
    unity8 = introspection.get_proxy_object_for_existing_process(connection_name=conn)
    greeter = unity8.select_single("Greeter")
    x, y, w, h = greeter.globalRect
    tx = x + w
    ty = y + (h / 2)

    pointing_device.drag(tx, ty, tx / 2, ty)
    try:
        greeter.shown.wait_for(False)
    except AssertionError:
        print "----------------------------------------------------------------------"
        print "THE SCREEN DIDN'T UNLOCK THE FIRST TRY, NOW ATTEMPTING A BLIND SWIPE"
        unlock_screen_blind(greeter)


def unlock_screen_blind(greeter=None):
    input_device = Touch.create()
    pointing_device = Pointer(input_device)
    x, y, w, h = Display.create(preferred_backend='UPA').get_screen_geometry(0)
    tx = x + w
    ty = y + (h / 2)

    pointing_device.drag(tx, ty, tx / 2, ty)
    if greeter is not None:
        try:
            greeter.shown.wait_for(False)
            if greeter.shown is False:
                print ""
                print "THE SCREEN IS NOW UNLOCKED"
        except AssertionError:
            print "----------------------------------------------------------------------"
            "THE SCREEN DIDN'T UNLOCK, RESTART THE DEVICE AND RUN THE SCRIPT AGAIN"


if len(sys.argv) >= 2 and sys.argv[1] == '-q':
    unlock_screen_blind()
elif len(sys.argv) >= 2 and sys.argv[1] == '-h':
    help()
else:
    start_unity_in_testability()
    unlock_screen()
