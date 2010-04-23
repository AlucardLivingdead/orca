# Orca
#
# Copyright 2006-2009 Sun Microsystems Inc.
# Copyright 2010 Joanmarie Diggs
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
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc., "  \
                "Copyright (c) 2010 Joanmarie Diggs"
__license__   = "LGPL"

import pyatspi

import orca.default as default
import orca.input_event as input_event
import orca.orca as orca
import orca.orca_state as orca_state

from speech_generator import SpeechGenerator
from formatting import Formatting

########################################################################
#                                                                      #
# The Java script class.                                               #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for Java applications.

        Arguments:
        - app: the application to create a script for.
        """
        default.Script.__init__(self, app)

        # Some objects which issue descendant changed events lack
        # STATE_MANAGES_DESCENDANTS. As a result, onSelectionChanged
        # doesn't ignore these objects. That in turn causes Orca to
        # double-speak some items and/or set the locusOfFocus to a
        # parent it shouldn't. See bgo#616582. [[[TODO - JD: remove
        # this hack if and when we get a fix for that bug]]]
        # 
        self._lastDescendantChangedSource = None

    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """
        return SpeechGenerator(self)

    def getFormatting(self):
        """Returns the formatting strings for this script."""
        return Formatting(self)

    def checkKeyboardEventData(self, keyboardEvent):
        """Checks the data on the keyboard event.

        Some toolkits don't fill all the key event fields, and/or fills
        them out with unexpected data. This method tries to fill in the
        missing fields and validate/standardize the data we've been given.
        While any script can override this method, it is expected that
        this will only be done at the toolkit script level.

        Arguments:
        - keyboardEvent: an instance of input_event.KeyboardEvent
        """

        default.Script.checkKeyboardEventData(self, keyboardEvent)

        if not keyboardEvent.keyval_name:
            return

        import gtk.gdk as gdk

        # Standardize the hw_code from a Java-unique one to a gdk one.
        #
        keymap = gdk.keymap_get_default()
        keyval = gdk.keyval_from_name(keyboardEvent.keyval_name)
        entries = keymap.get_entries_for_keyval(keyval)
        for entry in entries:
            if entry[1] == 0:  # group = 0
                keyboardEvent.hw_code = entry[0]
                break

        # Put the event_string back to what it was prior to the Java
        # Atk Wrapper hack which gives us the keyname and not the
        # expected and needed printable character for punctuation
        # marks.
        #
        if keyboardEvent.event_string == keyboardEvent.keyval_name \
           and len(keyboardEvent.event_string) > 1:
            keyval = gdk.keyval_from_name(keyboardEvent.keyval_name)
            if 0 < keyval < 256:
                keyboardEvent.event_string = unichr(keyval).encode("UTF-8")

    def getNodeLevel(self, obj):
        """Determines the node level of this object if it is in a tree
        relation, with 0 being the top level node.  If this object is
        not in a tree relation, then -1 will be returned.

        Arguments:
        -obj: the Accessible object
        """

        if not obj:
            return -1

        if not self._lastDescendantChangedSource:
            return default.Script.getNodeLevel(self, obj)

        # It would seem that Java is making multiple copies of accessibles
        # and/or killing them frequently. This is messing up our ability to
        # ascend the hierarchy. We need to see if we can find our clone and
        # set obj to it before trying to get the node level.
        #
        items = self.findByRole(
            self._lastDescendantChangedSource, obj.getRole())
        for item in items:
            if item.name == obj.name and self.isSameObject(item, obj):
                obj = item
                break
        else:
            return default.Script.getNodeLevel(self, obj)

        count = 0
        while obj:
            state = obj.getState()
            if state.contains(pyatspi.STATE_EXPANDABLE) \
               or state.contains(pyatspi.STATE_COLLAPSED):
                if state.contains(pyatspi.STATE_VISIBLE):
                    count += 1
                obj = obj.parent
            else:
                break

        return count - 1

    def isSameObject(self, obj1, obj2):
        """Compares two objects to determine if they are functionally
        the same object. This is needed because some applications and
        toolkits kill and replace accessibles."""

        if (obj1 == obj2):
            return True
        elif (not obj1) or (not obj2):
            return False

        if obj1.getIndexInParent() != obj2.getIndexInParent() \
           or obj1.childCount != obj2.childCount:
            return False

        return default.Script.isSameObject(self, obj1, obj2)

    def onFocus(self, event):
        """Called whenever an object gets focus.

        Arguments:
        - event: the Event
        """

        role = event.source.getRole()

        if role == pyatspi.ROLE_MENU:
            # Override default.py's onFocus decision to ignore focus
            # events on MENU items with selected children.  This is
            # because JMenu's pop up without their children selected,
            # but for some reason they always have
            # selection.nSelectedChildren > 0.  I suspect this is a
            # bug in JMenu.java:getAccessibleSelectionCount, but the
            # details of Swing's MenuSelectionManager are foreign to
            # me.  So, for now, we'll just be happy knowing that
            # Java's menu items will give us focus events when they
            # are selected.
            #
            orca.setLocusOfFocus(event, event.source)
            return

        default.Script.onFocus(self, event)

    def onActiveDescendantChanged(self, event):
        """Called when an object who manages its own descendants detects a
        change in one of its children.

        Arguments:
        - event: the Event
        """

        self._lastDescendantChangedSource = event.source

        # In Java comboboxes, when the list of options is popped up via
        # an up or down action, control (but not focus) goes to a LIST
        # object that manages the descendants.  So, we detect that here
        # and keep focus on the combobox.
        #
        if event.source.getRole() == pyatspi.ROLE_COMBO_BOX:
            orca.visualAppearanceChanged(event, event.source)
            return

        if event.source.getRole() == pyatspi.ROLE_LIST:
            combobox = self.getAncestor(event.source,
                                        [pyatspi.ROLE_COMBO_BOX],
                                        [pyatspi.ROLE_PANEL])
            if combobox:
                orca.visualAppearanceChanged(event, combobox)
                return

        default.Script.onActiveDescendantChanged(self, event)

    def onCaretMoved(self, event):
        # Java's SpinButtons are the most caret movement happy thing
        # I've seen to date.  If you Up or Down on the keyboard to
        # change the value, they typically emit three caret movement
        # events, first to the beginning, then to the end, and then
        # back to the beginning.  It's a very excitable little widget.
        # Luckily, it only issues one value changed event.  So, we'll
        # ignore caret movement events caused by value changes and
        # just process the single value changed event.
        #
        isSpinBox = self.isDesiredFocusedItem(event.source,
                                              [pyatspi.ROLE_TEXT,
                                               pyatspi.ROLE_PANEL,
                                               pyatspi.ROLE_SPIN_BUTTON])
        if isSpinBox:
            if isinstance(orca_state.lastInputEvent,
                          input_event.KeyboardEvent):
                eventStr = orca_state.lastNonModifierKeyEvent.event_string
            else:
                eventStr = None
            if (eventStr in ["Up", "Down"]) \
               or isinstance(orca_state.lastInputEvent,
                             input_event.MouseButtonEvent):
                return

        default.Script.onCaretMoved(self, event)

    def onSelectionChanged(self, event):
        """Called when an object's selection changes.

        Arguments:
        - event: the Event
        """

        # Avoid doing this with objects that manage their descendants
        # because they'll issue a descendant changed event. (Note: This
        # equality check is intentional; isSameObject() is especially
        # thorough with trees and tables, which is not performant.
        #
        if event.source == self._lastDescendantChangedSource:
            return

        # We treat selected children as the locus of focus. When the
        # selection changes in a list we want to update the locus of
        # focus. If there is no selection, we default the locus of
        # focus to the containing object.
        #
        if (event.source.getRole() in [pyatspi.ROLE_LIST,
                                       pyatspi.ROLE_PAGE_TAB_LIST,
                                       pyatspi.ROLE_TREE]) \
            and event.source.getState().contains(pyatspi.STATE_FOCUSED):
            newFocus = event.source
            if event.source.childCount:
                selection = event.source.querySelection()
                if selection.nSelectedChildren > 0:
                    newFocus = selection.getSelectedChild(0)
            orca.setLocusOfFocus(event, newFocus)
        else:
            default.Script.onSelectionChanged(self, event)

    def onStateChanged(self, event):
        """Called whenever an object's state changes.

        Arguments:
        - event: the Event
        """

        # Handle state changes when JTree labels become expanded
        # or collapsed.
        #
        if (event.source.getRole() == pyatspi.ROLE_LABEL) and \
            event.type.startswith("object:state-changed:expanded"):
            orca.visualAppearanceChanged(event, event.source)
            return

        # This is a workaround for a java-access-bridge bug (Bug 355011)
        # where popup menu events are not sent to Orca.
        #
        # When a root pane gets focus, a popup menu may have been invoked.
        # If there is a popup menu, give locus of focus to the armed menu
        # item.
        #
        if event.source.getRole() == pyatspi.ROLE_ROOT_PANE and \
               event.type.startswith("object:state-changed:focused") and \
               event.detail1 == 1:

            for child in event.source:
                # search the layered pane for a popup menu
                if child.getRole() == pyatspi.ROLE_LAYERED_PANE:
                    popup = self.findByRole(child,
                                            pyatspi.ROLE_POPUP_MENU, False)
                    if len(popup) > 0:
                        # set the locus of focus to the armed menu item
                        items = self.findByRole(popup[0],
                                                pyatspi.ROLE_MENU_ITEM, False)
                        for item in items:
                            if item.getState().contains(pyatspi.STATE_ARMED):
                                orca.setLocusOfFocus(event, item)
                                return

        # Present a value change in case of an focused popup menu.
        # Fix for Swing file chooser.
        #
        if event.type.startswith("object:state-changed:visible") and \
                event.source.getRole() == pyatspi.ROLE_POPUP_MENU and \
                event.source.parent.getState().contains(pyatspi.STATE_FOCUSED):
            orca.setLocusOfFocus(event, event.source.parent)
            return

        default.Script.onStateChanged(self, event)

    def onValueChanged(self, event):
        """Called whenever an object's value changes.

        Arguments:
        - event: the Event
        """

        # We'll ignore value changed events for Java's toggle buttons since
        # they also send a redundant object:state-changed:checked event.
        #
        if event.source.getRole() == pyatspi.ROLE_TOGGLE_BUTTON:
            return

        # Java's SpinButtons are the most caret movement happy thing
        # I've seen to date.  If you Up or Down on the keyboard to
        # change the value, they typically emit three caret movement
        # events, first to the beginning, then to the end, and then
        # back to the beginning.  It's a very excitable little widget.
        # Luckily, it only issues one value changed event.  So, we'll
        # ignore caret movement events caused by value changes and
        # just process the single value changed event.
        #
        if event.source.getRole() == pyatspi.ROLE_SPIN_BUTTON:
            try:
                thisBox = orca_state.locusOfFocus.parent.parent == event.source
            except:
                thisBox = False
            if thisBox:
                self._presentTextAtNewCaretPosition(event,
                                                    orca_state.locusOfFocus)
                return

        default.Script.onValueChanged(self, event)
