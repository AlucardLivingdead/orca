# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
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

"""Custom script for StarOffice and OpenOffice."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.speech_generator as speech_generator
import orca.settings as settings

from orca.orca_i18n import _ # for gettext support

import script_settings

class SpeechGenerator(speech_generator.SpeechGenerator):

    # pylint: disable-msg=W0142

    def __init__(self, script):
        speech_generator.SpeechGenerator.__init__(self, script)

    def __overrideParagraph(self, obj, **args):
        # Treat a paragraph which is serving as a text entry in a dialog
        # as a text object.
        #
        role = args.get('role', obj.getRole())
        override = \
            role == "text frame" \
            or (role == pyatspi.ROLE_PARAGRAPH \
                and self._script.getAncestor(obj,
                                             [pyatspi.ROLE_DIALOG],
                                             [pyatspi.ROLE_APPLICATION]))
        return override

    def _getRoleName(self, obj, **args):
        result = []
        role = args.get('role', obj.getRole())
        if role in [pyatspi.ROLE_PUSH_BUTTON, pyatspi.ROLE_TOGGLE_BUTTON] \
           and obj.parent.getRole() == pyatspi.ROLE_TOOL_BAR:
            # We don't speak roles for the objects in the toolbar.
            #
            pass
        else:
            # Treat a paragraph which is serving as a text entry in a dialog
            # as a text object.
            #
            override = self.__overrideParagraph(obj, **args)
            if override:
                oldRole = self._overrideRole(pyatspi.ROLE_TEXT, args)
            result.extend(speech_generator.SpeechGenerator._getRoleName(
                          self, obj, **args))
            if override:
                self._restoreRole(oldRole, args)
        return result

    def _getTextRole(self, obj, **args):
        result = []
        role = args.get('role', obj.getRole())
        if role != pyatspi.ROLE_PARAGRAPH \
           or self.__overrideParagraph(obj, **args):
            result.extend(self._getRoleName(obj, **args))
        return result

    def _getLabelOrName(self, obj, **args):
        """Gets the label or the name if the label is not preset."""
        result = []
        override = self.__overrideParagraph(obj, **args)
        # Treat a paragraph which is serving as a text entry in a dialog
        # as a text object.
        #
        if override:
            result.extend(self._getLabel(obj, **args))
            if len(result) == 0 and obj.parent:
                parentLabel = self._getLabel(obj.parent, **args)
                # If we aren't already focused, we will have spoken the
                # parent as part of the speech context and do not want
                # to repeat it.
                #
                already_focused = args.get('already_focused', False)
                if already_focused:
                    result.extend(parentLabel)
                # If we still don't have a label, look to the name.
                #
                if not parentLabel and obj.name and len(obj.name):
                    result.append(obj.name)
        else:
            result.extend(speech_generator.SpeechGenerator._getLabelOrName(
                self, obj, **args))
        return result

    def _getToggleState(self, obj, **args):
        """Treat push buttons (which act like toggle buttons) and toggle
        buttons in the toolbar specially.  This is so we can have more
        natural sounding speech such as "bold on", "bold off", etc."""
        result = []
        role = args.get('role', obj.getRole())
        if role in [pyatspi.ROLE_PUSH_BUTTON, pyatspi.ROLE_TOGGLE_BUTTON] \
           and obj.parent.getRole() == pyatspi.ROLE_TOOL_BAR:
            if obj.getState().contains(pyatspi.STATE_CHECKED):
                # Translators: this represents the state of a check box
                #
                result.append(_("on"))
            else:
                # Translators: this represents the state of a check box
                #
                result.append(_("off"))
        elif role == pyatspi.ROLE_TOGGLE_BUTTON:
            result.extend(speech_generator.SpeechGenerator._getToggleState(
                self, obj, **args))
        return result

    def _getNewRowHeader(self, obj, **args):
        result = []
        # Check to see if this spread sheet cell has either a dynamic
        # row heading associated with it.
        #
        table = self._script.getTable(obj)
        parent = obj.parent
        try:
            parentTable = parent.queryTable()
        except NotImplementedError:
            parentTable = None
        index = self._script.getCellIndex(obj)
        if "lastRow" in self._script.pointOfReference and \
           self._script.pointOfReference["lastRow"] != \
           parentTable.getRowAtIndex(index):
            if table in self._script.dynamicRowHeaders:
                column = self._script.dynamicRowHeaders[table]
                header = self._script.getDynamicColumnHeaderCell(obj, column)
                try:
                    headerText = header.queryText()
                except:
                    headerText = None
                if header.childCount > 0:
                    for child in header:
                        text = self._script.getText(child, 0, -1)
                        if text:
                            result.append(text)
                elif headerText:
                    text = self._script.getText(header, 0, -1)
                    if text:
                        result.append(text)
        return result

    def _getNewColumnHeader(self, obj, **args):
        result = []
        # Check to see if this spread sheet cell has either a dynamic
        # row heading associated with it.
        #
        table = self._script.getTable(obj)
        parent = obj.parent
        try:
            parentTable = parent.queryTable()
        except NotImplementedError:
            parentTable = None
        index = self._script.getCellIndex(obj)
        if "lastColumn" in self._script.pointOfReference and \
           self._script.pointOfReference["lastColumn"] != \
           parentTable.getColumnAtIndex(index):
            if table in self._script.dynamicColumnHeaders:
                row = self._script.dynamicColumnHeaders[table]
                header = self._script.getDynamicRowHeaderCell(obj, row)
                try:
                    headerText = header.queryText()
                except:
                    headerText = None
                if header.childCount > 0:
                    for child in header:
                        text = self._script.getText(child, 0, -1)
                        if text:
                            result.append(text)
                elif headerText:
                    text = self._script.getText(header, 0, -1)
                    if text:
                        result.append(text)
        return result

    def _getSpreadSheetCell(self, obj, **args):
        result = []
        if self._script.inputLineForCell == None:
            self._script.inputLineForCell = \
                self._script.locateInputLine(obj)
        try:
            if obj.queryText():
                objectText = self._script.getText(obj, 0, -1)
                if not script_settings.speakCellCoordinates \
                   and len(objectText) == 0:
                    # Translators: this indicates an empty (blank) spread
                    # sheet cell.
                    #
                    objectText = _("blank")
                    result.append(objectText)
        except NotImplementedError:
            pass

        if script_settings.speakCellCoordinates:
            nameList = obj.name.split()
            # We were assuming that the word for "cell" would always
            # precede the coordinates. This is not the case for all
            # languages (e.g. Hungarian). See bug #562532. Therefore
            # examine each item and choose the one which contains a
            # digit.
            #
            for name in nameList:                    
                for char in name.decode("UTF-8"):
                    if char.isdigit():
                        result.append(name)
        return result

    def _getRealTableCell(self, obj, **args):
        """Get the speech for a table cell. If this isn't inside a
        spread sheet, just return the utterances returned by the default
        table cell speech handler.

        Arguments:
        - obj: the table cell
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """
        result = []
        if self._script.isSpreadSheetCell(obj):
            result.extend(self._getSpreadSheetCell(obj, **args))
        else:
            # Check to see how many children this table cell has. If it's
            # just one (or none), then pass it on to the superclass to be
            # processed.
            #
            # If it's more than one, then get the speech for each child,
            # and call this method again.
            #
            if obj.childCount <= 1:
                result.extend(speech_generator.SpeechGenerator.\
                              _getRealTableCell(self, obj, **args))
            else:
                for child in obj:
                    result.extend(self._getRealTableCell(child, **args))
        return result

    def _getTableCellRow(self, obj, **args):
        """Get the speech for a table cell row or a single table cell
        if settings.readTableCellRow is False. If this isn't inside a
        spread sheet, just return the utterances returned by the default
        table cell speech handler.

        Arguments:
        - obj: the table cell
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """
        result = []
        if self._script.isSpreadSheetCell(obj):
            if settings.readTableCellRow:
                parent = obj.parent
                parentTable = parent.queryTable()
                index = self._script.getCellIndex(obj)
                row = parentTable.getRowAtIndex(index)
                column = parentTable.getColumnAtIndex(index)
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
                           ((row == 0 or row == parentTable.nRows-1) and \
                            pointOfReference["lastColumn"] == column)
                if speakAll:
                    [startIndex, endIndex] = \
                        self._script.getSpreadSheetRowRange(obj)
                    for i in range(startIndex, endIndex+1):
                        cell = parentTable.getAccessibleAt(row, i)
                        showing = cell.getState().contains( \
                                      pyatspi.STATE_SHOWING)
                        if showing:
                            result.extend(self._getRealTableCell(cell, **args))
                else:
                    result.extend(self._getRealTableCell(obj, **args))
            else:
                result.extend(self._getRealTableCell(obj, **args))
        else:
            print "HERE", settings.readTableCellRow
            result.extend(speech_generator.SpeechGenerator._getTableCellRow(
                          self, obj, **args))
        return result
