# Orca
#
# Copyright 2005-2006 Sun Microsystems Inc.
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

"""Custom script for StarOffice and OpenOffice."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2006 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.debug as debug
import orca.atspi as atspi
import orca.default as default
import orca.input_event as input_event
import orca.rolenames as rolenames
import orca.braille as braille
import orca.braillegenerator as braillegenerator
import orca.orca_state as orca_state
import orca.speech as speech
import orca.speechgenerator as speechgenerator
import orca.settings as settings
import orca.keybindings as keybindings
import orca.util as util

from orca.orca_i18n import _ # for gettext support

inputLineForCell = None

# Dictionaries for the calc dynamic row and column headers.
#
dynamicColumns = {}
dynamicRows = {}

def getCalcTable(obj):
    """Get the table that this table cell is in.

    Arguments:
    - obj: the table cell.

    Return the table that this table cell is in, or None if this object
    isn't in a table.
    """

    table = None
    if obj.role == rolenames.ROLE_TABLE_CELL and obj.parent:
        table = obj.parent.table

    return table

def getDynamicColumnHeaderCell(obj, column):
    """Given a table cell, return the dynamic column header cell associated
    with it.

    Arguments:
    - obj: the table cell.
    - column: the column that this dynamic header is on.

    Return the dynamic column header cell associated with the given table cell.
    """

    accCell = None
    parent = obj.parent
    if parent and parent.table:
        row = parent.table.getRowAtIndex(obj.index)
        cell = parent.table.getAccessibleAt(row, column)
        accCell = atspi.Accessible.makeAccessible(cell)

    return accCell

def getDynamicRowHeaderCell(obj, row):
    """Given a table cell, return the dynamic row header cell associated
    with it.

    Arguments:
    - obj: the table cell.
    - row: the row that this dynamic header is on.

    Return the dynamic row header cell associated with the given table cell.
    """

    accCell = None
    parent = obj.parent
    if parent and parent.table:
        column = parent.table.getColumnAtIndex(obj.index)
        cell = parent.table.getAccessibleAt(row, column)
        accCell = atspi.Accessible.makeAccessible(cell)

    return accCell

def locateInputLine(obj):
    """Return the spread sheet input line. This only needs to be found
    the very first time a spread sheet table cell gets focus. We use the
    table cell to work back up the component hierarchy until we have found
    the common panel that both it and the input line reside in. We then
    use that as the base component to search for a component which has a
    paragraph role. This will be the input line.

    Arguments:
    - obj: the spread sheet table cell that has just got focus.

    Returns the spread sheet input line component.
    """

    inputLine = None
    panel = obj.parent.parent.parent.parent
    if panel and panel.role == rolenames.ROLE_PANEL:
        allParagraphs = util.findByRole(panel, rolenames.ROLE_PARAGRAPH)
        if len(allParagraphs) == 1:
            inputLine = allParagraphs[0]
        else:
            debug.println(debug.LEVEL_SEVERE,
                  "StarOffice: locateInputLine: incorrect paragraph count.")
    else:
        debug.println(debug.LEVEL_SEVERE,
                  "StarOffice: locateInputLine: couldn't find common panel.")

    return inputLine

def isSpreadSheetCell(obj):
    """Return an indication of whether the given obj is a spread sheet
    table cell.

    Arguments:
    - obj: the object to check.

    Returns True if this is a table cell, False otherwise.
    """

    rolesList = [rolenames.ROLE_TABLE_CELL, \
                 rolenames.ROLE_TABLE, \
                 rolenames.ROLE_UNKNOWN, \
                 rolenames.ROLE_SCROLL_PANE, \
                 rolenames.ROLE_PANEL, \
                 rolenames.ROLE_ROOT_PANE, \
                 rolenames.ROLE_FRAME, \
                 rolenames.ROLE_APPLICATION]
    return util.isDesiredFocusedItem(obj, rolesList)

class BrailleGenerator(braillegenerator.BrailleGenerator):
    """Overrides _getBrailleRegionsForTableCell so that, when we are in
    a spread sheet, we can braille the location of the table cell as well
    as the contents.
    """

    def _getBrailleRegionsForTableCell(self, obj):
        """Get the braille for a table cell. If this isn't inside a
        spread sheet, just return the regions returned by the default
        table cell braille handler.

        Arguments:
        - obj: the table cell

        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """

        global dynamicColumns, dynamicRows
        global getColumnHeaderCell, getRowHeaderCell
        global inputLineForCell, isSpreadSheetCell, locateInputLine

        if isSpreadSheetCell(obj):
            if inputLineForCell == None:
                inputLineForCell = locateInputLine(obj)

            regions = []

            # Check to see if this spread sheet cell has either a dynamic
            # column or row (or both) associated with it. If it does, then
            # braille those first before brailling the cell contents.
            #
            table = getCalcTable(obj)
            if dynamicColumns.has_key(table):
                column = dynamicColumns[table]
                if column:
                    header = getDynamicColumnHeaderCell(obj, column)
                    if header.text:
                        text = header.text.getText(0, -1)
                        if text:
                            regions.append(braille.Region(" " + text))

            if dynamicRows.has_key(table):
                row = dynamicRows[table]
                if row:
                    header = getDynamicRowHeaderCell(obj, row)
                    if header.text:
                        text = header.text.getText(0, -1)
                        if text:
                            regions.append(braille.Region(" " + text + " "))

            text = util.getDisplayedText(obj)
            componentRegion = braille.Component(obj, text)
            regions.append(componentRegion)

            # If the spread sheet table cell has something in it, then we
            # want to append the name of the cell (which will be its location).
            # Note that if the cell was empty, then util.getDisplayedText will
            # have already done this for us.
            #
            if obj.text:
                objectText = obj.text.getText(0, -1)
                if objectText and len(objectText) != 0:
                    regions.append(braille.Region(" " + obj.name))

            return [regions, componentRegion]

        else:
            brailleGen = braillegenerator.BrailleGenerator
            regions = brailleGen._getBrailleRegionsForTableCell(self, obj)

            return regions

class SpeechGenerator(speechgenerator.SpeechGenerator):
    """Overrides _getSpeechForTableCell so that, when we are in a spread
    sheet, we can speak the location of the table cell as well as the
    contents.
    """

    def _getSpeechForTableCell(self, obj, already_focused):
        """Get the speech for a table cell. If this isn't inside a
        spread sheet, just return the utterances returned by the default
        table cell speech handler.

        Arguments:
        - obj: the table cell
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        global dynamicColumns, dynamicRows
        global getColumnHeaderCell, getRowHeaderCell
        global inputLineForCell, isSpreadSheetCell, locateInputLine

        if isSpreadSheetCell(obj):
            utterances = []

            # Check to see if this spread sheet cell has either a dynamic
            # column or row (or both) associated with it. If it does, then
            # speak those first before speaking the cell contents.
            #
            table = getCalcTable(obj)
            if dynamicColumns.has_key(table):
                column = dynamicColumns[table]
                if column:
                    header = getDynamicColumnHeaderCell(obj, column)
                    if header.text:
                        text = header.text.getText(0, -1)
                        if text:
                            utterances.append(text)

            if dynamicRows.has_key(table):
                row = dynamicRows[table]
                if row:
                    header = getDynamicRowHeaderCell(obj, row)
                    if header.text:
                        text = header.text.getText(0, -1)
                        if text:
                            utterances.append(text)

            utterances.append(util.getDisplayedText(\
                    util.getRealActiveDescendant(obj)))

            if inputLineForCell == None:
                inputLineForCell = locateInputLine(obj)

            # If the spread sheet table cell has something in it, then we
            # want to append the name of the cell (which will be its location).
            # Note that if the cell was empty, then util.getDisplayedText will
            # have already done this for us.
            #
            if obj.text:
                objectText = obj.text.getText(0, -1)
                if objectText and len(objectText) != 0:
                    utterances.append(" " + obj.name)
        else:
            speechGen = speechgenerator.SpeechGenerator
            utterances = speechGen._getSpeechForTableCell(self, obj,
                                                      already_focused)

        return utterances

########################################################################
#                                                                      #
# The StarOffice script class.                                         #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        global dynamicColumns, dynamicRows

        default.Script.__init__(self, app)

        # Set the debug level for all the methods in this script.
        #
        self.debugLevel = debug.LEVEL_FINEST

        # A handle to the last spread sheet cell encountered.
        #
        self.lastCell = None

        # The following variables will be used to try to determine if we've
        # already handled this misspelt word (see readMisspeltWord() for
        # more details.

        self.lastTextLength = -1
        self.lastBadWord = ''
        self.lastStartOff = -1
        self.lastEndOff = -1

        # Used to determine if the user has double-clicked the dynamic
        # row/column hotkeys.

        self.lastDynamicEvent = None

    def getBrailleGenerator(self):
        """Returns the braille generator for this script.
        """

        return BrailleGenerator()

    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """

        return SpeechGenerator()

    def setupInputEventHandlers(self):
        """Defines InputEventHandler fields for this script that can be
        called by the key and braille bindings. In this particular case,
        we just want to be able to add a handler to return the contents of
        the input line.
        """

        default.Script.setupInputEventHandlers(self)

        self.inputEventHandlers["speakInputLineHandler"] = \
            input_event.InputEventHandler(
                Script.speakInputLine,
                _("Speaks the contents of the input line."))

        self.inputEventHandlers["setDynamicColumnHandler"] = \
            input_event.InputEventHandler(
                Script.setDynamicColumn,
                _("Set the dynamic column to use when speaking calc cells."))

        self.inputEventHandlers["setDynamicRowHandler"] = \
            input_event.InputEventHandler(
                Script.setDynamicRow,
                _("Set the dynamic row to use when speaking calc cells."))

    def getKeyBindings(self):
        """Defines the key bindings for this script. Setup the default
        key bindings, then add one in for reading the input line.

        Returns an instance of keybindings.KeyBindings.
        """

        keyBindings = default.Script.getKeyBindings(self)

        keyBindings.add(
            keybindings.KeyBinding(
                "a",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.inputEventHandlers["speakInputLineHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "c",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.inputEventHandlers["setDynamicColumnHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "r",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.inputEventHandlers["setDynamicRowHandler"]))

        return keyBindings

    def speakInputLine(self, inputEvent):
        """Speak the contents of the spread sheet input line (assuming we
        have a handle to it - generated when we first focus on a spread
        sheet table cell.

        This will be either the contents of the table cell that has focus
        or the formula associated with it.

        Arguments:
        - inputEvent: if not None, the input event that caused this action.
        """

        debug.println(self.debugLevel, "StarOffice.speakInputLine.")

        # Check to see if the current focus is a table cell.
        #
        if isSpreadSheetCell(orca_state.locusOfFocus):
            if inputLineForCell and inputLineForCell.text:
                inputLine = self.getText(inputLineForCell, 0, -1)
                if not inputLine:
                    inputLine = _("empty")
                debug.println(self.debugLevel,
                        "StarOffice.speakInputLine: contents: %s" % inputLine)
                speech.speak(inputLine)

    def getCalcRow(self, cell):
        """Get the row number in the table that this table cell is on.

        Arguments:
        - cell: the table cell to get the row number for.

        Return the row number that this table cell is on, or None if
        this isn't a table cell.
        """

        row = None
        if cell.role == rolenames.ROLE_TABLE_CELL:
            parent = cell.parent
            if parent and parent.table:
                row = parent.table.getRowAtIndex(cell.index)

        return row

    def getCalcColumn(self, cell):
        """Get the column number in the table that this table cell is on.

        Arguments:
        - cell: the table cell to get the column number for.

        Return the column number that this table cell is on, or None if
        this isn't a table cell.
        """

        column = None
        if cell.role == rolenames.ROLE_TABLE_CELL:
            parent = cell.parent
            if parent and parent.table:
                column = parent.table.getColumnAtIndex(cell.index)

        return column

    def setDynamicColumn(self, inputEvent):
        """Set the dynamic header column to use when speaking calc cell 
        entries.  In order to set the column, the user should first set 
        focus to the column that they wish to define and then press Insert-c.

        Once the user has defined the column, it will be used to first speak 
        this header when moving between rows or columns. 

        A "double-click" of the Insert-c hotkey, will clear the dynamic
        header column.

        Arguments:
        - inputEvent: if not None, the input event that caused this action.
        """

        global dynamicColumns, getCalcTable

        debug.println(self.debugLevel, "StarOffice.setDynamicColumn.")

        clickCount = util.getClickCount(self.lastDynamicEvent, inputEvent)
        table = getCalcTable(orca_state.locusOfFocus)
        if table:
            column = self.getCalcColumn(orca_state.locusOfFocus)
            if clickCount == 2:
                dynamicColumns[table] = None
            else:
                dynamicColumns[table] = column
        self.lastDynamicEvent = inputEvent

        return True

    def setDynamicRow(self, inputEvent):
        """Set the dynamic header row to use when speaking calc cell entries.
        In order to set the row, the user should first set focus to the row
        that they wish to define and then press Insert-r.

        Once the user has defined the row, it will be used to first speak
        this header when moving between rows or columns.

        A "double-click" of the Insert-r hotkey, will clear the dynamic
        header row.

        Arguments:
        - inputEvent: if not None, the input event that caused this action.
        """

        global dynamicRows, getCalcTable

        debug.println(self.debugLevel, "StarOffice.setDynamicRow.")

        clickCount = util.getClickCount(self.lastDynamicEvent, inputEvent)
        table = getCalcTable(orca_state.locusOfFocus)
        if table:
            row = self.getCalcRow(orca_state.locusOfFocus)
            if clickCount == 2:
                dynamicRows[table] = None
            else:
                dynamicRows[table] = row
        self.lastDynamicEvent = inputEvent

        return True

    def readMisspeltWord(self, event, pane):
        """Speak/braille the current misspelt word plus its context.
           The spell check dialog contains a "paragraph" which shows the
           context for the current spelling mistake. After speaking/brailling
           the default action for this component, that a selection of the
           surronding text from that paragraph with the misspelt word is also
           spoken.

        Arguments:
        - event: the event.
        - pane: the option pane in the spell check dialog.
        """

        paragraph = util.findByRole(pane, rolenames.ROLE_PARAGRAPH)

        # Determine which word is the misspelt word. This word will have
        # non-default text attributes associated with it.

        textLength = paragraph[0].text.characterCount
        startFound = False
        endOff = textLength
        for i in range(0, textLength):
            attributes = paragraph[0].text.getAttributes(i)
            if len(attributes[0]) != 0:
                if not startFound:
                    startOff = i
                    startFound = True
            else:
                if startFound:
                    endOff = i
                    break

        badWord = self.getText(paragraph[0], startOff, endOff - 1)

        # Note that we often get two or more of these focus or property-change
        # events each time there is a new misspelt word. We extract the
        # length of the line of text, the misspelt word, the start and end
        # offsets for that word and compare them against the values saved
        # from the last time this routine was called. If they are the same
        # then we ignore it.

        debug.println(self.debugLevel, \
            "StarOffice.readMisspeltWord: type=%s  word=%s(%d,%d)  len=%d" % \
            (event.type, badWord, startOff, endOff, textLength))

        if (textLength == self.lastTextLength) and \
           (badWord == self.lastBadWord) and \
           (startOff == self.lastStartOff) and \
           (endOff == self.lastEndOff):
            return

        # Create a list of all the words found in the misspelt paragraph.
        #
        text = self.getText(paragraph[0], 0, -1)
        allTokens = text.split()

        util.speakMisspeltWord(allTokens, badWord)

        # Save misspelt word information for comparison purposes next
        # time around.
        #
        self.lastTextLength = textLength
        self.lastBadWord = badWord
        self.lastStartOff = startOff
        self.lastEndOff = endOff

    def endOfLink(self, obj, word, startOffset, endOffset):
        """Return an indication of whether the given word contains the
           end of a hypertext link.

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
               interface
        - word: the word to check
        - startOffset: the start offset for this word
        - endOffset: the end offset for this word

        Returns True if this word contains the end of a hypertext link.
        """

        nLinks = obj.hypertext.getNLinks()
        links = []
        for i in range(0, nLinks):
            links.append(obj.hypertext.getLink(i))

        for i in range(0, len(links)):
            if links[i].endIndex > startOffset and \
               links[i].endIndex <= endOffset:
                return True

        return False

    def sayWriterWord(self, obj, word, startOffset, endOffset):
        """Speaks the given word in the appropriate voice. If this word is
        a hypertext link and it is also at the end offset for one of the
        links, then the word "link" is also spoken.

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
               interface
        - word: the word to speak
        - startOffset: the start offset for this word
        - endOffset: the end offset for this word
        """

        voices = settings.voices

        for i in range(startOffset, endOffset):
            if util.getLinkIndex(obj, i) >= 0:
                voice = voices[settings.HYPERLINK_VOICE]
                break
            elif word.isupper():
                voice = voices[settings.UPPERCASE_VOICE]
            else:
                voice = voices[settings.DEFAULT_VOICE]

        speech.speak(word, voice)
        if self.endOfLink(obj, word, startOffset, endOffset):
            speech.speak(_("link"))

    def isSetupDialog(self, obj):
        """ Check to see if this object is in the Setup dialog by walking
        back up the object hierarchy until we get to the dialog object and
        checking to see if it has a name that starts with "Welcome to
        StarOffice".

        Arguments:
        - obj: an Accessible object that implements the AccessibleText
               interface

        Returns an indication of whether this object is in the Setup dialog.
        """

        found = False
        while obj and obj.role != rolenames.ROLE_APPLICATION:
            if obj.role == rolenames.ROLE_DIALOG and \
                (obj.name and obj.name.startswith(_("Welcome to StarOffice"))):
                debug.println(self.debugLevel,
                              "StarOffice.isSetupDialog: True.")
                found = True

            obj = obj.parent

        return found

    def speakSetupLabel(self, label):
        """Speak this Setup dialog label.

        Arguments:
        - label: the Setup dialog Label.
        """

        text = util.getDisplayedText(label)
        if text:
            speech.speak(text)

    def handleSetupPanel(self, panel):
        """Find all the labels in this Setup panel and speak them.

        Arguments:
        - panel: the Setup panel.
        """

        allLabels = util.findByRole(panel, rolenames.ROLE_LABEL)
        for i in range(0, len(allLabels)):
            self.speakSetupLabel(allLabels[i])

    # This method tries to detect and handle the following cases:
    # 1) Writer: text paragraph.
    # 2) Writer: spell checking dialog.
    # 3) Welcome to StarOffice dialog.

    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """

        brailleGen = self.brailleGenerator
        speechGen = self.speechGenerator

        debug.printObjectEvent(self.debugLevel,
                               event,
                               event.source.toString())

        # util.printAncestry(event.source)

        # 1) Writer: text paragraph.
        #
        # When the focus is on a paragraph in the Document view of the Writer,
        # then just speak/braille the current line (rather than speaking a
        # bogus initial "paragraph" utterance as well).

        rolesList = [rolenames.ROLE_PARAGRAPH, \
                     rolenames.ROLE_UNKNOWN, \
                     rolenames.ROLE_SCROLL_PANE, \
                     rolenames.ROLE_PANEL, \
                     rolenames.ROLE_ROOT_PANE, \
                     rolenames.ROLE_FRAME]
        if util.isDesiredFocusedItem(event.source, rolesList):
            debug.println(self.debugLevel,
                  "StarOffice.locusOfFocusChanged - Writer: text paragraph.")

            result = util.getTextLineAtCaret(event.source)
            result[0] = result[0].decode("UTF-8")

            # Check to see if there are any hypertext links in this paragraph.
            # If no, then just speak the whole line. Otherwise, split the
            # line into words and call sayWriterWord() to speak that token
            # in the appropriate voice.
            #
            hypertext = event.source.hypertext
            if not hypertext or (hypertext.getNLinks() == 0):
                if settings.enableSpeechIndentation:
                    self.speakTextIndentation(event.source,
                                              result[0].encode("UTF-8"))
                speech.speak(result[0].encode("UTF-8"), None, False)
            else:
                started = False
                startOffset = 0
                for i in range(0, len(result[0])):
                    if result[0][i] == ' ':
                        if started:
                            endOffset = i
                            self.sayWriterWord(event.source,
                                result[0][startOffset:endOffset+1].encode("UTF-8"),
                                startOffset, endOffset)
                            startOffset = i
                            started = False
                    else:
                        if not started:
                            startOffset = i
                            started = True

                if started:
                    endOffset = len(result[0])
                    self.sayWriterWord(event.source,
                        result[0][startOffset:endOffset].encode("UTF-8"),
                        startOffset, endOffset)

            braille.displayRegions(brailleGen.getBrailleRegions(event.source))

            return

        # 2) Writer: spell checking dialog.
        #
        # Check to see if the Spell Check dialog has just appeared and got
        # focus. If it has, then speak/braille the current misspelt word
        # plus its context.
        #
        # Note that in order to make sure that this focus event is for the
        # spell check dialog, a check is made of the localized name of the
        # option pane. Translators for other locales will need to ensure that
        # their translation of this string matches what StarOffice uses in
        # that locale.

        rolesList = [rolenames.ROLE_PUSH_BUTTON, \
                     rolenames.ROLE_OPTION_PANE, \
                     rolenames.ROLE_DIALOG, \
                     rolenames.ROLE_APPLICATION]
        if util.isDesiredFocusedItem(event.source, rolesList):
            pane = event.source.parent
            if pane.name.startswith(_("Spellcheck:")):
                debug.println(self.debugLevel,
                    "StarOffice.locusOfFocusChanged - " \
                    + "Writer: spell check dialog.")

                self.readMisspeltWord(event, pane)

                # Fall-thru to process the event with the default handler.

        # 3) Welcome to StarOffice dialog.
        #
        # Check to see if the object that just got focus is in the Setup
        # dialog. If it is, then check for a variety of scenerios.

        if self.isSetupDialog(event.source):

            # Check for 2. License Agreement: Scroll Down button.
            #
            rolesList = [rolenames.ROLE_PUSH_BUTTON, \
                         rolenames.ROLE_PANEL, \
                         rolenames.ROLE_OPTION_PANE, \
                         rolenames.ROLE_DIALOG, \
                         rolenames.ROLE_APPLICATION]
            if util.isDesiredFocusedItem(event.source, rolesList):
                debug.println(self.debugLevel,
                    "StarOffice.locusOfFocusChanged - Setup dialog: " \
                    + "License Agreement screen: Scroll Down button.")
                self.handleSetupPanel(event.source.parent)
                speech.speak(_("Note that the Scroll Down button has to be pressed numerous times."))

            # Check for 2. License Agreement: Accept button.
            #
            rolesList = [rolenames.ROLE_UNKNOWN, \
                         rolenames.ROLE_SCROLL_PANE, \
                         rolenames.ROLE_PANEL, \
                         rolenames.ROLE_OPTION_PANE, \
                         rolenames.ROLE_DIALOG, \
                         rolenames.ROLE_APPLICATION]
            if util.isDesiredFocusedItem(event.source, rolesList):
                debug.println(self.debugLevel,
                    "StarOffice.locusOfFocusChanged - Setup dialog: " \
                    + "License Agreement screen: accept button.")
                speech.speak(_("License Agreement Accept button now has focus."))

            # Check for 3. Personal Data: Transfer Personal Data check box.
            #
            rolesList = [rolenames.ROLE_CHECK_BOX, \
                         rolenames.ROLE_PANEL, \
                         rolenames.ROLE_OPTION_PANE, \
                         rolenames.ROLE_DIALOG, \
                         rolenames.ROLE_APPLICATION]
            if util.isDesiredFocusedItem(event.source, rolesList):
                debug.println(self.debugLevel,
                    "StarOffice.locusOfFocusChanged - Setup dialog: " \
                    + "Personal Data: Transfer Personal Data check box.")
                self.handleSetupPanel(event.source.parent)

            # Check for 4. User name: First Name text field.
            #
            rolesList = [rolenames.ROLE_TEXT, \
                        rolenames.ROLE_PANEL, \
                        rolenames.ROLE_OPTION_PANE, \
                        rolenames.ROLE_DIALOG, \
                        rolenames.ROLE_APPLICATION]
            if util.isDesiredFocusedItem(event.source, rolesList) and \
               event.source.name == _("First name"):
                debug.println(self.debugLevel,
                    "StarOffice.locusOfFocusChanged - Setup dialog: " \
                    + "User name: First Name text field.")

                # Just speak the informative labels at the top of the panel
                # (and not the ones that have LABEL_FOR relationships).
                #
                panel = event.source.parent
                allLabels = util.findByRole(panel, rolenames.ROLE_LABEL)
                for i in range(0, len(allLabels)):
                    relations = allLabels[i].relations
                    hasLabelFor = False
                    for relation in relations:
                        if relation.getRelationType() \
                               == atspi.Accessibility.RELATION_LABEL_FOR:
                            hasLabelFor = True
                    if not hasLabelFor:
                        self.speakSetupLabel(allLabels[i])

            # Check for 5. Registration: Register Now radio button.
            #
            rolesList = [rolenames.ROLE_RADIO_BUTTON, \
                        rolenames.ROLE_PANEL, \
                        rolenames.ROLE_OPTION_PANE, \
                        rolenames.ROLE_DIALOG, \
                        rolenames.ROLE_APPLICATION]
            if util.isDesiredFocusedItem(event.source, rolesList):
                debug.println(self.debugLevel,
                    "StarOffice.locusOfFocusChanged - Setup dialog: " \
                    + "Registration: Register Now radio button.")
                self.handleSetupPanel(event.source.parent)

        # Pass the event onto the parent class to be handled in the default way.

        default.Script.locusOfFocusChanged(self, event,
                                           oldLocusOfFocus, newLocusOfFocus)

    # This method tries to detect and handle the following cases:
    # 1) Setup dialog.

    def onWindowActivated(self, event):
        """Called whenever a property on an object changes.

        Arguments:
        - event: the Event
        """

        debug.printObjectEvent(self.debugLevel,
                               event,
                               event.source.toString())

        # util.printAncestry(event.source)

        # 1) Setup dialog.
        #
        # Check to see if the Setup dialog window has just been activated.
        # If it has, then find the panel within it that has no name and
        # speak all the labels within that panel.
        #
        if self.isSetupDialog(event.source):
            debug.println(self.debugLevel,
                "StarOffice.onWindowActivated - Setup dialog: Welcome screen.")

            allPanels = util.findByRole(event.source.parent,
                                        rolenames.ROLE_PANEL)
            for i in range(0, len(allPanels)):
                if not allPanels[i].name:
                    allLabels = util.findByRole(allPanels[i],
                                                rolenames.ROLE_LABEL)
                    for i in range(0, len(allLabels)):
                        self.speakSetupLabel(allLabels[i])
        else:
            # Pass the event onto the parent class to be handled in the
            # default way.
            #
            default.Script.onWindowActivated(self, event)


    # This method tries to detect and handle the following cases:
    # 1) Writer: spell checking dialog.

    def onNameChanged(self, event):
        """Called whenever a property on an object changes.

        Arguments:
        - event: the Event
        """

        brailleGen = self.brailleGenerator
        speechGen = self.speechGenerator

        debug.printObjectEvent(self.debugLevel,
                               event,
                               event.source.toString())

        # util.printAncestry(event.source)

        # 1) Writer: spell checking dialog.
        #
        # Check to see if if we've had a property-change event for the
        # accessible name for the option pane in the spell check dialog.
        # This (hopefully) means that the user has just corrected a
        # spelling mistake, in which case, speak/braille the current
        # misspelt word plus its context.
        #
        # Note that in order to make sure that this focus event is for the
        # spell check dialog, a check is made of the localized name of the
        # option pane. Translators for other locales will need to ensure that
        # their translation of this string matches what StarOffice uses in
        # that locale.

        rolesList = [rolenames.ROLE_OPTION_PANE, \
                     rolenames.ROLE_DIALOG, \
                     rolenames.ROLE_APPLICATION]
        if util.isDesiredFocusedItem(event.source, rolesList):
            pane = event.source
            if pane.name.startswith(_("Spellcheck:")):
                debug.println(self.debugLevel,
                      "StarOffice.onNameChanged - Writer: spell check dialog.")

                self.readMisspeltWord(event, pane)

                # Fall-thru to process the event with the default handler.

        # Pass the event onto the parent class to be handled in the default way.

        default.Script.onNameChanged(self, event)

    # This method tries to detect and handle the following cases:
    # 1) Calc: spread sheet Name Box line.

    def onSelectionChanged(self, event):
        """Called when an object's selection changes.

        Arguments:
        - event: the Event
        """

        debug.printObjectEvent(self.debugLevel,
                               event,
                               event.source.toString())

        # util.printAncestry(event.source)

        # 1) Calc: spread sheet input line.
        #
        # If this "object:selection-changed" is for the spread sheet Name
        # Box, then check to see if the current locus of focus is a spread
        # sheet cell. If it is, and the contents of the input line are
        # different from what is displayed in that cell, then speak "has
        # formula" and append it to the braille line.
        #
        rolesList = [rolenames.ROLE_LIST, \
                     rolenames.ROLE_COMBO_BOX, \
                     rolenames.ROLE_PANEL, \
                     rolenames.ROLE_TOOL_BAR, \
                     rolenames.ROLE_PANEL, \
                     rolenames.ROLE_ROOT_PANE, \
                     rolenames.ROLE_FRAME, \
                     rolenames.ROLE_APPLICATION]
        if util.isDesiredFocusedItem(event.source, rolesList):
            if orca_state.locusOfFocus.role == rolenames.ROLE_TABLE_CELL:
                cell = orca_state.locusOfFocus

                # We are getting two "object:selection-changed" events
                # for each spread sheet cell move, so in order to prevent
                # appending "has formula" twice, we only do it if the last
                # cell is different from this one.
                #
                if cell != self.lastCell:
                    self.lastCell = cell

                    if cell.text:
                        cellText = self.getText(cell, 0, -1)
                        if cellText and len(cellText):
                            if inputLineForCell and inputLineForCell.text:
                                inputLine = self.getText(inputLineForCell,0,-1)
                                if inputLine and \
                                    (len(inputLine) > 1) and \
                                    (inputLine[0] == "="):
                                        hf = _(" has formula")
                                        speech.speak(hf, None, False)

                                        line = braille.getShowingLine()
                                        line.addRegion(braille.Region(hf))
                                        braille.refresh()
                                        #
                                        # Fall-thru to process the event with
                                        # the default handler.

        default.Script.onSelectionChanged(self, event)

    def getText(self, obj, startOffset, endOffset):
        """Returns the substring of the given object's text specialization.

        NOTE: This is here to handle the problematic implementation of
        getText by OpenOffice.  See the bug discussion at:

           http://bugzilla.gnome.org/show_bug.cgi?id=356425)

        Once the OpenOffice issue has been resolved, this method probably
        should be removed.

        Arguments:
        - obj: an accessible supporting the accessible text specialization
        - startOffset: the starting character position
        - endOffset: the ending character position
        """
        text = obj.text.getText(0, -1).decode("UTF-8")
        if startOffset >= len(text):
            startOffset = len(text) - 1
        if startOffset >= endOffset:
            endOffset = startOffset + 1
        string = text[max(0,startOffset):min(len(text),endOffset)]
        string = string.encode("UTF-8")
        return string
