# Orca
#
# Copyright 2004-2005 Sun Microsystems Inc.
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

import gtk
import os, signal, sys

import atspi
import braille
import debug
import keynames
import keybindings
#import mag - [[[TODO: WDW - disable until I can figure out how to
#             resolve the GNOME reference in mag.py.  This is logged
#             as bugzilla bug 319643.]]]
import settings
import speech

from input_event import BrailleEvent
from input_event import KeyboardEvent
from input_event import InputEventHandler

from orca_i18n import _           # for gettext support

# The InputEvent instance representing the last input event.  This is
# set each time a keyboard or braille event is received.
#
lastInputEvent = None

# A new modifier to use (currently bound to the "Insert" key) to represent
# special Orca key sequences.
#
MODIFIER_ORCA = 8

########################################################################
#                                                                      #
# METHODS FOR HANDLING PRESENTATION MANAGERS                           #
#                                                                      #
# A presentation manager is what reacts to AT-SPI object events as     #
# well as user input events (keyboard and Braille) to present info     #
# to the user.                                                         #
#                                                                      #
########################################################################

# The known presentation managers (set up in start())
#
_PRESENTATION_MANAGERS = None

# The current presentation manager, which is an index into the
# _PRESENTATION_MANAGERS list.
#
_currentPresentationManager = -1

def _switchToPresentationManager(index):
    """Switches to the given presentation manager.

    Arguments:
    - index: an index into _PRESENTATION_MANAGERS
    """

    global _currentPresentationManager

    if _currentPresentationManager >= 0:
        _PRESENTATION_MANAGERS[_currentPresentationManager].deactivate()

    _currentPresentationManager = index

    # Wrap the presenter index around.
    #
    if _currentPresentationManager >= len(_PRESENTATION_MANAGERS):
        _currentPresentationManager = 0
    elif _currentPresentationManager < 0:
        _currentPresentationManager = len(_PRESENTATION_MANAGERS) - 1

    _PRESENTATION_MANAGERS[_currentPresentationManager].activate()

def _switchToNextPresentationManager(script=None, inputEvent=None):
    """Switches to the next presentation manager.

    Arguments:
    - inputEvent: the InputEvent instance that caused this to be called.

    Returns True indicating the event should be consumed.
    """

    _switchToPresentationManager(_currentPresentationManager + 1)
    return True

########################################################################
#                                                                      #
# METHODS TO HANDLE APPLICATION LIST AND FOCUSED OBJECTS               #
#                                                                      #
########################################################################

# List of all the running apps we know about.  Each element is a Python
# Accessible instance.
#
apps = []

# The Accessible that has visual focus.
#
locusOfFocus = None

def setLocusOfFocus(event, obj, notifyPresentationManager=True):
    """Sets the locus of focus (i.e., the object with visual focus) and
    notifies the current presentation manager of the change.

    Arguments:
    - event: if not None, the Event that caused this to happen
    - obj: the Accessible with the new locus of focus.
    - notifyPresentationManager: if True, propagate this event
    """

    global locusOfFocus

    if obj == locusOfFocus:
        return

    oldLocusOfFocus = locusOfFocus
    if oldLocusOfFocus and not oldLocusOfFocus.valid:
        oldLocusOfFocus = None

    locusOfFocus = obj
    if locusOfFocus and not locusOfFocus.valid:
        locusOfFocus = None

    if locusOfFocus:
        appname = ""
        if not locusOfFocus.app:
            appname = "None"
        else:
            appname = "'" + locusOfFocus.app.name + "'"

        debug.println(debug.LEVEL_FINE,
                      "LOCUS OF FOCUS: app=%s name='%s' role='%s'" \
                      % (appname, locusOfFocus.name, locusOfFocus.role))

        if event:
            debug.println(debug.LEVEL_FINE,
                          "                event='%s'" % event.type)
        else:
            debug.println(debug.LEVEL_FINE,
                          "                event=None")
    else:
        if event:
            debug.println(debug.LEVEL_FINE,
                          "LOCUS OF FOCUS: None event='%s'" % event.type)
        else:
            debug.println(debug.LEVEL_FINE,
                          "LOCUS OF FOCUS: None event=None")

    if notifyPresentationManager and _currentPresentationManager >= 0:
        _PRESENTATION_MANAGERS[_currentPresentationManager].\
            locusOfFocusChanged(event, oldLocusOfFocus, locusOfFocus)

def visualAppearanceChanged(event, obj):
    """Called (typically by scripts) when the visual appearance of an object
    changes and notifies the current presentation manager of the change.  This
    method should not be called for objects whose visual appearance changes
    solely because of focus -- setLocusOfFocus is used for that.  Instead, it
    is intended mostly for objects whose notional 'value' has changed, such as
    a checkbox changing state, a progress bar advancing, a slider moving, text
    inserted, caret moved, etc.

    Arguments:
    - event: if not None, the Event that caused this to happen
    - obj: the Accessible whose visual appearance changed.
    """

    if _currentPresentationManager >= 0:
        _PRESENTATION_MANAGERS[_currentPresentationManager].\
            visualAppearanceChanged(event, obj)

def isInActiveApp(obj):
    """Returns True if the given object is from the same application that
    currently has keyboard focus.

    Arguments:
    - obj: an Accessible object
    """

    if not obj:
        return False
    else:
        return locusOfFocus and (locusOfFocus.app == obj.app)

def findActiveWindow():
    """Traverses the list of known apps looking for one who has an
    immediate child (i.e., a window) whose state includes the active state.

    Returns the Python Accessible of the window that's active or None if
    no windows are active.
    """

    window = None
    for app in apps:
        for i in range(0, app.childCount):
            state = app.child(i).state
            if state.count(atspi.Accessibility.STATE_ACTIVE) > 0:
                window = app.child(i)
		break

    return window

def _buildAppList(registry):
    """Retrieves the list of currently running apps for the desktop and
    populates the apps list attribute with these apps.
    """

    global apps

    debug.println(debug.LEVEL_FINEST,
                  "orca._buildAppList...")

    apps = []

    for i in range(0, registry.desktop.childCount):
        acc = registry.desktop.getChildAtIndex(i)
        try:
            app = atspi.Accessible.makeAccessible(acc)
            if app:
                apps.insert(0, app)
        except:
            debug.printException(debug.LEVEL_SEVERE)

    debug.println(debug.LEVEL_FINEST,
                  "...orca._buildAppList")

def _onChildrenChanged(e):
    """Tracks children-changed events on the desktop to determine when
    apps start and stop.

    Arguments:
    - e: at-spi event from the at-api registry
    """

    registry = atspi.Registry()
    if e.source == registry.desktop:

        # If the desktop is empty, the user has logged out-- shutdown Orca
        #
        try:
            if registry.desktop.childCount == 0:
                speech.speak(_("User logged out - shutting down."))
                shutdown()
                return
        except: # could be a CORBA.COMM_FAILURE
            debug.printException(debug.LEVEL_FINEST)
            shutdown()
            return

        # [[[TODO: WDW - Note the call to _buildAppList - that will update the
        # apps[] list.  If this logic is changed in the future, the apps list
        # will most likely needed to be updated here.]]]
        #
        _buildAppList(registry)

########################################################################
#                                                                      #
# Keyboard Event Recording Support                                     #
#                                                                      #
########################################################################

_recordingKeystrokes = False
_keystrokesFile = None

def _closeKeystrokeWindowAndRecord(entry, window):
    global _keystrokesFile
    window.destroy()
    entry_text = entry.get_text()
    _keystrokesFile = open(entry_text, 'w')

def _closeKeystrokeWindowAndCancel(window):
    global _recordingKeystrokes
    window.destroy()
    _recordingKeystrokes = False

def toggleKeystrokeRecording(script=None, inputEvent=None):
    """Toggles the recording of keystrokes on and off.  When the
    user presses the magic key (Pause), Orca will pop up a window
    requesting a filename.  When the user presses the close button,
    Orca will start recording keystrokes to the file and will continue
    recording them until the user presses the magic key again.

    This functionality is used primarily to help gather keystroke
    information for regression testing purposes.  The keystrokes are
    recorded in such a way that they can be played back via the
    src/tools/play_keystrokes.py utility.

    Arguments:
    - inputEvent: the key event (if any) which caused this to be called.

    Returns True indicating the event should be consumed.
    """

    global _recordingKeystrokes
    global _keystrokesFile

    if _recordingKeystrokes:
        # If the filename entry window is still up, we don't have a file
        # yet.
        #
        if _keystrokesFile:
            _keystrokesFile.close()
            _keystrokesFile = None
            _recordingKeystrokes = False
    else:
        _recordingKeystrokes = True
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_title("Keystroke Filename")

        vbox = gtk.VBox(False, 0)
        window.add(vbox)
        vbox.show()

        entry = gtk.Entry()
        entry.set_max_length(50)
        entry.set_editable(True)
        entry.set_text("keystrokes.txt")
        entry.select_region(0, len(entry.get_text()))
        # For now, do not allow "Return" to close the window - the reason
        # for this is that the key press closes the window, and the key
        # release will end up getting recorded.
        #
        #entry.connect("activate", _closeKeystrokeWindow, window)
        vbox.pack_start(entry, True, True, 0)
        entry.show()

        hbox = gtk.HBox(False, 0)
        vbox.add(hbox)
        hbox.show()

        ok = gtk.Button(stock=gtk.STOCK_OK)
        ok.connect("clicked", lambda w: _closeKeystrokeWindowAndRecord(\
            entry, \
            window))

        cancel = gtk.Button(stock=gtk.STOCK_CANCEL)
        cancel.connect("clicked", lambda w: _closeKeystrokeWindowAndCancel(\
            window))

        vbox.pack_start(cancel, True, True, 0)
        vbox.pack_start(ok, True, True, 0)

        ok.set_flags(gtk.CAN_DEFAULT)
        ok.grab_default()
        ok.show()
        cancel.show()

        window.set_modal(True)
        window.show()
    return True

########################################################################
#                                                                      #
# DEBUG support.                                                       #
#                                                                      #
########################################################################

def cycleDebugLevel(script=None, inputEvent=None):
    """Cycles the debug level at run time.

    Arguments:
    - inputEvent: the InputEvent instance that caused this to be called.

    Returns True indicating the event should be consumed.
    """

def cycleDebugLevel(script=None, inputEvent=None):
    global _debugLevel

    level = debug.getDebugLevel()
    
    if level == debug.LEVEL_ALL:
        level = debug.LEVEL_FINEST
    elif level == debug.LEVEL_FINEST:
        level = debug.LEVEL_FINER
    elif level == debug.LEVEL_FINER:
        level = debug.LEVEL_FINE
    elif level == debug.LEVEL_FINE:
        level = debug.LEVEL_CONFIGURATION
    elif level == debug.LEVEL_CONFIGURATION:
        level = debug.LEVEL_INFO
    elif level == debug.LEVEL_INFO:
        level = debug.LEVEL_WARNING
    elif level == debug.LEVEL_WARNING:
        level = debug.LEVEL_SEVERE
    elif level == debug.LEVEL_SEVERE:
        level = debug.LEVEL_OFF
    elif level == debug.LEVEL_OFF:
        level = debug.LEVEL_ALL

    debug.setDebugLevel(level)
    
    if level == debug.LEVEL_ALL:
        speech.speak(_("Debug level all."))
    elif level == debug.LEVEL_FINEST:
        speech.speak(_("Debug level finest."))
    elif level == debug.LEVEL_FINER:
        speech.speak(_("Debug level finer."))
    elif level == debug.LEVEL_FINE:
        speech.speak(("Debug level fine."))
    elif level == debug.LEVEL_CONFIGURATION:
        speech.speak("Debug level configuration.")
    elif level == debug.LEVEL_INFO:
        speech.speak("Debug level info.")
    elif level == debug.LEVEL_WARNING:
        speech.speak("Debug level warning.")
    elif level == debug.LEVEL_SEVERE:
        speech.speak("Debug level severe.")
    elif level == debug.LEVEL_OFF:
        speech.speak("Debug level off.")

    return True

def printApps(script=None, inputEvent=None):
    """Prints a list of all applications to stdout

    Arguments:
    - inputEvent: the InputEvent instance that caused this to be called.

    Returns True indicating the event should be consumed.
    """

    level = debug.LEVEL_OFF

    debug.println(level, "There are %d Accessible applications" % len(apps))
    for app in apps:
        debug.printDetails(level, "  App: ", app, False)
        for i in range(0, app.childCount):
            child = app.child(i)
            debug.printDetails(level, "    Window: ", child, False)
            if child.parent != app:
                debug.println(level,
                              "      WARNING: child's parent is not app!!!")

    return True

def printActiveApp(script=None, inputEvent=None):
    """Prints the active application.

    Arguments:
    - inputEvent: the key event (if any) which caused this to be called.

    Returns True indicating the event should be consumed.
    """

    level = debug.LEVEL_OFF

    window = findActiveWindow()
    if not window:
        debug.println(level, "Active application: None")
    else:
        app = window.app
        if not app:
            debug.println(level, "Active application: None")
        else:
            debug.println(level, "Active application: %s" % app.name)
            printAccessibleTree(level, "  ", findActiveWindow())

    return True

def printAncestry(script=None, inputEvent=None):
    """Prints the ancestry for the current locusOfFocus"""
    atspi.printAncestry(locusOfFocus)
    return True

def printHierarchy(script=None, inputEvent=None):
    """Prints the application for the current locusOfFocus"""
    if locusOfFocus:
        atspi.printHierarchy(locusOfFocus.app, locusOfFocus)
    return True

########################################################################
#                                                                      #
# METHODS FOR HANDLING LEARN MODE.                                     #
#                                                                      #
########################################################################

def enterLearnMode(script=None, inputEvent=None):
    """Turns learn mode on.  The user must press the escape key to exit
    learn mode.

    Returns True to indicate the input event has been consumed.
    """

    speech.speak(
        _("Entering learn mode.  Press any key to hear its function. " \
          + "To exit learn mode, press the escape key."))
    braille.displayMessage(_("Learn mode.  Press escape to exit."))
    settings.setLearnModeEnabled(True)
    return True

def exitLearnMode(script=None, inputEvent=None):
    """Turns learn mode off.

    Returns True to indicate the input event has been consumed.
    """

    speech.speak(_("Exiting learn mode."))
    braille.displayMessage(_("Exiting learn mode."))
    settings.setLearnModeEnabled(False)
    return True

########################################################################
#                                                                      #
# METHODS FOR PRE-PROCESSING AND MASSAGING KEYBOARD EVENTS.            #
#                                                                      #
# All keyboard events are funnelled through here first.  Orca itself   #
# might have global keybindings (e.g., to switch between presenters),  #
# but it will typically pass the event onto the currently active       #
# active presentation manager.                                         #
#                                                                      #
########################################################################

# Keybindings that Orca itself cares about.
#
_keybindings = None

# True if the insert key is currently pressed.  We will use the insert
# key as a modifier for Orca, and it will be presented as the "insert"
# modifier string.
#
_insertPressed = False

def _keyEcho(key):
    """If the keyEcho setting is enabled, echoes the key via speech.
    Uppercase keys will be spoken using the "uppercase" voice style,
    whereas lowercase keys will be spoken using the "default" voice style.

    Arguments:
    - key: a string representing the key name to echo.
    """

    if not settings.getSetting(settings.USE_KEY_ECHO, False):
        return
    if key.isupper():
        voices = settings.getSetting(settings.VOICES, None)
        speech.speak(key, voices[settings.UPPERCASE_VOICE])
    else:
        # Check to see if there are localized words to be spoken for
        # this key event.
        try:
            key = keynames.keynames[key]
        except:
            debug.printException(debug.LEVEL_FINEST)
            pass
        speech.speak(key)

def _processKeyboardEvent(event):
    """The primary key event handler for Orca.  Keeps track of various
    attributes, such as the lastInputEvent.  Also calls keyEcho as well
    as any local keybindings before passing the event on to the active
    presentation manager.  This method is called synchronously from the
    AT-SPI registry and should be performant.  In addition, it
    must return True if it has consumed the event (and False if not).

    Arguments:
    - event: an AT-SPI DeviceEvent

    Returns True if the event should be consumed.
    """

    global lastInputEvent
    global _insertPressed

    event_string = event.event_string

    # Log the keyboard event for future playback, if desired.
    #
    string = atspi.KeystrokeListener.keyEventToString(event)
    if _recordingKeystrokes and _keystrokesFile \
       and (event_string != "Pause"):
        _keystrokesFile.write(string + "\n")
    debug.printInputEvent(debug.LEVEL_FINE, string)

    if event.type == atspi.Accessibility.KEY_PRESSED_EVENT:
        # Key presses always interrupt speech.
        #
        speech.stop()

        # The control characters come through as control characters,
        # so we just turn them into their ASCII equivalent.  NOTE that
        # the upper case ASCII characters will be used (e.g., ctrl+a
        # will be turned into the string "A").  All these checks here
        # are to just do some sanity checking before doing the
        # conversion. [[[WDW - this is making assumptions about
        # mapping ASCII control characters to to UTF-8.]]]
        #
        if (event.modifiers & (1 << atspi.Accessibility.MODIFIER_CONTROL)) \
           and (not event.is_text) and (len(event.event_string) == 1):
            value = ord(event.event_string[0])
            if value < 32:
                event_string = chr(value + 0x40)

        _keyEcho(event_string)

        # We treat the Insert key as a modifier - so just swallow it and
        # set our internal state.
        #
        if event_string == "Insert":
            _insertPressed = True
            return True

    elif event.type == atspi.Accessibility.KEY_RELEASED_EVENT \
         and (event_string == "Insert"):
        _insertPressed = False
        return True

    # Orca gets first stab at the event.  Then, the presenter gets
    # a shot. [[[TODO: WDW - might want to let the presenter try first?
    # The main reason this is staying as is is that we may not want
    # scripts to override fundamental Orca key bindings.]]]
    #
    keyboardEvent = KeyboardEvent(event)
    if _insertPressed:
        keyboardEvent.modifiers |= (1 << MODIFIER_ORCA)

    consumed = False
    try:
        consumed = _keybindings.consumeKeyboardEvent(None, keyboardEvent)
        if (not consumed) and (_currentPresentationManager >= 0):
            consumed = _PRESENTATION_MANAGERS[_currentPresentationManager].\
                       processKeyboardEvent(keyboardEvent)
        if (not consumed) and settings.getSetting(settings.LEARN_MODE_ENABLED,
                                                  False):
            if event.type == atspi.Accessibility.KEY_PRESSED_EVENT:
                braille.displayMessage(event_string)
                speech.speak(event_string)
            elif (event.type == atspi.Accessibility.KEY_RELEASED_EVENT) \
                 and (event_string == "Escape"):
                exitLearnMode(None, keyboardEvent)
            consumed = True
    except:
        debug.printException(debug.LEVEL_SEVERE)

    lastInputEvent = keyboardEvent

    return consumed

########################################################################
#                                                                      #
# METHODS FOR PRE-PROCESSING AND MASSAGING BRAILLE EVENTS.             #
#                                                                      #
########################################################################

def _processBrailleEvent(command):
    """Called whenever a  key is pressed on the Braille display.

    Arguments:
    - command: the BrlAPI command for the key that was pressed.

    Returns True if the event was consumed; otherwise False
    """

    global lastInputEvent

    # [[[TODO: WDW - probably should add braille bindings to this module.]]]

    consumed = False

    # Braille key presses always interrupt speech.
    #
    speech.stop()

    event = BrailleEvent(command)
    lastInputEvent = event

    try:
        consumed = _PRESENTATION_MANAGERS[_currentPresentationManager].\
                   processBrailleEvent(event)
    except:
        debug.printException(debug.LEVEL_SEVERE)

    if (not consumed) and settings.getSetting(settings.LEARN_MODE_ENABLED,
                                              False):
        consumed = True

    return consumed

########################################################################
#                                                                      #
# METHODS FOR DRAWING RECTANGLES AROUND OBJECTS ON THE SCREEN          #
#                                                                      #
########################################################################

_display = None
_visibleRectangle = None

def drawOutline(x, y, width, height, erasePrevious=True):
    """Draws a rectangular outline around the accessible, erasing the
    last drawn rectangle in the process."""

    global _display
    global _visibleRectangle

    if not _display:
        try:
            _display = gtk.gdk.display_get_default()
        except:
            debug.printException(debug.LEVEL_FINEST)
            _display = gtk.gdk.display(":0")

        if not _display:
            debug.println(debug.LEVEL_SEVERE,
                          "orca.drawOutline could not open display.")
            return

    screen = _display.get_default_screen()
    root_window = screen.get_root_window()
    graphics_context = root_window.new_gc()
    graphics_context.set_subwindow(gtk.gdk.INCLUDE_INFERIORS)
    graphics_context.set_function(gtk.gdk.INVERT)
    graphics_context.set_line_attributes(3,                  # width
                                         gtk.gdk.LINE_SOLID, # style
                                         gtk.gdk.CAP_BUTT,   # end style
                                         gtk.gdk.JOIN_MITER) # join style

    # Erase the old rectangle.
    #
    if _visibleRectangle and erasePrevious:
        drawOutline(_visibleRectangle[0], _visibleRectangle[1],
                    _visibleRectangle[2], _visibleRectangle[3], False)
        _visibleRectangle = None

    # We'll use an invalid x value to indicate nothing should be
    # drawn.
    #
    if x < 0:
        _visibleRectangle = None
        return

    # The +1 and -2 stuff here is an attempt to stay within the
    # bounding box of the object.
    #
    root_window.draw_rectangle(graphics_context,
                               False, # Fill
                               x + 1,
                               y + 1,
                               max(1, width - 2),
                               max(1, height - 2))

    _visibleRectangle = [x, y, width, height]

def outlineAccessible(accessible, erasePrevious=True):
    """Draws a rectangular outline around the accessible, erasing the
    last drawn rectangle in the process."""

    if accessible:
        component = accessible.component
        if component:
            visibleRectangle = component.getExtents(0) # coord type = screen
            drawOutline(visibleRectangle.x, visibleRectangle.y,
                        visibleRectangle.width, visibleRectangle.height,
                        erasePrevious)
    else:
        drawOutline(-1, 0, 0, 0, erasePrevious)

########################################################################
#                                                                      #
# METHODS FOR HANDLING INITIALIZATION, SHUTDOWN, AND USE.              #
#                                                                      #
########################################################################

# If True, this module has been initialized.
#
_initialized = False

def init(registry):
    """Initialize the orca module, which initializes speech, braille,
    and mag modules.  Also builds up the application list, registers
    for AT-SPI events, and creates scripts for all known applications.

    Returns True if the initialization procedure has run, or False if this
    module has already been initialized.
    """

    global _initialized
    global _keybindings

    if _initialized:
        return False

    registry.registerKeystrokeListeners(_processKeyboardEvent)

    _keybindings = keybindings.KeyBindings()

    enterLearnModeHandler = InputEventHandler(\
        enterLearnMode,
        _("Enters learn mode.  Press escape to exit learn mode."))
    _keybindings.add(keybindings.KeyBinding("F1", \
                                            1 << MODIFIER_ORCA, \
                                            1 << MODIFIER_ORCA, \
                                            enterLearnModeHandler))

    decreaseSpeechRateHandler = InputEventHandler(\
        speech.decreaseSpeechRate,
        _("Decreases the speech rate."))
    _keybindings.add(keybindings.KeyBinding("Left", \
                                            1 << MODIFIER_ORCA, \
                                            1 << MODIFIER_ORCA,
                                            decreaseSpeechRateHandler))

    increaseSpeechRateHandler = InputEventHandler(\
        speech.increaseSpeechRate,
        _("Increases the speech rate."))
    _keybindings.add(keybindings.KeyBinding("Right", \
                                            1 << MODIFIER_ORCA, \
                                            1 << MODIFIER_ORCA,
                                            increaseSpeechRateHandler))

    shutdownHandler = InputEventHandler(shutdown, _("Quits Orca"))
    _keybindings.add(keybindings.KeyBinding("F12", \
                                            0, \
                                            0,
                                            shutdownHandler))
    _keybindings.add(keybindings.KeyBinding("SunF37", \
                                            0, \
                                            0,
                                            shutdownHandler))

    keystrokeRecordingHandler = InputEventHandler(\
        toggleKeystrokeRecording,
        _("Toggles keystroke recording on and off."))
    _keybindings.add(keybindings.KeyBinding("Pause", \
                                            0, \
                                            0,
                                            keystrokeRecordingHandler))

    listAppsHandler = InputEventHandler(
        printApps,
        _("Prints a debug listing of all known applications to the console where Orca is running."))
    _keybindings.add(keybindings.KeyBinding(
        "F5", 
        (1 << MODIFIER_ORCA | 1 << atspi.Accessibility.MODIFIER_CONTROL), 
        1 << MODIFIER_ORCA,
        listAppsHandler))

    cycleDebugLevelHandler = InputEventHandler(
        cycleDebugLevel,
        _("Cycles the debug level at run time."))
    _keybindings.add(keybindings.KeyBinding(
        "F5", 
        (1 << MODIFIER_ORCA | 1 << atspi.Accessibility.MODIFIER_CONTROL), 
        (1 << MODIFIER_ORCA | 1 << atspi.Accessibility.MODIFIER_CONTROL), 
        cycleDebugLevelHandler))

    printActiveAppHandler = InputEventHandler(\
        printActiveApp,
        _("Prints debug information about the currently active application to the console where Orca is running."))
    _keybindings.add(keybindings.KeyBinding("F6", \
                                            1 << MODIFIER_ORCA, \
                                            1 << MODIFIER_ORCA,
                                            printActiveAppHandler))

    printAncestryHandler = InputEventHandler(\
        printAncestry,
        _("Prints debug information about the ancestry of the object with focus"))
    _keybindings.add(keybindings.KeyBinding(
        "F7",
        (1 << MODIFIER_ORCA | 1 << atspi.Accessibility.MODIFIER_CONTROL), 
        1 << MODIFIER_ORCA,
        printAncestryHandler))

    printHierarchyHandler = InputEventHandler(\
        printHierarchy,
        _("Prints debug information about the application with focus"))
    
    _keybindings.add(keybindings.KeyBinding(
        "F7",
        (1 << MODIFIER_ORCA | 1 << atspi.Accessibility.MODIFIER_CONTROL), 
        (1 << MODIFIER_ORCA | 1 << atspi.Accessibility.MODIFIER_CONTROL), 
        printHierarchyHandler))

    nextPresentationManagerHandler = InputEventHandler(\
        _switchToNextPresentationManager,
        _("Switches to the next presentation manager."))
    _keybindings.add(keybindings.KeyBinding("F8", \
                                            1 << MODIFIER_ORCA, \
                                            1 << MODIFIER_ORCA,
                                            nextPresentationManagerHandler))

    if settings.getSetting(settings.USE_SPEECH, True):
        try:
            speech.init()
            debug.println(debug.LEVEL_CONFIGURATION,
                          "Speech module has been initialized.")
        except:
            debug.println(debug.LEVEL_SEVERE,
                          "Could not initialize connection to speech.")
    else:
        debug.println(debug.LEVEL_CONFIGURATION,
                      "Speech module has NOT been initialized.")

    if settings.getSetting(settings.USE_BRAILLE, False):
        try:
            braille.init(_processBrailleEvent, 7)
        except:
            debug.println(debug.LEVEL_SEVERE,
                          "Could not initialize connection to braille.")

    if settings.getSetting(settings.USE_MAGNIFIER, False):
        try:
            mag.init()
            debug.println(debug.LEVEL_CONFIGURATION,
                          "Magnification module has been initialized.")
        except:
            debug.println(debug.LEVEL_SEVERE,
                          "Could not initialize connection to magnifier.")
    else:
        debug.println(debug.LEVEL_CONFIGURATION,
                      "Magnification module has NOT been initialized.")

    # Build list of accessible apps.
    #
    _buildAppList(registry)

    # Create and load an app's script when it is added to the desktop
    #
    registry.registerEventListener(_onChildrenChanged,
				   "object:children-changed:")

    _initialized = True
    return True

def start(registry):
    """Starts Orca.
    """

    global _PRESENTATION_MANAGERS
    
    if not _initialized:
        init(registry)

    try:
        speech.speak(_("Welcome to Orca."))
        braille.displayMessage(_("Welcome to Orca."))
    except:
        debug.printException(debug.LEVEL_SEVERE)

    if not _PRESENTATION_MANAGERS:
        import focus_tracking_presenter
        import hierarchical_presenter
        _PRESENTATION_MANAGERS = \
            [focus_tracking_presenter.FocusTrackingPresenter(),
             hierarchical_presenter.HierarchicalPresenter()]
    
    _switchToPresentationManager(0) # focus_tracking_presenter

    registry.start()

def shutdown(script=None, inputEvent=None):
    """Exits Orca.  Unregisters any event listeners and cleans up.  Also
    quits the bonobo main loop and resets the initialized state to False.

    Returns True if the shutdown procedure ran or False if this module
    was never initialized.
    """

    global _initialized

    if not _initialized:
        return False

    speech.speak(_("goodbye."))
    braille.displayMessage(_("Goodbye."))

    # Deregister our event listeners
    #
    registry = atspi.Registry()
    registry.deregisterEventListener(_onChildrenChanged,
            	                     "object:children-changed:")

    if _currentPresentationManager >= 0:
        _PRESENTATION_MANAGERS[_currentPresentationManager].deactivate()

    # Shutdown all the other support.
    #
    if settings.getSetting(settings.USE_SPEECH, True):
        speech.shutdown()
    if settings.getSetting(settings.USE_BRAILLE, False):
        braille.shutdown();
    if settings.getSetting(settings.USE_MAGNIFIER, False):
        mag.shutdown();

    registry.stop()

    _initialized = False
    return True

def shutdownAndExit(signum, frame):
    print "Goodbye."
    try:
	shutdown()
    except:
        pass
    sys.exit()

def main():
    userprefs = os.path.join (os.environ["HOME"], ".orca")
    sys.path.insert (0, userprefs)
    signal.signal(signal.SIGINT, shutdownAndExit)
    signal.signal(signal.SIGQUIT, shutdownAndExit)
    registry = atspi.Registry()
    init(registry)
    start(registry)

if __name__ == "__main__":
    main()
