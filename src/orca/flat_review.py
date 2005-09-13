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

import re

import a11y
import braille
import core
import debug
import eventsynthesizer
import rolenames

# [[[TODO: WDW - HACK Regular expression to split strings on
# whitespace boundaries, which is what we'll use for word dividers
# instead of living at the whim of whomever decided to implement the
# AT-SPI interfaces for their toolkit or app.]]]
#
whitespace_re = re.compile(r'(\s+)', re.DOTALL | re.IGNORECASE | re.M)

class Char:
    """Represents a single char of an Accessibility_Text object."""
    
    def __init__(self,
                 word,
                 index,
                 string,
                 x, y, width, height):
        """Creates a new char.

        Arguments:
        - word: the Word instance this belongs to
        - index: the index of this char in the word
        - string: the actual char
        - x, y, width, height: the extents of this Char on the screen
        """

        self.word = word
        self.string = string
        self.index = index
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    
class Word:
    """Represents a single word of an Accessibility_Text object, or
    the entire name of an Image or Component if the associated object
    does not implement the Accessibility_Text interface.  As a rule of
    thumb, all words derived from an Accessibility_Text interface will
    start with the word and will end with all chars up to the
    beginning of the next word.  That is, whitespace and punctuation
    will usually be tacked on to the end of words."""
    
    def __init__(self,
                 zone,
                 index,
                 string,
                 x, y, width, height):
        """Creates a new Word.

        Arguments:
        - zone: the Zone instance this belongs to
        - index: the index of this word in the Zone
        - string: the actual string
        - x, y, width, height: the extents of this Char on the screen"""
        
        self.zone = zone
        self.index = index
        self.string = string
        self.length = len(string)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
    def __getattr__(self, attr):
        """Used for lazily determining the chars of a word.  We do
        this to reduce the total number of round trip calls to the app,
        and to also spread the round trip calls out over the lifetime
        of a flat review context.

        Arguments:
        - attr: a string indicating the attribute name to retrieve

        Returns the value of the given attribute.
        """
 
        if attr == "chars":
            if isinstance(self.zone, TextZone):
                text = self.zone.accessible.text
                self.chars = []
                i = 0
                while i < self.length:
                    [char, startOffset, endOffset] = text.getTextAtOffset(
                        self.startOffset + i,
                        core.Accessibility.TEXT_BOUNDARY_CHAR)
                    [x, y, width, height] = text.getRangeExtents(
                        startOffset,
                        endOffset,
                        0)                    
                    self.chars.append(Char(self,
                                           i,
                                           char,
                                           x, y, width, height))
                    i += 1
            else:
                self.chars = None
            return self.chars       
        elif attr.startswith('__') and attr.endswith('__'):
            raise AttributeError, attr
        else:
            return self.__dict__[attr]

        
class Zone:
    """Represents text that is a portion of a single horizontal line."""

    def __init__(self,
                 accessible,
                 string,
                 x, y, 
                 width, height):
        """Creates a new Zone, which is a horizontal region of text.

        Arguments:
        - accessible: the Accessible associated with this Zone
        - string: the string being displayed for this Zone
        - extents: x, y, width, height in screen coordinates
        """

        self.accessible = accessible
        self.string = string
        self.length = len(string)
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __getattr__(self, attr):
        """Used for lazily determining the words in a Zone.

        Arguments:
        - attr: a string indicating the attribute name to retrieve

        Returns the value of the given attribute.
        """
 
        if attr == "words":
            self.words = []
            return self.words        
        elif attr.startswith('__') and attr.endswith('__'):
            raise AttributeError, attr
        else:
            return self.__dict__[attr]

    def onSameLine(self, zone):
        """Returns True if this Zone is on the same horiztonal line as
        the given zone."""

        highestBottom = min(self.y + self.height, zone.y + zone.height)
        lowestTop     = max(self.y,               zone.y)

        # If we do overlap, lets see how much.  We'll require a 25% overlap
        # for now...
        #
        if lowestTop < highestBottom:
            overlapAmount = highestBottom - lowestTop
            shortestHeight = min(self.height, zone.height)
            return ((1.0 * overlapAmount) / shortestHeight) > 0.25
        else:
            return False

        
class TextZone(Zone):
    """Represents Accessibility_Text that is a portion of a single
    horizontal line."""

    def __init__(self,
                 accessible,
                 startOffset,
                 string,
                 x, y, 
                 width, height):
        """Creates a new Zone, which is a horizontal region of text.

        Arguments:
        - accessible: the Accessible associated with this Zone
        - startOffset: the index of the char in the Accessibility_Text
                       interface where this Zone starts
        - string: the string being displayed for this Zone
        - extents: x, y, width, height in screen coordinates
        """

        self.accessible = accessible
        self.startOffset = startOffset
        self.string = string
        self.length = len(string)
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # If the accessible for this TextZone is multiline, we will
        # keep track of the next and previous lines.
        #
        self.previousLineZone = None
        self.nextLineZone = None

    def __getattr__(self, attr):
        """Used for lazily determining the words in a Zone.  The words
        will either be all whitespace (interword boundaries) or actual
        words.  To determine if a Word is whitespace, use
        word.string.isspace()

        Arguments:
        - attr: a string indicating the attribute name to retrieve

        Returns the value of the given attribute.
        """
 
        if attr == "words":
            text = self.accessible.text
            self.words = []
            wordIndex = 0
            offset = self.startOffset
            for string in whitespace_re.split(self.string):
                if len(string):
                    endOffset = offset + len(string)
                    [x, y, width, height] = text.getRangeExtents(
                        offset, 
                        endOffset, 
                        0)
                    word = Word(self,
                                wordIndex,
                                string,
                                x, y, width, height)
                    word.startOffset = offset
                    self.words.append(word)
                    wordIndex += 1
                    offset = endOffset
                
            return self.words
        
        elif attr.startswith('__') and attr.endswith('__'):
            raise AttributeError, attr
        else:
            return self.__dict__[attr]


class Line:
    """A Line is a single line across a window and is composed of Zones."""

    def __init__(self,
                 index,
                 zones):
        """Creates a new Line, which is a horizontal region of text.

        Arguments:
        - index: the index of this Line in the window
        - zones: the Zones that make up this line
        """

        self.index = index
        self.zones = zones
        
        bounds = None
        self.string = ""
        for zone in self.zones:
            if bounds is None:
                bounds = [zone.x, zone.y,
                          zone.x + zone.width, zone.y + zone.height]
            else:
                bounds[0] = min(bounds[0], zone.x)
                bounds[1] = min(bounds[1], zone.y)
                bounds[2] = max(bounds[2], zone.x + zone.width)
                bounds[3] = max(bounds[3], zone.y + zone.height)
            if len(zone.string):
                if len(self.string):
                    self.string += " "
                self.string += zone.string
                
        if bounds is None:
            bounds = [-1, -1, -1, -1]

        self.x = bounds[0]
        self.y = bounds[1]
        self.width = bounds[2] - bounds[0]
        self.height = bounds[3] - bounds[1]

    
class Context:
    """Information regarding where a user happens to be exploring
    right now.
    """

    ZONE   = 0
    CHAR   = 1
    WORD   = 2
    LINE   = 3 # includes all zones on same line
    WINDOW = 4

    WRAP_LINE       = 1 << 0
    WRAP_TOP_BOTTOM = 1 << 1
    WRAP_ALL        = (WRAP_LINE | WRAP_TOP_BOTTOM)
    
    def __init__(self, lines, lineIndex, zoneIndex, wordIndex, charIndex):
        """Create a new Context that will be used for handling flat
        review mode.

        Arguments:
        - lines: an array of arrays of Zones (see clusterZonesByLine)
        - lineIndex: index into lines
        - zoneIndex: index into lines[lineIndex].zones
        - wordIndex: index into lines[lineIndex].zones[zoneIndex].words
        - charIndex: index lines[lineIndex].zones[zoneIndex].words[wordIndex].chars
        """

        self.lines     = lines
        self.lineIndex = lineIndex
        self.zoneIndex = zoneIndex
        self.wordIndex = wordIndex
        self.charIndex = charIndex

        # This is used to tell us where we should strive to move to
        # when going up and down lines to the closest character.
        # The targetChar is the character where we initially started
        # moving from, and does not change when one moves up or down
        # by line.
        #
        self.targetCharInfo = None
        

    def _dumpCurrentState(self):
        print "line=%d, zone=%d, word=%d, char=%d" \
              % (self.lineIndex,
                 self.zoneIndex,
                 self.wordIndex,
                 self.zoneIndex)

        zone = self.lines[self.lineIndex].zones[self.zoneIndex]
        text = zone.accessible.text

        if text is None:
            print "  Not Accessibility_Text"
            return

        print "  getTextBeforeOffset: %d" % text.caretOffset        
        [string, startOffset, endOffset] = text.getTextBeforeOffset(
            text.caretOffset,
            core.Accessibility.TEXT_BOUNDARY_WORD_START)
        print "    WORD_START: start=%d end=%d string='%s'" \
              % (startOffset, endOffset, string)
        [string, startOffset, endOffset] = text.getTextBeforeOffset(
            text.caretOffset,
            core.Accessibility.TEXT_BOUNDARY_WORD_END)
        print "    WORD_END:   start=%d end=%d string='%s'" \
              % (startOffset, endOffset, string)

        print "  getTextAtOffset: %d" % text.caretOffset        
        [string, startOffset, endOffset] = text.getTextAtOffset(
            text.caretOffset,
            core.Accessibility.TEXT_BOUNDARY_WORD_START)
        print "    WORD_START: start=%d end=%d string='%s'" \
              % (startOffset, endOffset, string)
        [string, startOffset, endOffset] = text.getTextAtOffset(
            text.caretOffset,
            core.Accessibility.TEXT_BOUNDARY_WORD_END)
        print "    WORD_END:   start=%d end=%d string='%s'" \
              % (startOffset, endOffset, string)

        print "  getTextAfterOffset: %d" % text.caretOffset        
        [string, startOffset, endOffset] = text.getTextAfterOffset(
            text.caretOffset,
            core.Accessibility.TEXT_BOUNDARY_WORD_START)
        print "    WORD_START: start=%d end=%d string='%s'" \
              % (startOffset, endOffset, string)
        [string, startOffset, endOffset] = text.getTextAfterOffset(
            text.caretOffset,
            core.Accessibility.TEXT_BOUNDARY_WORD_END)
        print "    WORD_END:   start=%d end=%d string='%s'" \
              % (startOffset, endOffset, string)
        

    def clickCurrent(self, button=1):
        """Performs a mouse click on the current accessible."""

        if (not self.lines) \
           or (not self.lines[self.lineIndex].zones):
            return

        [string, x, y, width, height] = self.getCurrent(Context.CHAR)
        try:

            # We try to click to the left of center.  This is to
            # handle toolkits that will offset the caret position to
            # the right if you click dead on center of a character.
            #
            # [[[TODO: WDW - probably need to go the other way for
            # locales that read right to left.]]]
            #
            eventsynthesizer.clickPoint(x,
                                        y + height/ 2,
                                        button)
        except:
            debug.printException(debug.LEVEL_SEVERE)
        
        
    def getCurrent(self, type=ZONE):
        """Gets the string, offset, and extent information for the
        current locus of interest.

        Arguments:
        - type: one of ZONE, CHAR, WORD, LINE

        Returns: [string, x, y, width, height]
        """

        if (not self.lines) \
           or (not self.lines[self.lineIndex].zones):
            return

        zone = self.lines[self.lineIndex].zones[self.zoneIndex]
            
        if type == Context.ZONE:
            return [zone.string,
                    zone.x,
                    zone.y,
                    zone.width,
                    zone.height]
        elif type == Context.CHAR:
            if isinstance(zone, TextZone):
                text = zone.accessible.text
                words = zone.words
                if words:
                    chars = zone.words[self.wordIndex].chars
                    if chars:
                        char = chars[self.charIndex]
                        return [char.string,
                                char.x,
                                char.y,
                                char.width,
                                char.height]
                    else:
                        word = words[self.wordIndex]
                        return [word.string,
                                word.x,
                                word.y,
                                word.width,
                                word.height]
            return self.getCurrent(Context.ZONE)
        elif type == Context.WORD:
            if isinstance(zone, TextZone):
                text = zone.accessible.text
                words = zone.words
                if words:
                    word = words[self.wordIndex]
                    return [word.string,
                            word.x,
                            word.y,
                            word.width,
                            word.height]
            return self.getCurrent(Context.ZONE)
        elif type == Context.LINE:
            line = self.lines[self.lineIndex]
            return [line.string,
                    line.x,
                    line.y,
                    line.width,
                    line.height]
        else:
            raise Error, "Invalid type: %d" % type


    def getCurrentBrailleRegions(self):
        """Gets the braille for the entire current line.

        Returns [regions, regionWithFocus]
        """

        regions = []
        focusedRegion = None
        
        if (not self.lines) \
           or (not self.lines[self.lineIndex].zones):
            return [regions, focusedRegion]

        line = self.lines[self.lineIndex]

        zoneIndex = 0
        wordIndex = 0
        charIndex = 0
        while zoneIndex < len(line.zones):
            zone = line.zones[zoneIndex]
            if (zone.accessible.role == rolenames.ROLE_TEXT) \
               or (zone.accessible.role == rolenames.ROLE_PASSWORD_TEXT) \
               or (zone.accessible.role == rolenames.ROLE_TERMINAL):
                region = braille.ReviewText(zone.accessible,
                                            zone.string,
                                            zone.startOffset)
            else:
                region = braille.Component(zone.accessible, zone.string)
                
            if len(regions):
                regions.append(braille.Region(" "))
            regions.append(region)

            # We might have the object of interest.
            # If so, we need to convert the current
            # character index into an offset into the
            # string for this zone.
            #
            if zoneIndex == self.zoneIndex:
                regionWithFocus = region
                regionWithFocus.cursorOffset = 0
                if zone.words:
                    wordIndex = 0
                    while wordIndex < self.wordIndex:
                        regionWithFocus.cursorOffset += \
                            len(zone.words[wordIndex].string)
                        wordIndex += 1
                regionWithFocus.cursorOffset += self.charIndex
            zoneIndex += 1

        return [regions, regionWithFocus]

    
    def goBegin(self, type=WINDOW):
        """Moves this context's locus of interest to the first char
        of the first relevant zone.

        Arguments:
        - type: one of LINE or WINDOW
        
        Returns True if the locus of interest actually changed.
        """

        if type == Context.LINE:
            lineIndex = self.lineIndex
        elif type == Context.WINDOW:
            lineIndex = 0
        else:
            raise Error, "Invalid type: %d" % type
            
        zoneIndex = 0
        wordIndex = 0
        charIndex = 0

        moved = (self.lineIndex != lineIndex) \
                or (self.zoneIndex != zoneIndex) \
                or (self.wordIndex != wordIndex) \
                or (self.charIndex != charIndex) \

        if moved:
            self.lineIndex = lineIndex
            self.zoneIndex = zoneIndex
            self.wordIndex = wordIndex
            self.charIndex = charIndex
            self.targetCharInfo = self.getCurrent(Context.CHAR) 
        
        return moved

    
    def goEnd(self, type=WINDOW):
        """Moves this context's locus of interest to the last char
        of the last relevant zone.

        Arguments:
        - type: one of ZONE, LINE, or WINDOW
        
        Returns True if the locus of interest actually changed.
        """

        if type == Context.LINE:
            lineIndex = self.lineIndex
        elif type == Context.WINDOW:
            lineIndex  = len(self.lines) - 1
        else:
            raise Error, "Invalid type: %d" % type

        zoneIndex = len(self.lines[lineIndex].zones) - 1
        zone = self.lines[lineIndex].zones[zoneIndex]
        if zone.words:
            wordIndex = len(zone.words) - 1
            chars = zone.words[wordIndex].chars
            if chars:
                charIndex = len(chars) - 1
            else:
                charIndex = 0
        else:
            wordIndex = 0
            charIndex = 0

        moved = (self.lineIndex != lineIndex) \
                or (self.zoneIndex != zoneIndex) \
                or (self.wordIndex != wordIndex) \
                or (self.charIndex != charIndex) \

        if moved:
            self.lineIndex = lineIndex
            self.zoneIndex = zoneIndex
            self.wordIndex = wordIndex
            self.charIndex = charIndex
            self.targetCharInfo = self.getCurrent(Context.CHAR) 
        
        return moved

        
    def goPrevious(self, type=ZONE, wrap=WRAP_ALL, omitWhitespace=True):
        """Moves this context's locus of interest to the first char
        of the previous type.

        Arguments:
        - type: one of ZONE, CHAR, WORD, LINE
        - wrap: if True, will cross boundaries, including top and
                bottom; if False, will stop on boundaries.                

        Returns True if the locus of interest actually changed.
        """

        moved = False

        if type == Context.ZONE:
            if self.zoneIndex > 0:
                self.zoneIndex -= 1
                self.wordIndex = 0
                self.charIndex = 0
                moved = True
            elif wrap & Context.WRAP_LINE:
                if self.lineIndex > 0:
                    self.lineIndex -= 1
                    self.zoneIndex = len(self.lines[self.lineIndex].zones) - 1
                    self.wordIndex = 0
                    self.charIndex = 0
                    moved = True
                elif wrap & Context.WRAP_TOP_BOTTOM:
                    self.lineIndex = len(self.lines) - 1
                    self.zoneIndex = len(self.lines[self.lineIndex].zones) - 1
                    self.wordIndex = 0
                    self.charIndex = 0
                    moved = True
        elif type == Context.CHAR:
            if self.charIndex > 0:
                self.charIndex -= 1
                moved = True
            else:
                moved = self.goPrevious(Context.WORD, wrap, False)
                if moved:
                    zone = self.lines[self.lineIndex].zones[self.zoneIndex]
                    if zone.words:
                        chars = zone.words[self.wordIndex].chars
                        if chars:
                            self.charIndex = len(chars) - 1
        elif type == Context.WORD:
            zone = self.lines[self.lineIndex].zones[self.zoneIndex]
            accessible = zone.accessible
            lineIndex = self.lineIndex
            zoneIndex = self.zoneIndex
            wordIndex = self.wordIndex
            charIndex = self.charIndex

            if self.wordIndex > 0:
                self.wordIndex -= 1
                self.charIndex = 0
                moved = True
            else:
                moved = self.goPrevious(Context.ZONE, wrap)
                if moved:
                    zone = self.lines[self.lineIndex].zones[self.zoneIndex]
                    if zone.words:
                        self.wordIndex = len(zone.words) - 1

            # If we landed on a whitespace word or something with no words,
            # we might need to move some more.
            #
            zone = self.lines[self.lineIndex].zones[self.zoneIndex]
            if omitWhitespace \
               and moved \
               and ((len(zone.words) == 0) \
                    or zone.words[self.wordIndex].string.isspace()):

                # If we're on whitespace in the same zone, then let's
                # try to move on.  If not, we've definitely moved
                # across accessibles.  If that's the case, let's try
                # to find the first 'real' word in the accessible.
                # If we cannot, then we're just stuck on an accessible
                # with no words and we should do our best to announce
                # this to the user (e.g., "whitespace" or "blank").
                #
                if zone.accessible == accessible:
                    moved = self.goPrevious(Context.WORD, wrap)
                else:
                    wordIndex = self.wordIndex - 1
                    while wordIndex >= 0:
                        if (zone.words[wordIndex].string is None) \
                            or not len(zone.words[wordIndex].string) \
                            or zone.words[wordIndex].string.isspace():
                            wordIndex -= 1
                        else:
                            break
                    if wordIndex >= 0:
                        self.wordIndex = wordIndex

            if not moved:
                self.lineIndex = lineIndex
                self.zoneIndex = zoneIndex
                self.wordIndex = wordIndex
                self.charIndex = charIndex
 
        elif type == Context.LINE:
            if wrap & Context.WRAP_LINE:
                if self.lineIndex > 0:
                    self.lineIndex -= 1
                    self.zoneIndex = 0
                    self.wordIndex = 0
                    self.charIndex = 0
                    moved = True
                elif (wrap & Context.WRAP_TOP_BOTTOM) \
                     and (len(lines) != 1):
                    self.lineIndex = len(self.lines) - 1
                    self.zoneIndex = 0
                    self.wordIndex = 0
                    self.charIndex = 0
                    moved = True
        else:
            raise Error, "Invalid type: %d" % type

        if moved and (type != Context.LINE):
            self.targetCharInfo = self.getCurrent(Context.CHAR) 
            
        return moved


    def goNext(self, type=ZONE, wrap=WRAP_ALL, omitWhitespace=True):
        """Moves this context's locus of interest to first char of
        the next type.

        Arguments:
        - type: one of ZONE, CHAR, WORD, LINE
        - wrap: if True, will cross boundaries, including top and
                bottom; if False, will stop on boundaries.
        """

        moved = False
        
        if type == Context.ZONE:
            if self.zoneIndex < (len(self.lines[self.lineIndex].zones) - 1):
                self.zoneIndex += 1
                self.wordIndex = 0
                self.charIndex = 0
                moved = True
            elif wrap & Context.WRAP_LINE:
                if self.lineIndex < (len(self.lines) - 1):
                    self.lineIndex += 1
                    self.zoneIndex  = 0
                    self.wordIndex = 0
                    self.charIndex = 0
                    moved = True
                elif wrap & Context.WRAP_TOP_BOTTOM:
                    self.lineIndex  = 0
                    self.zoneIndex  = 0
                    self.wordIndex = 0
                    self.charIndex = 0
                    moved = True
        elif type == Context.CHAR:
            zone = self.lines[self.lineIndex].zones[self.zoneIndex]
            if zone.words:
                chars = zone.words[self.wordIndex].chars
                if chars:
                    if self.charIndex < (len(chars) - 1):
                        self.charIndex += 1
                        moved = True
                    else:
                        moved = self.goNext(Context.WORD, wrap, False)
                else:
                    moved = self.goNext(Context.WORD, wrap)
            else:
                moved = self.goNext(Context.ZONE, wrap)
        elif type == Context.WORD:
            zone = self.lines[self.lineIndex].zones[self.zoneIndex]
            accessible = zone.accessible
            lineIndex = self.lineIndex
            zoneIndex = self.zoneIndex
            wordIndex = self.wordIndex
            charIndex = self.charIndex
            
            if zone.words:
                if self.wordIndex < (len(zone.words) - 1):
                    self.wordIndex += 1
                    self.charIndex = 0
                    moved = True
                else:
                    moved = self.goNext(Context.ZONE, wrap)
            else:
                moved = self.goNext(Context.ZONE, wrap)

            # If we landed on a whitespace word or something with no words,
            # we might need to move some more.
            #
            zone = self.lines[self.lineIndex].zones[self.zoneIndex]
            if omitWhitespace \
               and moved \
               and ((len(zone.words) == 0) \
                    or zone.words[self.wordIndex].string.isspace()):

                # If we're on whitespace in the same zone, then let's
                # try to move on.  If not, we've definitely moved
                # across accessibles.  If that's the case, let's try
                # to find the first 'real' word in the accessible.
                # If we cannot, then we're just stuck on an accessible
                # with no words and we should do our best to announce
                # this to the user (e.g., "whitespace" or "blank").
                #
                if zone.accessible == accessible:
                    moved = self.goNext(Context.WORD, wrap)
                else:
                    wordIndex = self.wordIndex + 1
                    while wordIndex < len(zone.words):
                        if (zone.words[wordIndex].string is None) \
                            or not len(zone.words[wordIndex].string) \
                            or zone.words[wordIndex].string.isspace():
                            wordIndex += 1
                        else:
                            break
                    if wordIndex < len(zone.words):
                        self.wordIndex = wordIndex
                        
            if not moved:
                self.lineIndex = lineIndex
                self.zoneIndex = zoneIndex
                self.wordIndex = wordIndex
                self.charIndex = charIndex
                
        elif type == Context.LINE:
            if wrap & Context.WRAP_LINE:
                if self.lineIndex < (len(self.lines) - 1):
                    self.lineIndex += 1
                    self.zoneIndex = 0
                    self.wordIndex = 0
                    self.charIndex = 0
                    moved = True
                elif (wrap & Context.WRAP_TOP_BOTTOM) \
                     and (self.lineIndex != 0):
                        self.lineIndex = 0
                        self.zoneIndex = 0
                        self.wordIndex = 0
                        self.charIndex = 0
                        moved = True
        else:
            raise Error, "Invalid type: %d" % type

        if moved and (type != Context.LINE):
            self.targetCharInfo = self.getCurrent(Context.CHAR) 
            
        return moved
    

    def goAbove(self, type=LINE, wrap=WRAP_ALL):
        """Moves this context's locus of interest to first char
        of the type that's closest to and above the current locus of
        interest.

        Arguments:
        - type: LINE
        - wrap: if True, will cross top/bottom boundaries; if False, will
                stop on top/bottom boundaries.

        Returns: [string, startOffset, endOffset, x, y, width, height]
        """

        moved = False
        if type == Context.CHAR:
            # We want to shoot for the closest character, which we've
            # saved away as self.targetCharInfo, which is the list
            # [string, x, y, width, height].
            #
            if self.targetCharInfo is None:
                self.targetCharInfo = self.getCurrent(Context.CHAR)
            target = self.targetCharInfo
            leftTargetX = target[1]              # x
            rightTargetX = target[1] + target[3] # x + width
            
            moved = self.goPrevious(Context.LINE, wrap)
            if moved:
                while True:
                    [string, bx, by, bwidth, bheight] = \
                             self.getCurrent(Context.CHAR)
                    leftMostRightEdge = min(rightTargetX, bx + bwidth)
                    rightMostLeftEdge = max(leftMostRightEdge, bx)
                    if (rightMostLeftEdge < leftMostRightEdge) \
                       or (bx >= rightTargetX):
                        break
                    elif not self.goNext(Context.CHAR, 0):
                        break

            # Moving around might have reset the current targetCharInfo,
            # so we reset it to our saved value.
            #
            self.targetCharInfo = target
        elif type == Context.LINE:
            return goPrevious(type, wrap)
        else:
            raise Error, "Invalid type: %d" % type

        return moved


    def goBelow(self, type=LINE, wrap=WRAP_ALL):
        """Moves this context's locus of interest to the first
        char of the type that's closest to and below the current
        locus of interest.

        Arguments:
        - type: one of WORD, LINE
        - wrap: if True, will cross top/bottom boundaries; if False, will
                stop on top/bottom boundaries.

        Returns: [string, startOffset, endOffset, x, y, width, height]
        """

        moved = False
        if type == Context.CHAR:
            # We want to shoot for the closest character, which we've
            # saved away as self.targetCharInfo, which is the list
            # [string, x, y, width, height].
            #
            if self.targetCharInfo is None:
                self.targetCharInfo = self.getCurrent(Context.CHAR)
            target = self.targetCharInfo
            leftTargetX = target[1]              # x
            rightTargetX = target[1] + target[3] # x + width
            
            moved = self.goNext(Context.LINE, wrap)
            if moved:
                while True:
                    [string, bx, by, bwidth, bheight] = \
                             self.getCurrent(Context.CHAR)
                    leftMostRightEdge = min(rightTargetX, bx + bwidth)
                    rightMostLeftEdge = max(leftTargetX, bx)
                    if (rightMostLeftEdge < leftMostRightEdge) \
                       or (bx >= rightTargetX):
                        break
                    elif not self.goNext(Context.CHAR, 0):
                        break

            # Moving around might have reset the current targetCharInfo,
            # so we reset it to our saved value.
            #
            self.targetCharInfo = target
        elif type == Context.LINE:
            moved = goNext(type, wrap)
        else:
            raise Error, "Invalid type: %d" % type

        return moved

    
def visible(ax, ay, awidth, aheight,
            bx, by, bwidth, bheight):
    """Returns true if any portion of region 'a' is in region 'b'
    """
    highestBottom = min(ay + aheight, by + bheight)    
    lowestTop = max(ay, by)

    leftMostRightEdge = min(ax + awidth, bx + bwidth)
    rightMostLeftEdge = max(ax, bx)

    if (lowestTop < highestBottom) \
       and (rightMostLeftEdge < leftMostRightEdge):
        return True
    elif (aheight == 0):
        if (awidth == 0):
            return (lowestTop == highestBottom) \
                   and (leftMostRightEdge == rightMostLeftEdge)
        else:
            return leftMostRightEdge < rightMostLeftEdge
    elif (awidth == 0):
        return (lowestTop < highestBottom)

        
def clip(ax, ay, awidth, aheight,
         bx, by, bwidth, bheight):
    """Clips region 'a' by region 'b' and returns the new region as
    a list: [x, y, width, height].
    """
    
    x = max(ax, bx)
    x2 = min(ax + awidth, bx + bwidth)
    width = x2 - x
    
    y = max(ay, by)
    y2 = min(ay + aheight, by + bheight)
    height = y2 - y
    
    return [x, y, width, height]


def getZonesFromAccessible(accessible, cliprect):
    """Returns a list of Zones for the given accessible.

    Arguments:
    - accessible: the accessible
    - cliprect: the extents that the Zones must fit inside.    
    """

    # Get the component extents in screen coordinates.
    #
    extents = accessible.component.getExtents(0)
    
    if not visible(extents.x, extents.y, 
                   extents.width, extents.height,
                   cliprect.x, cliprect.y,
                   cliprect.width, cliprect.height):
        return []
    
    zones = []

    # Now see if there is any accessible text.  If so, find new zones,
    # where each zone represents a line of this text object.  When
    # creating the zone, only keep track of the text that is actually
    # showing on the screen.
    #
    if accessible.text:
        text = accessible.text
        length = text.characterCount

        offset = 0
        while offset < length:
            
            [string, startOffset, endOffset] = text.getTextAtOffset(
                offset,
                core.Accessibility.TEXT_BOUNDARY_LINE_START)

            [x, y, width, height] = text.getRangeExtents(startOffset, 
                                                         endOffset, 
                                                         0)

            offset = endOffset
            previousLineZone = None
            
            if visible(x, y, width, height, 
                       cliprect.x, cliprect.y, 
                       cliprect.width, cliprect.height):
                   
                clipping = clip(x, y, width, height,
                                cliprect.x, cliprect.y,
                                cliprect.width, cliprect.height)

		# [[[TODO: WDW - HACK it would be nice to clip the
                # the text by what is really showing on the screen,
                # but this seems to hang Orca and the client.]]]
		#
                #ranges = text.getBoundedRanges(\
                #    clipping[0],
                #    clipping[1],
                #    clipping[2],
                #    clipping[3],
                #    0,
                #    core.Accessibility.TEXT_CLIP_BOTH,
                #    core.Accessibility.TEXT_CLIP_BOTH)
                #
                #print
                #print "HERE!"
                #for range in ranges:
                #    print range.startOffset
                #    print range.endOffset
                #    print range.content
                                                                   
                zone = TextZone(accessible,
                                startOffset,
                                string, 
                                clipping[0],
                                clipping[1],
                                clipping[2],
                                clipping[3])

                if previousLineZone:
                    previousLineZone.nextLineZone = zone
                zone.previousLineZone = previousLineZone
                zone.nextLineZone = None
                
                zones.append(zone)

                previousLineZone = zone
                
            elif len(zones):
                # We'll break out of searching all the text - the idea
                # here is that we'll at least try to optimize for when
                # we gone below the visible clipping area.
                #
                # [[[TODO: WDW - would be nice to optimize this better.
                # for example, perhaps we can assume the caret will always
                # be visible, and we can start our text search from there.]]]
                #
                break
        
        # We might have a zero length text area.  In that case, well,
        # lets hack...
        #
        if len(zones) == 0:
            if (accessible.role == rolenames.ROLE_TEXT) \
               or ((accessible.role == rolenames.ROLE_PASSWORD_TEXT)):
                zones.append(TextZone(accessible,
                                      0,
                                      "",
                                      extents.x, extents.y,
                                      extents.width, extents.height))

    # We really want the accessible text information.  But, if we have
    # an image, and it has a description, we can fall back on it.
    #
    if (len(zones) == 0) \
           and accessible.image \
           and accessible.image.imageDescription \
           and len(accessible.image.imageDescription):
        
        [x, y] = accessible.image.getImagePosition(0)
        [width, height] = accessible.image.getImageSize()
        
        if (width != 0) and (height != 0) \
               and visible(x, y, width, height,
                           cliprect.x, cliprect.y, 
                           cliprect.width, cliprect.height):
                   
            clipping = clip(x, y, width, height,
                            cliprect.x, cliprect.y,
                            cliprect.width, cliprect.height)

            if (clipping[2] != 0) or (clipping[3] != 0):
                zones.append(Zone(accessible, 
                                  accessible.image.imageDescription, 
                                  clipping[0],
                                  clipping[1],
                                  clipping[2],
                                  clipping[3]))

    # Well...darn.  Maybe we didn't get anything of use, but we certainly
    # know there's something there.  If that's the case, we'll just use
    # the component extents and the name or description of the accessible.
    #
    if len(zones) == 0:
        clipping = clip(extents.x, extents.y,
                        extents.width, extents.height,
                        cliprect.x, cliprect.y,
                        cliprect.width, cliprect.height)
        if accessible.name and len(accessible.name):
            string = accessible.name
        elif accessible.description and len(accessible.description):
            string = accessible.description
        else:
            string = ""
            
        if (clipping[2] != 0) or (clipping[3] != 0):
            zones.append(Zone(accessible,
                              string,
                              clipping[0],
                              clipping[1],
                              clipping[2],
                              clipping[3]))
    
    return zones


def getShowingZones(root):
    """Returns a list of all interesting, non-intersecting, regions
    that are drawn on the screen.  Each element of the list is the
    Accessible object associated with a given region.  The term
    'zone' here is inherited from OCR algorithms and techniques.
    
    The Zones are returned in no particular order.

    Arguments:
    - root: the Accessible object to traverse

    Returns: a list of Zones under the specified object
    """

    if root is None:
        return []
    
    # If we're at a leaf node, then we've got a good one on our hands.
    #
    if root.childCount <= 0:
        return getZonesFromAccessible(root, root.extents)

    # We'll stop at various objects because, while they do have
    # children, we logically think of them as one region on the
    # screen.  [[[TODO: WDW - HACK stopping at menu bars for now
    # because their menu items tell us they are showing even though
    # they are not showing.  Until I can figure out a reliable way to
    # get past these lies, I'm going to ignore them.]]]
    #
    if (root.parent and (root.parent.role == rolenames.ROLE_MENU_BAR)) \
       or (root.role == rolenames.ROLE_COMBO_BOX):
        return getZonesFromAccessible(root, root.extents)
    
    # Otherwise, dig deeper.
    #
    objlist = []

    # We'll include page tabs: while they are parents, their extents do
    # not contain their children.
    #
    if root.role == rolenames.ROLE_PAGE_TAB:
        objlist.extend(getZonesFromAccessible(root, root.extents))
        
    # [[[TODO: WDW - probably want to do something a little smarter
    # for parents that manage gazillions of descendants.]]]
    #
    i = 0
    while i < root.childCount:
        child = root.child(i)
        if child == root:
            debug.println(debug.LEVEL_SEVERE,
                          indent + "  " + "WARNING CHILD == PARENT!!!")
        elif child is None:
            debug.println(debug.LEVEL_SEVERE,
                          indent + "  " + "WARNING CHILD IS NONE!!!")
        elif child.parent != root:
            debug.println(debug.LEVEL_SEVERE,
                          indent + "  " + "WARNING CHILD.PARENT != PARENT!!!")
        elif child.state.count(core.Accessibility.STATE_SHOWING):    
            objlist.extend(getShowingZones(child))
        i += 1
        
    return objlist


def clusterZonesByLine(zones):
    """Given a list of interesting accessible objects (the Zones),
    returns a list of lines in order from the top to bottom, where
    each line is a list of accessible objects in order from left
    to right.
    """
    
    if len(zones) == 0:
        return []

    # Sort the zones and also find the top most zone - we'll bias
    # the clustering to the top of the window.  That is, if an
    # object can be part of multiple clusters, for now it will
    # become a part of the top most cluster.
    #
    numZones = len(zones)
    i = 0
    while i < numZones:
        j = 0
        while j < (numZones - 1 - i):
            a = zones[j]
            b = zones[j + 1]
            if b.y < a.y:
                zones[j] = b
                zones[j + 1] = a
            j += 1
        i += 1

    # Now we cluster the zones.  We create the clusters on the
    # fly, adding a zone to an existing cluster only if it's
    # rectangle horizontally overlaps all other zones in the
    # cluster.
    #
    lineClusters = []
    for clusterCandidate in zones:
        addedToCluster = False
        for lineCluster in lineClusters:
            inCluster = True
            for zone in lineCluster:
                if not zone.onSameLine(clusterCandidate):
                    inCluster = False
                    break
            if inCluster:
                # Add to cluster based on the x position.
                #
                i = 0
                while i < len(lineCluster):
                    zone = lineCluster[i]
                    if clusterCandidate.x < zone.x:
                        break
                    i += 1
                lineCluster.insert(i, clusterCandidate)
                addedToCluster = True
                break                
        if not addedToCluster:
            lineClusters.append([clusterCandidate])

    # Now, adjust all the indeces.
    #
    lines = []
    lineIndex = 0
    for lineCluster in lineClusters:
        lines.append(Line(lineIndex, lineCluster))
        zoneIndex = 0
        for zone in lineCluster:
            zone.line = lines[lineIndex]
            zone.index = zoneIndex
            zoneIndex += 1
        lineIndex += 1
        
    return lines
