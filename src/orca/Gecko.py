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

"""Custom script for Gecko toolkit.  NOT WORKING WELL AT THE MOMENT."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2006 Sun Microsystems Inc."
__license__   = "LGPL"

import atspi
import braille
import braillegenerator
import debug
import default
import input_event
import keybindings
import orca
import orca_state
import rolenames
import settings
import speech
import speechgenerator
import util

from orca_i18n import _

# Embedded object character used to indicate that an object is
# embedded in a string.
#
EMBEDDED_OBJECT_CHARACTER = u'\ufffc'

# Roles that imply their text starts on a new line.
#
NEWLINE_ROLES = [rolenames.ROLE_PARAGRAPH,
                 rolenames.ROLE_SEPARATOR,
                 rolenames.ROLE_LIST_ITEM,
                 rolenames.ROLE_HEADING]

def _getAutocompleteEntry(obj):
    for i in range(0, obj.childCount):
        child = obj.child(i)
        if child.role == rolenames.ROLE_ENTRY:
            return child
    return None

########################################################################
#                                                                      #
# Custom BrailleGenerator                                              #
#                                                                      #
########################################################################

class BrailleGenerator(braillegenerator.BrailleGenerator):
    """Handle Gecko's unique hiearchical representation, such as menus
    duplicating themselves in the hierarchy and tables used for layout
    and indentation purposes.
    """

    def __init__(self, script):
        braillegenerator.BrailleGenerator.__init__(self, script)
        self.brailleGenerators[rolenames.ROLE_AUTOCOMPLETE] = \
             self._getBrailleRegionsForAutocomplete
        self.brailleGenerators[rolenames.ROLE_ENTRY]        = \
             self._getBrailleRegionsForText

    def _getBrailleRegionsForAutocomplete(self, obj):
        """Gets the role of an autocomplete box.  We let the handlers
        for the children do the rest.

        Arguments:
        - obj: an Accessible

        Returns a list where the first element is a list of Regions to
        display and the second element is the Region which should get
        focus.
        """

        self._debugGenerator("Gecko._getBrailleRegionsForAutocomplete", obj)

        regions = []
        if settings.brailleVerbosityLevel == settings.VERBOSITY_LEVEL_VERBOSE:
            regions.append(braille.Region(
                rolenames.getBrailleForRoleName(obj)))
        else:
            regions.append(braille.Region(""))

        return (regions, regions[0])

    def _getBrailleRegionsForText(self, obj):
        """Gets text to be displayed for an autocomplete box.

        Arguments:
        - obj: an Accessible

        Returns a list where the first element is a list of Regions to
        display and the second element is the Region which should get
        focus.
        """

        self._debugGenerator("Gecko._getBrailleRegionsForText", obj)

        parent = obj.parent
        if parent.role != rolenames.ROLE_AUTOCOMPLETE:
            return braillegenerator.BrailleGenerator._getBrailleRegionsForText(
                self, obj)

        regions = []

        label = util.getDisplayedLabel(parent)
        if not label or not len(label):
            label = parent.name

        textRegion = braille.Text(obj, label)
        regions.append(textRegion)
        eol = braille.Region(" $l")
        regions.append(eol)
        return [regions, textRegion]

    def _getBrailleRegionsForComboBox(self, obj):
        """Get the braille for a combo box.  If the combo box already has
        focus, then only the selection is displayed.

        Arguments:
        - obj: the combo box

        Returns a list where the first element is a list of Regions to display
        and the second element is the Region which should get focus.
        """

        self._debugGenerator("Gecko._getBrailleRegionsForComboBox", obj)

        regions = []

        # With Gecko, a combo box has a menu as a child.  If the menu
        # has a name (usually the case when the object is labelled by
        # something), then it is the text showing in the combo box.
        # If not, then the combo box is probably not labelled by
        # something.  If that's the case, then the name of the combo
        # box is the text that is showing.  Except perhaps if the
        # menu is popped up.  Then, the name is the name of the menu
        # item that is selected.
        #
        label = util.getDisplayedLabel(obj)
        menu = obj.child(0)

        focusedRegionIndex = 0
        if label and len(label):
            regions.append(braille.Region(label + " "))
            focusedRegionIndex = 1

        if menu.name:
            regions.append(braille.Region(menu.name))
        else:
            name = obj.name
            if menu.state.count(atspi.Accessibility.STATE_VISIBLE):
                selection = menu.selection
                item = selection.getSelectedChild(0)
                name = item.name
            regions.append(braille.Region(name))

        if settings.brailleVerbosityLevel == settings.VERBOSITY_LEVEL_VERBOSE:
            regions.append(braille.Region(
                " " + rolenames.getBrailleForRoleName(obj)))

        # Things may not have gone as expected above, so we'll do some
        # defensive programming to make sure we don't get an index out
        # of bounds.
        #
        if focusedRegionIndex >= len(regions):
            focusedRegionIndex = 0

        # [[[TODO: WDW - perhaps if a text area was created, we should
        # give focus to it.]]]
        #
        return [regions, regions[focusedRegionIndex]]

########################################################################
#                                                                      #
# Custom SpeechGenerator                                               #
#                                                                      #
########################################################################

class SpeechGenerator(speechgenerator.SpeechGenerator):
    """Handle Gecko's unique hiearchical representation, such as menus
    duplicating themselves in the hierarchy and tables used for layout
    and indentation purposes.
    """

    def __init__(self, script):
        speechgenerator.SpeechGenerator.__init__(self, script)
        self.speechGenerators[rolenames.ROLE_ENTRY]        = \
             self._getSpeechForText

    def _getSpeechForText(self, obj, already_focused):
        """Gets the speech for an autocomplete box.

        Arguments:
        - obj: an Accessible
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        parent = obj.parent
        if parent.role != rolenames.ROLE_AUTOCOMPLETE:
            [text, startOffset, endOffset] = util.getTextLineAtCaret(obj)
            return speechgenerator.SpeechGenerator._getSpeechForText(
                self, obj, already_focused)

        utterances = []

        label = util.getDisplayedLabel(parent)
        if not label or not len(label):
            label = parent.name
        utterances.append(label)

        utterances.extend(self._getSpeechForObjectRole(obj))

        [text, startOffset, endOffset] = util.getTextLineAtCaret(obj)
        utterances.append(text)

        self._debugGenerator("Gecko._getSpeechForText",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForComboBox(self, obj, already_focused):
        """Get the speech for a combo box.  If the combo box already has focus,
        then only the selection is spoken.

        Arguments:
        - obj: the combo box
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []

        # With Gecko, a combo box has a menu as a child.  If the menu
        # has a name (usually the case when the object is labelled by
        # something), then it is the text showing in the combo box.
        # If not, then the combo box is probably not labelled by
        # something.  If that's the case, then the name of the combo
        # box is the text that is showing.  Except perhaps if the
        # menu is popped up.  Then, the name is the name of the menu
        # item that is selected.
        #
        label = util.getDisplayedLabel(obj)
        menu = obj.child(0)

        if not already_focused and label:
            utterances.append(label)

        if not already_focused:
            utterances.extend(self._getSpeechForObjectRole(obj))

        if menu.name:
            utterances.append(menu.name)
        else:
            name = obj.name
            if menu.state.count(atspi.Accessibility.STATE_VISIBLE):
                selection = menu.selection
                item = selection.getSelectedChild(0)
                name = item.name
            utterances.append(name)

        utterances.extend(self._getSpeechForObjectAvailability(obj))

        self._debugGenerator("Gecko._getSpeechForComboBox",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def getSpeechContext(self, obj, stopAncestor=None):
        """Get the speech that describes the names and role of
        the container hierarchy of the object, stopping at and
        not including the stopAncestor.

        Arguments:
        - obj: the object
        - stopAncestor: the anscestor to stop at and not include (None
          means include all ancestors)

        Returns a list of utterances to be spoken.
        """

        utterances = []

        if not obj:
            return utterances

        if obj is stopAncestor:
            return utterances

        # We'll eliminate toolbars if we're in a menu.  The reason for
        # this is that Gecko puts its menu bar in a couple of nested
        # toolbars.
        #
        inMenuBar = False

        parent = obj.parent
        while parent and (parent.parent != parent):
            if parent == stopAncestor:
                break

            if parent.role == rolenames.ROLE_MENU_BAR:
                inMenuBar = True

            # We try to omit things like fillers off the bat...
            #
            if (parent.role == rolenames.ROLE_FILLER) \
                or (parent.role == rolenames.ROLE_LAYERED_PANE) \
                or (parent.role == rolenames.ROLE_SPLIT_PANE) \
                or (parent.role == rolenames.ROLE_SCROLL_PANE) \
                or (parent.role == rolenames.ROLE_UNKNOWN):
                parent = parent.parent
                continue

            text = util.getDisplayedText(parent)
            label = util.getDisplayedLabel(parent)

            # Don't announce unlabelled panels.
            #
            if parent.role == rolenames.ROLE_PANEL \
                and (((not label) or (len(label) == 0) \
                      or (not text) or (len(text) == 0))):
                parent = parent.parent
                continue

            # Skip table cells.
            #
            if parent.role == rolenames.ROLE_TABLE_CELL:
                parent = parent.parent
                continue

            # Skip unfocusable menus.  This is for earlier versions
            # of Firefox where menus were nested in kind of an odd
            # dual nested menu hierarchy.
            #
            if (parent.role == rolenames.ROLE_MENU) \
               and not parent.state.count(atspi.Accessibility.STATE_FOCUSABLE):
                parent = parent.parent
                continue

            # Well...if we made it this far, we will now append the
            # role, then the text, and then the label.
            #
            utterances.append(rolenames.getSpeechForRoleName(parent))

            # Now...autocompletes are wierd.  We'll let the handling of
            # the entry give us the name.
            #
            if parent.role == rolenames.ROLE_AUTOCOMPLETE:
                parent = parent.parent
                continue

            if text and (text != label) and len(text):
                utterances.append(text)

            if label and len(label):
                utterances.append(label)

            parent = parent.parent

        utterances.reverse()

        return utterances
        
########################################################################
#                                                                      #
# Script                                                               #
#                                                                      #
########################################################################

class Script(default.Script):
    """The script for Firefox.

    NOTE: THIS IS UNDER DEVELOPMENT AND DOES NOT PROVIDE ANY COMPELLING
    ACCESS TO FIREFOX AT THIS POINT.
    """

    ####################################################################
    #                                                                  #
    # Standard Script Methods                                          #
    #                                                                  #
    ####################################################################

    def __init__(self, app):
        #print "Gecko.__init__"
        default.Script.__init__(self, app)
        
    def getBrailleGenerator(self):
        """Returns the braille generator for this script.
        """
        return BrailleGenerator(self)

    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """
        return SpeechGenerator(self)

    def setupInputEventHandlers(self):
        """Defines InputEventHandler fields for this script that can be
        called by the key and braille bindings.
        """

        default.Script.setupInputEventHandlers(self)

        self.inputEventHandlers["dumpContentHandler"] = \
            input_event.InputEventHandler(
                Script.dumpContent,
                "Dumps document content.")

        self.inputEventHandlers["goNextHandler"] = \
            input_event.InputEventHandler(
                Script.goNextCharacter,
                "Goes to next character.")

    def getKeyBindings(self):
        """Defines the key bindings for this script.

        Returns an instance of keybindings.KeyBindings.
        """

        keyBindings = default.Script.getKeyBindings(self)

        keyBindings.add(
            keybindings.KeyBinding(
                "d",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.inputEventHandlers["dumpContentHandler"]))

        keyBindings.add(
            keybindings.KeyBinding(
                "w",
                1 << settings.MODIFIER_ORCA,
                1 << settings.MODIFIER_ORCA,
                self.inputEventHandlers["goNextHandler"]))

        return keyBindings

    def onCaretMoved(self, event):
        print "Gecko.onCaretMoved", event.detail1
        
        # We always automatically go back to focus tracking mode when
        # the caret moves in the focused object.
        #
        if self.flatReviewContext:
            self.toggleFlatReviewMode()

        [string, startOffset, endOffset] = event.source.text.getTextAtOffset(
            event.source.text.caretOffset,
            atspi.Accessibility.TEXT_BOUNDARY_LINE_START)
        #print "  text line at offset", string

        self._presentTextAtNewCaretPosition(event)

    def onNameChanged(self, event):
        """Called whenever a property on an object changes.

        Arguments:
        - event: the Event
        """
        # We ignore these because Gecko just happily keeps generating
        # name changed events for objects whose name don't change.
        #
        return

    # This function is called whenever an object within Gecko receives
    # focus
    #
    def onFocus(self, event):
        print "Gecko.onFocus"

        # We're going to ignore focus events on the frame.  They
        # are often intermingled with menu activity, wreaking havoc
        # on the context.
        #
        if (event.source.role == rolenames.ROLE_FRAME) \
           or (event.source.role == rolenames.ROLE_DOCUMENT_FRAME) \
           or (not len(event.source.role)):
            return

        # We're also going to ignore menus that are children of menu
        # bars.  They never really get focus themselves - it's always
        # a transient event and one of the menu items or submenus will
        # get focus immediately after the menu gets focus.  So...we
        # compress the events.
        #
        # [[[WDW - commented this out on 27-Jul-2006 based upon feedback
        # from Lynn Monsanto that it was getting in the way for Firefox
        # and Yelp.]]]
        #
        #if (event.source.role == rolenames.ROLE_MENU) \
        #   and event.source.parent \
        #   and (event.source.parent.role == rolenames.ROLE_MENU_BAR):
        #    return

        # Gecko's combo boxes are a bit of a struggle to work with.
        # First of all, the combo box is a container for a menu.
        # When you arrow up and down in them, the menu item gets
        # focus and then we see name changed events for the menu
        # to represent the name of the menu item that was just
        # selected.  It's all wonderfully convoluted.
        #
        if (event.source.role == rolenames.ROLE_MENU_ITEM):
            parent = event.source.parent
            if parent and (parent.role == rolenames.ROLE_COMBO_BOX):
                orca.setLocusOfFocus(event, parent)
                orca.visualAppearanceChanged(event, parent)
                return
            elif parent and (parent.role == rolenames.ROLE_MENU):
                parent = parent.parent
                if parent and (parent.role == rolenames.ROLE_COMBO_BOX):
                    orca.setLocusOfFocus(event, parent, False)
                    orca.visualAppearanceChanged(event, parent)
                    return

        # Autocomplete widgets are a complex beast as well.  When they
        # get focus, their child (which is an entry) really has focus.
        #
        if event.source.role == rolenames.ROLE_AUTOCOMPLETE:
            entry = _getAutocompleteEntry(event.source)
            orca.setLocusOfFocus(event, entry)
            return

        default.Script.onFocus(self, event)

    # This function is called when a hyperlink is selected - This happens
    # when a link is navigated to using tab/shift-tab
    #
    def onLinkSelected(self, event):
        text = event.source.text
        hypertext = event.source.hypertext
        linkIndex = util.getLinkIndex(event.source, text.caretOffset)

        if linkIndex >= 0:
            link = hypertext.getLink(linkIndex)
            linkText = self.getText(event.source,
                                    link.startIndex,
                                    link.endIndex)
            [string, startOffset, endOffset] = text.getTextAtOffset(
                text.caretOffset,
                atspi.Accessibility.TEXT_BOUNDARY_LINE_START)
            #print "onLinkSelected", event.source.role, string,
            #print "  caretOffset:     ", text.caretOffset
            #print "  line startOffset:", startOffset
            #print "  line endOffset:  ", startOffset
            #print "  caret in line:   ", text.caretOffset - startOffset
            speech.speak(linkText, self.voices[settings.HYPERLINK_VOICE])
        elif text:
            # We'll just assume the whole thing is a link.  This happens
            # in yelp when we navigate the table of contents of something
            # like the Desktop Accessibility Guide.
            #
            linkText = self.getText(event.source, 0, -1)
            speech.speak(linkText, self.voices[settings.HYPERLINK_VOICE])
        else:
            speech.speak(_("link"), self.voices[settings.HYPERLINK_VOICE])

        self.updateBraille(event.source)

    def locusOfFocusChanged(self, event, oldLocusOfFocus, newLocusOfFocus):
        """Called when the visual object with focus changes.

        Arguments:
        - event: if not None, the Event that caused the change
        - oldLocusOfFocus: Accessible that is the old locus of focus
        - newLocusOfFocus: Accessible that is the new locus of focus
        """
        # Don't bother speaking all the information about the HTML
        # container - it's duplicated all over the place.  So, we
        # just speak the role.
        #
        if newLocusOfFocus \
           and newLocusOfFocus.role == rolenames.ROLE_HTML_CONTAINER:
            # We always automatically go back to focus tracking mode when
            # the focus changes.
            #
            if self.flatReviewContext:
                self.toggleFlatReviewMode()
            self.updateBraille(newLocusOfFocus)
            speech.speak(rolenames.getSpeechForRoleName(newLocusOfFocus))
        else:
            default.Script.locusOfFocusChanged(self,
                                               event,
                                               oldLocusOfFocus,
                                               newLocusOfFocus)
            
    ####################################################################
    #                                                                  #
    # Utility Methods                                                  #
    #                                                                  #
    ####################################################################

    def dumpInfo(self, obj):
        """Dumps the parental hierachy info to stdout."""
        
        if obj.parent:
            self.dumpInfo(obj.parent)
            
        print "---"
        print obj, obj.role, obj.accessible.getIndexInParent()
        offset = self.getCharacterOffsetInParent(obj)
        if offset >= 0:
            print "  offset =", offset

    def getContents(self):
        contents = ""
        lastObj = None
        [obj, characterOffset] = self.getCaretContext()
        while obj:
            if obj and obj.state.count(atspi.Accessibility.STATE_SHOWING):
                characterExtents = obj.text.getRangeExtents(
                    characterOffset,
                    characterOffset + 1,
                    0)
                if lastObj and (lastObj != obj):
                    if obj.role == rolenames.ROLE_LIST_ITEM:
                        contents += "\n"                        
                    if lastObj.role == rolenames.ROLE_LINK:
                        contents += ">"
                    elif (lastCharacterExtents[1] < characterExtents[1]):
                        contents += "\n"                        
                    elif obj.role == rolenames.ROLE_TABLE_CELL:
                        parent = obj.parent
                        if parent.table.getColumnAtIndex(obj.index) != 0:
                            contents += " "
                    elif obj.role == rolenames.ROLE_LINK:
                        contents += "<"                        
                contents += self.getCharacter(obj, characterOffset)
                [lastObj, lastCharacterOffset] = [obj, characterOffset]
                lastCharacterExtents = characterExtents
            [obj, characterOffset] = self.getNextInOrder(obj, characterOffset)
        if lastObj and lastObj.role == rolenames.ROLE_LINK:
            contents += ">"
        return contents
        
    def dumpContent(self, inputEvent):
        """Dumps the document frame content to stdout."""        
        print self.getContents()
            
    def oldDumpContent(self, inputEvent, root=None, accumulated="", indent=""):
        """Dumps the document frame content to stdout."""
        
        if not root:
            documentFrame = self.getDocumentFrame()
            if not documentFrame:
                print "COULD NOT FIND DOCUMENT FRAME"
            else:
                print self.oldDumpContent(inputEvent, documentFrame)
            return
            
        if NEWLINE_ROLES.count(root.role) and len(accumulated):
            accumulated += "\n"

        if root.role == rolenames.ROLE_LINK:
            accumulated += "<"

        childIndex = 0

        if root.text:
            text = self.getText(root, 0, -1).decode("UTF-8")
            for characterIndex in range(0, len(text)):
                if text[characterIndex] == EMBEDDED_OBJECT_CHARACTER:
                    child = root.child(childIndex)
                    accumulated = self.dumpContent(inputEvent,
                                                   child,
                                                   accumulated,
                                                   indent + " ")
                    childIndex += 1
                else:
                    accumulated += text[characterIndex]
        else:
            while True:
                if childIndex < root.childCount:
                    accumulated = self.dumpContent(inputEvent,
                                                   root.child(childIndex),
                                                   accumulated,
                                                   indent + " ")
                    childIndex += 1
                else:
                    break

        if root.role == "link":
            accumulated += ">"

        return accumulated
    
    def getDocumentFrame(self):
        """Returns the document frame that holds the content being shown."""

        # [[[TODO: WDW - this is based upon the 12-Oct-2006 implementation
        # that uses the EMBEDS relation on the top level frame as a means
        # to find the document frame.  Future implementations will break
        # this.]]]
        #
        documentFrame = None
        for i in range(0, self.app.childCount):
            child = self.app.child(i)
            if child.role == rolenames.ROLE_FRAME:
                relations = child.relations
                for relation in relations:
                    if relation.getRelationType()  \
                        == atspi.Accessibility.RELATION_EMBEDS:
                        documentFrame = atspi.Accessible.makeAccessible( \
                            relation.getTarget(0))
                        break

        return documentFrame

    def getUnicodeText(self, obj):
        try:
            return obj.unicodeText
        except:
            if obj.text:
                obj.unicodeText = self.getText(obj, 0, -1).decode("UTF-8")
            else:
                obj.unicodeText = None
        return obj.unicodeText
    
    def getCharacterOffsetInParent(self, obj):
        """Returns the character offset of the embedded object
        character for this hyperlink in its parent's accessible text.

        Arguments:
        - obj: an Accessible that should implement the accessible hyperlink
               specialization.

        Returns an integer representing the character offset of the
        embedded object character for this hyperlink in its parent's
        accessible text, or -1 if this object is not a hyperlink.
        """
        
        # [[[TODO: WDW - HACK to handle the fact that
        # hyperlink.startIndex and hyperlink.endIndex is broken in the
        # Gecko a11y implementation.  This will hopefully be fixed.
        # If it is, one should be able to use hyperlink.startIndex.]]]
        #
        try:
            return obj.characterOffsetInParent
        except:
            hyperlink = obj.hyperlink
            if obj.hyperlink:
                index = 0
                text = self.getUnicodeText(obj.parent)
                for offset in range(0, len(text)):
                    if text[offset] == EMBEDDED_OBJECT_CHARACTER:
                        if index == obj.index:
                            obj.characterOffsetInParent = offset
                            break
                        else:
                            index += 1
            else:
                obj.characterOffsetInParent = -1

        return obj.characterOffsetInParent

    def getChildIndex(self, obj, characterOffset):
        try:
            indeces = obj.childrenIndeces
        except:
            obj.childrenIndeces = {}

        try:
            return obj.childrenIndeces[characterOffset]
        except:
            index = -1
            unicodeText = self.getUnicodeText(obj)
            if unicodeText:
                for character in range(0, characterOffset + 1):
                    if unicodeText[character] == EMBEDDED_OBJECT_CHARACTER:
                        index += 1
            obj.childrenIndeces[characterOffset] = index
            
        return obj.childrenIndeces[characterOffset]
    
    def getNextInOrder(self, obj=None, startOffset=-1):
        """Given an object an a character offset, return the next
        caret context following an in order traversal rule.

        Arguments:
        - root: the Accessible to start at.  If None, starts at the
        document frame.
        - startOffset: character position in the object text field
        (if it exists) to start at.  Defaults to -1, which means
        start at the beginning - that is, the next character is the
        first character in the object.

        Returns [obj, characterOffset] or [None, -1]
        
        DETAIL: If an object presents text, it implements the
        accessible text interface.  If an object has children that
        also present text, then the accessible text for the object
        contains one EMBEDDED_OBJECT_CHARACTER for each child, where
        the EMBEDDED_OBJECT_CHARACTER represents the position of the
        child's text in the object and the order of the
        EMBEDDED_OBJECT_CHARACTERs represent the order of the children
        (i.e., the first EMBEDDED_OBJECT_CHARACTER represents child 0,
        the next EMBEDDED_OBJECT_CHARACTER represents child 1, and so
        on.)
        
        So...we keep track of our current position in a page by
        managing a caret context, which is tuple that consists of an
        Accessible object in the document frame and our caret offset
        in that object.
        """

        if not obj:
            obj = self.getDocumentFrame()
            
        if obj.text:
            unicodeText = self.getUnicodeText(obj)
            nextOffset = startOffset + 1
            if nextOffset < len(unicodeText):
                if unicodeText[nextOffset] != EMBEDDED_OBJECT_CHARACTER:
                    return [obj, nextOffset]
                else:
                    return self.getNextInOrder(
                        obj.child(self.getChildIndex(obj, nextOffset)), -1)
        elif obj.childCount:
            return self.getNextInOrder(obj.child(0), -1)
            
        # If we're here, we need to start looking up the tree
        #
        while obj.parent and obj != obj.parent:
            characterOffsetInParent = self.getCharacterOffsetInParent(obj)
            if characterOffsetInParent >= 0:
                return self.getNextInOrder(obj.parent, characterOffsetInParent)
            else:
                index = obj.index + 1
                if index < obj.parent.childCount:
                    return self.getNextInOrder(obj.parent.child(index), -1)
            obj = obj.parent

        return [None, -1]

    def getCaretContext(self):
        try:
            return self.caretContext
        except:
            self.caretContext = self.getNextInOrder()
        return self.caretContext
    
    def getCharacter(self, obj, characterOffset):
        if obj:
            unicodeText = self.getUnicodeText(obj)
            return unicodeText[characterOffset].encode("UTF-8")
        else:
            return None

    def goNextCharacter(self, inputEvent):

        [obj, characterOffset] = self.getCaretContext()
        while obj:
            [obj, characterOffset] = self.getNextInOrder(obj, characterOffset)
            if obj and obj.state.count(atspi.Accessibility.STATE_SHOWING):
                self.caretContext = [obj, characterOffset]
                break
            
        character = self.getCharacter(obj, characterOffset)
        if character:
            print character
        else:
            print "DONE!"
            del self.caretContext
