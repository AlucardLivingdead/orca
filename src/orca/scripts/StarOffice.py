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

import orca.debug as debug
import orca.atspi as atspi
import orca.default as default
import orca.rolenames as rolenames
import orca.orca as orca
import orca.braille as braille
import orca.braillegenerator as braillegenerator
import orca.speech as speech
import orca.speechgenerator as speechgenerator
import orca.settings as settings
import orca.keybindings as keybindings
import orca.util as util

from orca.orca_i18n import _ # for gettext support

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

        rolesList = [rolenames.ROLE_TABLE_CELL, \
                     rolenames.ROLE_TABLE, \
                     rolenames.ROLE_UNKNOWN, \
                     rolenames.ROLE_SCROLL_PANE, \
                     rolenames.ROLE_PANEL, \
                     rolenames.ROLE_ROOT_PANE, \
                     rolenames.ROLE_FRAME, \
                     rolenames.ROLE_APPLICATION]
        if util.isDesiredFocusedItem(obj, rolesList):
            text = util.getDisplayedText(obj)
            regions = []
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

        speechGen = speechgenerator.SpeechGenerator
        utterances = speechGen._getSpeechForTableCell(self, obj, 
                                                      already_focused)

        rolesList = [rolenames.ROLE_TABLE_CELL, \
                     rolenames.ROLE_TABLE, \
                     rolenames.ROLE_UNKNOWN, \
                     rolenames.ROLE_SCROLL_PANE, \
                     rolenames.ROLE_PANEL, \
                     rolenames.ROLE_ROOT_PANE, \
                     rolenames.ROLE_FRAME, \
                     rolenames.ROLE_APPLICATION]
        if util.isDesiredFocusedItem(obj, rolesList):

            # If the spread sheet table cell has something in it, then we
            # want to append the name of the cell (which will be its location).
            # Note that if the cell was empty, then util.getDisplayedText will
            # have already done this for us.
            #
            if obj.text:
                objectText = obj.text.getText(0, -1)
                if objectText and len(objectText) != 0:
                    utterances.append(" " + obj.name)

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

        default.Script.__init__(self, app)

        # Set the debug level for all the methods in this script.
        #
        self.debugLevel = debug.LEVEL_FINEST

        # The following variables will be used to try to determine if we've
        # already handled this misspelt word (see readMisspeltWord() for
        # more details.

        self.lastTextLength = -1
        self.lastBadWord = ''
        self.lastStartOff = -1
        self.lastEndOff = -1

    def getBrailleGenerator(self):
        """Returns the braille generator for this script.
        """

        return BrailleGenerator()

    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """

        return SpeechGenerator()

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

        paragraph = atspi.findByRole(pane, rolenames.ROLE_PARAGRAPH)

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

        badWord = paragraph[0].text.getText(startOff, endOff-1)

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
        text = paragraph[0].text.getText(0, -1)
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

        isHyperText = False
        voices = settings.voices

        for i in range(startOffset, endOffset):
            if util.getLinkIndex(obj, i) >= 0:
                isHyperText = True
                voice = voices[settings.HYPERLINK_VOICE]
                break
            elif word.isupper():
                voice = voices[settings.UPPERCASE_VOICE]
            else:
                voice = voices[settings.DEFAULT_VOICE]

        speech.speak(word, voice)
        if self.endOfLink(obj, word, startOffset, endOffset):
            speech.speak(_("link"))

    # This method tries to detect and handle the following cases:
    # 1) Writer: text paragraph.
    # 2) Writer: spell checking dialog.

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

        # atspi.printAncestry(event.source)

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

            result = atspi.getTextLineAtCaret(event.source)

            # Check to see if there are any hypertext links in this paragraph.
            # If no, then just speak the whole line. Otherwise, split the
            # line into words and call sayWriterWord() to speak that token
            # in the appropriate voice.
            #
            hypertext = event.source.hypertext
            if not hypertext or (hypertext.getNLinks() == 0):
                speech.speak(result[0], None, False)
            else:
                started = False
                startOffset = 0
                for i in range(0, len(result[0])):
                    if result[0][i] == ' ':
                        if started:
                            endOffset = i
                            self.sayWriterWord(event.source,
                                result[0][startOffset:endOffset+1],
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
                                       result[0][startOffset:endOffset],
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
                    "StarOffice.locusOfFocusChanged - Writer: spell check dialog.")

                self.readMisspeltWord(event, pane)

                # Fall-thru to process the event with the default handler.

        # Pass the event onto the parent class to be handled in the default way.

        default.Script.locusOfFocusChanged(self, event,
                                           oldLocusOfFocus, newLocusOfFocus)

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

        # atspi.printAncestry(event.source)

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

