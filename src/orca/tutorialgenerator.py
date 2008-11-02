# Orca
#
# Copyright 2008 Sun Microsystems Inc.
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

"""Utilities for obtaining tutorial utterances for objects.  In general,
there probably should be a singleton instance of the TutorialGenerator
class.  For those wishing to override the generators, however,
one can create a new instance and replace/extend the tutorial generators
as they see fit."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi
import debug
import settings

from orca_i18n import _         # for gettext support

class TutorialGenerator:
    """Takes accessible objects and produces a tutorial string to speak 
    for those objects.  See the getTutorialString method, which is the 
    primary entry point.  Subclasses can feel free to override/extend 
    the getTutorialGenerators instance field as they see fit."""

    def __init__(self, script):

        # The script that created us.  This allows us to ask the
        # script for information if we need it.
        #
        self._script = script
        # storing the last spoken message.
        self.lastTutorial = ""

        # Set up a dictionary that maps role names to functions
        # that generate tutorial strings for objects that implement that role.
        #
        self.tutorialGenerators = {}
        self.tutorialGenerators[pyatspi.ROLE_CHECK_BOX] = \
            self._getTutorialForCheckBox
        self.tutorialGenerators[pyatspi.ROLE_COMBO_BOX] = \
            self._getTutorialForComboBox
        self.tutorialGenerators[pyatspi.ROLE_FRAME] = \
            self._getTutorialForFrame
        self.tutorialGenerators[pyatspi.ROLE_LIST] = \
            self._getTutorialForList
        self.tutorialGenerators[pyatspi.ROLE_LIST_ITEM] = \
            self._getTutorialForListItem
        self.tutorialGenerators[pyatspi.ROLE_PAGE_TAB] = \
            self._getTutorialForPageTab
        self.tutorialGenerators[pyatspi.ROLE_PARAGRAPH] = \
            self._getTutorialForText
        self.tutorialGenerators[pyatspi.ROLE_PASSWORD_TEXT] = \
            self._getTutorialForText
        self.tutorialGenerators[pyatspi.ROLE_ENTRY] = \
            self._getTutorialForText
        self.tutorialGenerators[pyatspi.ROLE_PUSH_BUTTON] = \
            self._getTutorialForPushButton
        self.tutorialGenerators[pyatspi.ROLE_SPIN_BUTTON] = \
            self._getTutorialForSpinButton
        self.tutorialGenerators[pyatspi.ROLE_TABLE_CELL] = \
            self._getTutorialForTableCellRow
        self.tutorialGenerators[pyatspi.ROLE_TEXT] = \
            self._getTutorialForText
        self.tutorialGenerators[pyatspi.ROLE_TOGGLE_BUTTON] = \
            self._getTutorialForCheckBox
        self.tutorialGenerators[pyatspi.ROLE_RADIO_BUTTON] = \
            self._getTutorialForRadioButton
        self.tutorialGenerators[pyatspi.ROLE_MENU]                = \
            self._getTutorialForMenu
        self.tutorialGenerators[pyatspi.ROLE_CHECK_MENU_ITEM]     = \
            self._getTutorialForCheckBox
        self.tutorialGenerators[pyatspi.ROLE_MENU_ITEM]           = \
            self._getTutorialForPushButton
        self.tutorialGenerators[pyatspi.ROLE_RADIO_MENU_ITEM]     = \
            self._getTutorialForCheckBox        
        self.tutorialGenerators[pyatspi.ROLE_SLIDER]              = \
            self._getTutorialForSlider

    def _debugGenerator(self, generatorName, obj, already_focused, utterances):
        """Prints debug.LEVEL_FINER information regarding 
        the tutorial generator.

        Arguments:
        - generatorName: the name of the generator
        - obj: the object being presented
        - already_focused: False if object just received focus
        - utterances: the generated text
        """

        debug.println(debug.LEVEL_FINER,
                      "GENERATOR: %s" % generatorName)
        debug.println(debug.LEVEL_FINER,
                      "           obj             = %s" % obj.name)
        debug.println(debug.LEVEL_FINER,
                      "           role            = %s" % obj.getRoleName())
        debug.println(debug.LEVEL_FINER,
                      "           already_focused = %s" % already_focused)
        debug.println(debug.LEVEL_FINER,
                      "           utterances:")
        for text in utterances:
            debug.println(debug.LEVEL_FINER,
                    "               (%s)" % text)

    def _getDefaultTutorial(self, obj, already_focused, forceMessage, \
      role=None):
        """The default tutorial generator returns the empty tutorial string
        because We have no associated tutorial function for the object.
        
        Arguments:
        - obj: an Accessible
        - already_focused: False if object just received focus
        - forceMessage: used for when whereAmI really needs the tutorial string.
        - role: A role that should be used instead of the Accessible's 
          possible role.

        Returns the empty list []
        """

        return []


    def _getTutorialForCheckBox(self, obj, already_focused, forceMessage):
        """Get the  tutorial string for a check box.

        Arguments:
        - obj: the check box
        - already_focused: False if object just received focus
        - forceMessage: used for when whereAmI really needs the tutorial string.

        Returns a list of tutorial utterances to be spoken for the object.
        """

        utterances = []
        # Translators: this is a tip for the user on how to toggle a checkbox.
        msg = _("Press space to toggle.")

        if (not already_focused and self.lastTutorial != [msg]) or forceMessage:
            utterances.append(msg)

        self._debugGenerator("_getTutorialForCheckBox",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getTutorialForComboBox(self, obj, already_focused, forceMessage):
        """Get the  tutorial string for a combobox.

        Arguments:
        - obj: the combo box
        - already_focused: False if object just received focus
        - forceMessage: used for when whereAmI really needs the tutorial string.

        Returns a list of tutorial utterances to be spoken for the object.
        """

        utterances = []
        # Translators: this is a tip for the user on how to interact 
        # with a combobox.
        msg = _("Press space to expand, and use up and down to select an item.")

        if (not already_focused and self.lastTutorial != [msg]) or forceMessage:
            utterances.append(msg)

        self._debugGenerator("_getTutorialForComboBox",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getTutorialForFrame(self, obj, already_focused, forceMessage):
        """Get the  tutorial string for a frame.

        Arguments:
        - obj: the frame
        - already_focused: False if object just received focus
        - forceMessage: used for when whereAmI really needs the tutorial string.

        Returns a list of tutorial utterances to be spoken for the object.
        """

        utterances = []
        name = self._script.getDisplayedText(obj)
        if not name and obj.description:
            name = obj.description

        # Translators: this is the tutorial string for when first landing 
        # on the desktop, giving tips on how to navigate.
        # Also describing how to access the menues.
        desktopMsg = _("To move to items, use either " \
                     "the arrow keys, or type ahead searching. " \
                     "To get to the system menues press the alt+f1 key.")
        
        # Translators: If this application has more than one unfocused alert or
        # dialog window, inform user of how to refocus these.
        childWindowsMsg = _("Press alt+f6 to give focus to child windows.")

        scriptName = self._script.name
        sibling = obj.parent.getChildAtIndex(0)
        if 'nautilus' in scriptName and obj == sibling:
            utterances.append(desktopMsg)

        # If this application has more than one unfocused alert or
        # dialog window, tell user how to give them focus.
        alertAndDialogCount = \
                    self._script.getUnfocusedAlertAndDialogCount(obj)
        if alertAndDialogCount > 0:
            utterances.append(childWindowsMsg)

        self._debugGenerator("_getTutorialForFrame",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getTutorialForList(self, obj, already_focused, forceMessage):
        """Get the  tutorial string for a list.

        Arguments:
        - obj: the list
        - already_focused: False if object just received focus
        - forceMessage: used for when whereAmI really needs the tutorial string.

        Returns a list of tutorial utterances to be spoken for the object.
        """

        utterances = []
        
        # Translators: this is the tutorial string when navigating lists.
        msg = _("Use up and down to select an item.")
        
        if (not already_focused and self.lastTutorial != [msg]) or forceMessage:
            utterances.append(msg)

        self._debugGenerator("_getTutorialForList",
                             obj,
                             already_focused,
                             utterances)

        return utterances
    
    def _getTutorialForListItem(self, obj, already_focused, forceMessage):
        """Get the  tutorial string for a listItem.

        Arguments:
        - obj: the listitem
        - already_focused: False if object just received focus
        - forceMessage: used for when whereAmI really needs the tutorial string.

        Returns a list of tutorial utterances to be spoken for the object.
        """

        utterances = []

        # Translators: this represents the state of a node in a tree.
	# 'expanded' means the children are showing.
        # 'collapsed' means the children are not showing.
        # this string informs the user how to collapse the node.
        expandedMsg = _("To collapse, press shift plus left.")
        
        # Translators: this represents the state of a node in a tree.
        # 'expanded' means the children are showing.
        # 'collapsed' means the children are not showing.
        # this string informs the user how to expand the node.
        collapsedMsg = _("To expand, press shift plus right.")
        
        
        # If already in focus then the tree probably collapsed or expanded
        state = obj.getState()
        if state.contains(pyatspi.STATE_EXPANDABLE):
            if state.contains(pyatspi.STATE_EXPANDED):
                if (self.lastTutorial != [expandedMsg]) or forceMessage:
                    utterances.append(expandedMsg)
            else:
                if (self.lastTutorial != [collapsedMsg]) or forceMessage:
                    utterances.append(collapsedMsg)
                
        self._debugGenerator("_getTutorialForListItem",
                             obj,
                             already_focused,
                             utterances)
        return utterances

    def _getTutorialForText(self, obj, already_focused, forceMessage):
        """Get the tutorial string for a text object.

        Arguments:
        - obj: the text component
        - already_focused: False if object just received focus
        - forceMessage: used for when whereAmI really needs the tutorial string.

        Returns a list of tutorial utterances to be spoken for the object.
        """
        utterances = []
        # Translators: This is the tutorial string for when landing 
        # on text fields.
        msg = _("Type in text.")

        if (not already_focused or forceMessage) and \
           not self._script.isReadOnlyTextArea(obj):
            utterances.append(msg)

        self._debugGenerator("_getTutorialForText",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getTutorialForPageTab(self, obj, already_focused, forceMessage):
        """Get the tutorial string for a page tab.

        Arguments:
        - obj: the page tab
        - already_focused: False if object just received focus
        - forceMessage: used for when whereAmI really needs the tutorial string.

        Returns a list of tutorial utterances to be spoken for the object.
        """

        utterances = []
        # Translators: this is the tutorial string for landing 
        # on a page tab, we are informing the 
        # user how to navigate these.
        msg = _("Use left and right to view other tabs.")
        
        if (self.lastTutorial != [msg]) or forceMessage:
            utterances.append(msg)

        self._debugGenerator("_getTutorialForPageTabList",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getTutorialForPushButton(self, obj, already_focused, forceMessage):
        """Get the tutorial string for a push button

        Arguments:
        - obj: the push button
        - already_focused: False if object just received focus
        - forceMessage: used for when whereAmI really needs the tutorial string.

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []
        # Translators: this is the tutorial string for activating a push button.
        msg = _("To activate press space.")
        
        if (not already_focused and self.lastTutorial != [msg]) or forceMessage:
            utterances.append(msg)

        self._debugGenerator("_getTutorialForPushButton",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getTutorialForSpinButton(self, obj, already_focused, forceMessage):
        """Get the tutorial string for a spin button.  If the object already has
        focus, then no tutorial is given.

        Arguments:
        - obj: the spin button
        - already_focused: False if object just received focus
        - forceMessage: used for when whereAmI really needs the tutorial string.

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []
        # Translators: this is the tutorial string for when landing 
        # on a spin button.
        msg = _("Use up or down arrow to select value." \
              " Or type in the desired numerical value.")

        if (not already_focused and self.lastTutorial != [msg]) or forceMessage:
            utterances.append(msg)

        self._debugGenerator("_getTutorialForSpinButton",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getTutorialForTableCell(self, obj, already_focused, forceMessage):
        """Get the tutorial utterances for a single table cell

        Arguments:
        - obj: the table
        - already_focused: False if object just received focus
        - forceMessage: used for when whereAmI really needs the tutorial string.

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []

        # Translators: this represents the state of a node in a tree.
	# 'expanded' means the children are showing.
        # 'collapsed' means the children are not showing.
        # this string informs the user how to collapse the node.
        expandedMsg = _("To collapse, press shift plus left.")
        
        # Translators: this represents the state of a node in a tree.
        # 'expanded' means the children are showing.
        # 'collapsed' means the children are not showing.
        # this string informs the user how to expand the node.
        collapsedMsg = _("To expand, press shift plus right.")

        # If this table cell has 2 children and one of them has a 
        # 'toggle' action and the other does not, then present this 
        # as a checkbox where:
        # 1) we get the checked state from the cell with the 'toggle' action
        # 2) we get the label from the other cell.
        # See Orca bug #376015 for more details.
        #
        if obj.childCount == 2:
            cellOrder = []
            hasToggle = [ False, False ]
            for i, child in enumerate(obj):
                try:
                    action = child.queryAction()
                except NotImplementedError:
                    continue
                else:
                    for j in range(0, action.nActions):
                        # Translators: this is the action name for
                        # the 'toggle' action. It must be the same
                        # string used in the *.po file for gail.
                        #
                        if action.getName(j) in ["toggle", _("toggle")]:
                            hasToggle[i] = True
                            break

            if hasToggle[0] and not hasToggle[1]:
                cellOrder = [ 1, 0 ] 
            elif not hasToggle[0] and hasToggle[1]:
                cellOrder = [ 0, 1 ]
            if cellOrder:
                for i in cellOrder:
                    # Don't speak the label if just the checkbox state has
                    # changed.
                    #
                    if already_focused and not hasToggle[i]:
                        pass
                    else:
                        utterances.extend( \
                            self._getTutorialForTableCell(obj[i],
                            already_focused, forceMessage))
                return utterances

        # [[[TODO: WDW - Attempt to infer the cell type.  There's a
        # bunch of stuff we can do here, such as check the EXPANDABLE
        # state, check the NODE_CHILD_OF relation, etc.  Logged as
        # bugzilla bug 319750.]]]
        #
        try:
            action = obj.queryAction()
        except NotImplementedError:
            action = None
        if action:
            for i in range(0, action.nActions):
                debug.println(debug.LEVEL_FINEST,
                    "tutorialgenerator._getTutorialForTableCell" \
                    + "looking at action %d" % i)

                # Translators: this is the action name for
                # the 'toggle' action. It must be the same
                # string used in the *.po file for gail.
                #
                if action.getName(i) in ["toggle", _("toggle")]:
                    utterances = self._getTutorialForCheckBox(obj,
                                  already_focused, forceMessage)
                    break

        state = obj.getState()
        if state.contains(pyatspi.STATE_EXPANDABLE):
            if state.contains(pyatspi.STATE_EXPANDED):
                if self.lastTutorial != [expandedMsg] or forceMessage:
                    utterances.append(expandedMsg)
            else:
                if self.lastTutorial != [collapsedMsg] or forceMessage:
                    utterances.append(collapsedMsg)

        self._debugGenerator("_getTutorialForTableCell",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getTutorialForTableCellRow(self, obj, already_focused, forceMessage):
        """Get the tutorial string for the active table cell in the table row.

        Arguments:
        - obj: the table
        - already_focused: False if object just received focus
        - forceMessage: used for when whereAmI really needs the tutorial string.

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []

        if (not already_focused):
            try:
                parent_table = obj.parent.queryTable()
            except NotImplementedError:
                parent_table = None
            if settings.readTableCellRow and parent_table \
                and (not self._script.isLayoutOnly(obj.parent)):
                parent = obj.parent
                index = self._script.getCellIndex(obj)
                row = parent_table.getRowAtIndex(index)
                column = parent_table.getColumnAtIndex(index)

                # This is an indication of whether we should speak all the
                # table cells (the user has moved focus up or down a row),
                # or just the current one (focus has moved left or right in
                # the same row).
                #
                speakAll = True
                if "lastRow" in self._script.pointOfReference and \
                    "lastColumn" in self._script.pointOfReference:
                    pointOfReference = self._script.pointOfReference
                    speakAll = (pointOfReference["lastRow"] != row) or \
                        ((row == 0 or row == parent_table.nRows-1) and \
                           pointOfReference["lastColumn"] == column)

                utterances.extend(self._getTutorialForTableCell(obj,
                                        already_focused, forceMessage))
            else:
                utterances = self._getTutorialForTableCell(obj, 
                  already_focused, forceMessage)
        else:
            utterances = self._getTutorialForTableCell(obj, already_focused, \
              forceMessage)

        self._debugGenerator("_getTutorialForTableCellRow",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getTutorialForRadioButton(self, obj, already_focused, forceMessage):
        """Get the tutorial string for a radio button.

        Arguments:
        - obj: the radio button
        - already_focused: False if object just received focus
        - forceMessage: used for when whereAmI really needs the tutorial string.

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []
        # Translators: this is a tip for the user, how to navigate radiobuttons.
        msg = _("Use arrow keys to change.")

        if (not already_focused and self.lastTutorial != [msg]) or forceMessage:
            utterances.append(msg)

        self._debugGenerator("_getTutorialForRadioButton",
                             obj,
                             already_focused,
                             utterances)
        return utterances

    def _getTutorialForMenu(self, obj, already_focused, forceMessage):
        """Get the tutorial string for a menu.

        Arguments:
        - obj: the menu
        - already_focused: False if object just received focus
        - forceMessage: used for when whereAmI really needs the tutorial string.

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []
        # Translators: this is a tip for the user, how to navigate menues.
        mainMenuMsg = _("To navigate, press left or right arrow. " \
                       "To move through items press up or down arrow.")

        # Translators: this is a tip for the user, how to 
        # navigate into sub menues.
        subMenuMsg = _("To enter sub menu, press right arrow.")        
        
        # Checking if we are a submenu,
        # we can't rely on our parent being just a menu.
        if obj.parent.name != "" and obj.parent.__class__ == obj.__class__:
            if (self.lastTutorial != [subMenuMsg]) or forceMessage:
                utterances.append(subMenuMsg)
        else:
            if (self.lastTutorial != [mainMenuMsg]) or forceMessage:
                utterances.append(mainMenuMsg)

        self._debugGenerator("_getTutorialForMenu",
                             obj,
                             already_focused,
                             utterances)
        return utterances

    def _getTutorialForSlider(self, obj, already_focused, forceMessage):
        """Get the tutorial string for a slider.  If the object already has
        focus, then no tutorial is given.

        Arguments:
        - obj: the slider
        - already_focused: False if object just received focus
        - forceMessage: used for when whereAmI really needs the tutorial string.

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []
        # Translators: this is the tutorial string for when landing 
        # on a slider.
        msg = _("To decrease press left arrow, to increase press right arrow." \
          " To go to minimum press home, and for maximum press end.")
              
        if (not already_focused and self.lastTutorial != [msg]) or forceMessage:
            utterances.append(msg)

        self._debugGenerator("_getTutorialForSlider",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def getTutorial(self, obj, already_focused, forceMessage = False):
        """Get the tutorial for an Accessible object.  This will look
        first to the specific tutorial generators and if this 
        does not exist then return the empty tutorial.
        This method is the primary method
        that external callers of this class should use.

        Arguments:
        - obj: the object
        - already_focused: False if object just received focus
        - forceMessage: used for when whereAmI really needs the tutorial string.

        Returns a list of utterances to be spoken.
        """

        if not settings.enableTutorialMessages:
            return []
        
        role = obj.getRole()
        if role in self.tutorialGenerators:
            generator = self.tutorialGenerators[role]
        else:
            generator = self._getDefaultTutorial
        msg = generator(obj, already_focused, forceMessage)
        utterances = [" ".join(msg)]
        if msg:
            self.lastTutorial = msg
        if forceMessage:
            self.lastTutorial = ""

        self._debugGenerator("getTutorial",
                             obj,
                             already_focused,
                             utterances)
        return utterances
