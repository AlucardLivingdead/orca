# Orca
#
# Copyright 2005 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

"""Bug reproducer for bug x.  This standalone module talks
directly with the AT-SPI Registry via its IDL interfaces.  No Orca
logic or code is stuck in the middle.

To run this module, merely type 'python bug_x.py'.

To reproduce bug x, follow these steps:

1)
2)
3)
"""

import time

import bonobo
import ORBit

ORBit.load_typelib("Accessibility")
ORBit.CORBA.ORB_init()

import Accessibility
import Accessibility__POA

listeners = []
keystrokeListeners = []

registry = bonobo.get_object("OAFIID:Accessibility_Registry:1.0",
                             "Accessibility/Registry")

########################################################################
#                                                                      #
# Event listener classes for global and keystroke events               #
#                                                                      #
########################################################################

class EventListener(Accessibility__POA.EventListener):
    """Registers a callback directly with the AT-SPI Registry for the
    given event type.  Most users of this module will not use this
    class directly, but will instead use the addEventListener method.
    """

    def __init__(self, registry, callback, eventType):
        self.registry  = registry
        self.callback  = callback
        self.eventType = eventType
        self.register()

    def ref(self): pass

    def unref(self): pass

    def queryInterface(self, repo_id):
	thiz = None
        if repo_id == "IDL:Accessibility/EventListener:1.0":
            thiz = self._this()
	return thiz

    def register(self):
        self._default_POA().the_POAManager.activate()
        self.registry.registerGlobalEventListener(self._this(),
                                                  self.eventType)
        self.__registered = True
        return self.__registered

    def deregister(self):
        if not self.__registered:
            return
        self.registry.deregisterGlobalEventListener(self._this(),
                                                    self.eventType)
        self.__registered = False

    def notifyEvent(self, event):
        self.callback(event)

    def __del__(self):
        self.deregister()

class KeystrokeListener(Accessibility__POA.DeviceEventListener):
    """Registers a callback directly with the AT-SPI Registry for the
    given keystroke.  Most users of this module will not use this
    class directly, but will instead use the registerKeystrokeListeners
    method."""

    def keyEventToString(event):
        return ("KEYEVENT: type=%d\n" % event.type) \
               + ("          hw_code=%d\n" % event.hw_code) \
               + ("          modifiers=%d\n" % event.modifiers) \
               + ("          event_string=(%s)\n" % event.event_string) \
               + ("          is_text=%s\n" % event.is_text) \
               + ("          time=%f" % time.time())

    keyEventToString = staticmethod(keyEventToString)

    def __init__(self, registry, callback,
                 keyset, mask, type, synchronous, preemptive, isGlobal):
        self._default_POA().the_POAManager.activate()

        self.registry         = registry
        self.callback         = callback
        self.keyset           = keyset
        self.mask             = mask
        self.type             = type
        self.mode             = Accessibility.EventListenerMode()
        self.mode.synchronous = synchronous
        self.mode.preemptive  = preemptive
        self.mode._global     = isGlobal
        self.register()

    def ref(self): pass

    def unref(self): pass

    def queryInterface(self, repo_id):
	thiz = None
        if repo_id == "IDL:Accessibility/EventListener:1.0":
            thiz = self._this()
	return thiz

    def register(self):
        d = self.registry.getDeviceEventController()
        if d.registerKeystrokeListener(self._this(),
                                       self.keyset,
                                       self.mask,
                                       self.type,
                                       self.mode):
            self.__registered = True
        else:
            self.__registered = False
        return self.__registered

    def deregister(self):
        if not self.__registered:
            return
        d = self.registry.getDeviceEventController()
        d.deregisterKeystrokeListener(self._this(),
                                      self.keyset,
                                      self.mask,
                                      self.type)
        self.__registered = False

    def notifyEvent(self, event):
        """Called by the at-spi registry when a key is pressed or released.

        Arguments:
        - event: an at-spi DeviceEvent

        Returns True if the event has been consumed.
        """
        return self.callback(event)

    def __del__(self):
        self.deregister()

########################################################################
#                                                                      #
# Testing functions.                                                   #
#                                                                      #
########################################################################

def start():
    """Starts event notification with the AT-SPI Registry.  This method
    only returns after 'stop' has been called.
    """
    bonobo.main()

def stop():
    """Unregisters any event or keystroke listeners registered with
    the AT-SPI Registry and then stops event notification with the
    AT-SPI Registry.
    """
    for listener in (listeners + keystrokeListeners):
        listener.deregister()
    bonobo.main_quit()

def registerEventListener(callback, eventType):
    global listeners
    listener = EventListener(registry, callback, eventType)
    listeners.append(listener)

def registerKeystrokeListeners(callback):
    """Registers a single callback for all possible keystrokes.
    """
    global keystrokeListeners
    for i in range(0, (1 << (Accessibility.MODIFIER_NUMLOCK + 1))):
        keystrokeListeners.append(
            KeystrokeListener(registry,
                              callback, # callback
                              [],       # keyset
                              i,        # modifier mask
                              [Accessibility.KEY_PRESSED_EVENT,
                               Accessibility.KEY_RELEASED_EVENT],
                              True,     # synchronous
                              True,     # preemptive
                              False))   # global

eventTypes = [
    "focus:",
##     "mouse:rel",
##     "mouse:button",
##     "mouse:abs",
##     "keyboard:modifiers",
##     "object:property-change",
##     "object:property-change:accessible-name",
##     "object:property-change:accessible-description",
##     "object:property-change:accessible-parent",
##     "object:state-changed",
##     "object:state-changed:focused",
##     "object:selection-changed",
##     "object:children-changed"
##     "object:active-descendant-changed"
##     "object:visible-data-changed"
##     "object:text-selection-changed",
##     "object:text-caret-moved",
##     "object:text-changed",
##     "object:column-inserted",
##     "object:row-inserted",
##     "object:column-reordered",
##     "object:row-reordered",
##     "object:column-deleted",
##     "object:row-deleted",
##     "object:model-changed",
##     "object:link-selected",
##     "object:bounds-changed",
##     "window:minimize",
##     "window:maximize",
##     "window:restore",
##     "window:activate",
##     "window:create",
##     "window:deactivate",
##     "window:close",
##     "window:lower",
##     "window:raise",
##     "window:resize",
##     "window:shade",
##     "window:unshade",
##     "object:property-change:accessible-table-summary",
##     "object:property-change:accessible-table-row-header",
##     "object:property-change:accessible-table-column-header",
##     "object:property-change:accessible-table-summary",
##     "object:property-change:accessible-table-row-description",
##     "object:property-change:accessible-table-column-description",
##     "object:test",
##     "window:restyle",
##     "window:desktop-create",
##     "window:desktop-destroy"
]

def printTopObject(child):
    parent = child
    while parent:
	if not parent.parent:
            print "TOP OBJECT:", parent.name, parent.getRoleName()
            #if parent.getRole() != Accessibility.ROLE_APPLICATION:
            #    print "ERROR: TOP OBJECT NOT AN APPLICATION."
            #    shutdownAndExit()
        parent = parent.parent
	
def printDesktops():
    print "There are %d desktops" % registry.getDesktopCount()
    for i in range(0,registry.getDesktopCount()):
        desktop = registry.getDesktop(i)
        print "  Desktop %d (name=%s) has %d apps" \
              % (i, desktop.name, desktop.childCount)
        for j in range(0, desktop.childCount):
            app = desktop.getChildAtIndex(j)
            print "    App %d: name=%s role=%s" \
		  % (j, app.name, app.getRoleName())
            for k in range(0, app.childCount):
                child = app.getChildAtIndex(k)
                print "      Child %d: name=%s role=%s" \
                      % (k, child.name, child.getRoleName())
               
def findActiveWindow():
    desktop = registry.getDesktop(0)
    window = None
    for j in range(0, desktop.childCount):
        app = desktop.getChildAtIndex(j)
        for k in range(0, app.childCount):
            child = app.getChildAtIndex(k)
            s = child.getState()
            s = s._narrow(Accessibility.StateSet)
            state = s.getStates()            
            if (state.count(Accessibility.STATE_ACTIVE) > 0) \
               or (state.count(Accessibility.STATE_FOCUSED) > 0):
                window = child
		break
        if window:
           break
    return window
 
def findAllText(root):
    if not root:
        return
    text = root.queryInterface("IDL:Accessibility/Text:1.0")
    if text:
        text = text._narrow(Accessibility.Text)
        print "Text (len=%d): %s" % (text.characterCount, text.getText(0, -1))
    for i in range(0, root.childCount):
        findAllText(root.getChildAtIndex(i))

def notifyEvent(event):
        print event.type, event.source.name, event.source.getRoleName(), \
              event.detail1, event.detail2,  \
              event.any_data
	printTopObject(event.source)

def notifyKeystroke(event):
    print "keystroke type=%d hw_code=%d modifiers=%d event_string=(%s) " \
          "is_text=%s" \
          % (event.type, event.hw_code, event.modifiers, event.event_string,
             event.is_text)
    if event.event_string == "F12":
        shutdownAndExit()
    elif event.event_string == "F11":
       findAllText(findActiveWindow())
       return True
    return False

def shutdownAndExit(signum=None, frame=None):
    stop()
    print "Goodbye."

def test():
    print "Press F12 to Exit."
    printDesktops()
    for eventType in eventTypes:
        registerEventListener(notifyEvent, eventType)
    registerKeystrokeListeners(notifyKeystroke)
    start()

if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGINT, shutdownAndExit)
    signal.signal(signal.SIGQUIT, shutdownAndExit)
    test()
