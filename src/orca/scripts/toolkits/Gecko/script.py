# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
# Copyright 2010 Orca Team.
# Copyright 2014-2015 Igalia, S.L.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

# [[[TODO: WDW - Pylint is giving us a bunch of errors along these
# lines throughout this file:
#
# E1103:4241:Script.updateBraille: Instance of 'list' has no 'getRole'
# member (but some types could not be inferred)
#
# I don't know what is going on, so I'm going to tell pylint to
# disable those messages for Gecko.py.]]]
#
# pylint: disable-msg=E1103

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc." \
                "Copyright (c) 2010 Orca Team." \
                "Copyright (c) 2014-2015 Igalia, S.L."
__license__   = "LGPL"

from gi.repository import Gtk
import pyatspi
import time
import urllib.parse

import orca.braille as braille
import orca.cmdnames as cmdnames
import orca.debug as debug
import orca.scripts.default as default
import orca.eventsynthesizer as eventsynthesizer
import orca.guilabels as guilabels
import orca.input_event as input_event
import orca.keybindings as keybindings
import orca.liveregions as liveregions
import orca.messages as messages
import orca.object_properties as object_properties
import orca.orca as orca
import orca.orca_state as orca_state
import orca.settings as settings
import orca.settings_manager as settings_manager
import orca.speech as speech
import orca.speechserver as speechserver

from . import keymaps
from .braille_generator import BrailleGenerator
from .speech_generator import SpeechGenerator
from .formatting import Formatting
from .bookmarks import GeckoBookmarks
from .structural_navigation import GeckoStructuralNavigation
from .script_utilities import Utilities
from .tutorial_generator import TutorialGenerator

from orca.orca_i18n import _
from orca.speech_generator import Pause
from orca.acss import ACSS

_settingsManager = settings_manager.getManager()

########################################################################
#                                                                      #
# Script                                                               #
#                                                                      #
########################################################################

class Script(default.Script):
    """The script for Firefox."""

    ####################################################################
    #                                                                  #
    # Overridden Script Methods                                        #
    #                                                                  #
    ####################################################################

    def __init__(self, app):
        default.Script.__init__(self, app)
        # Initialize variables to make pylint happy.
        #
        self.changedLinesOnlyCheckButton = None
        self.controlCaretNavigationCheckButton = None
        self.minimumFindLengthAdjustment = None
        self.minimumFindLengthLabel = None
        self.minimumFindLengthSpinButton = None
        self.sayAllOnLoadCheckButton = None
        self.skipBlankCellsCheckButton = None
        self.speakCellCoordinatesCheckButton = None
        self.speakCellHeadersCheckButton = None
        self.speakCellSpanCheckButton = None
        self.speakResultsDuringFindCheckButton = None
        self.structuralNavigationCheckButton = None
        self.autoFocusModeStructNavCheckButton = None
        self.autoFocusModeCaretNavCheckButton = None
        self.layoutModeCheckButton = None

        # _caretNavigationFunctions are functions that represent fundamental
        # ways to move the caret (e.g., by the arrow keys).
        #
        self._caretNavigationFunctions = \
            [Script.goNextCharacter,
             Script.goPreviousCharacter,
             Script.goNextWord,
             Script.goPreviousWord,
             Script.goNextLine,
             Script.goPreviousLine,
             Script.goTopOfFile,
             Script.goBottomOfFile,
             Script.goBeginningOfLine,
             Script.goEndOfLine]

        self._liveRegionFunctions = \
            [Script.setLivePolitenessOff,
             Script.advanceLivePoliteness,
             Script.monitorLiveRegions,
             Script.reviewLiveAnnouncement]

        if _settingsManager.getSetting('caretNavigationEnabled') == None:
            _settingsManager.setSetting('caretNavigationEnabled', True)
        if _settingsManager.getSetting('sayAllOnLoad') == None:
            _settingsManager.setSetting('sayAllOnLoad', True)

        # We keep track of whether we're currently in the process of
        # loading a page.
        #
        self._loadingDocumentContent = False

        # In tabbed content (i.e., Firefox's support for one tab per
        # URL), we also keep track of the caret context in each tab.
        # the key is the document frame and the value is the caret
        # context for that frame.
        #
        self._documentFrameCaretContext = {}

        # During a find we get caret-moved events reflecting the changing
        # screen contents.  The user can opt to have these changes announced.
        # If the announcement is enabled, it still only will be made if the
        # selected text is a certain length (user-configurable) and if the
        # line has changed (so we don't keep repeating the line).  However,
        # the line has almost certainly changed prior to this length being
        # reached.  Therefore, we need to make an initial announcement, which
        # means we need to know if that has already taken place.
        #
        self.madeFindAnnouncement = False

        # Create the live region manager and start the message manager
        self.liveMngr = liveregions.LiveRegionManager(self)

        # We want to keep track of the line contents we just got so that
        # we can speak and braille this information without having to call
        # getLineContentsAtOffset() twice.
        #
        self.currentLineContents = []

        # For really large objects, a call to getAttributes can take up to
        # two seconds! This is a Firefox bug. We'll try to improve things
        # by storing attributes.
        #
        self.currentAttrs = {}

        # A dictionary of Gecko-style attribute names and their equivalent/
        # expected names. This is necessary so that we can present the
        # attributes to the user in a consistent fashion across apps and
        # toolkits. Note that underlinesolid and line-throughsolid are
        # temporary fixes: text_attribute_names.py assumes a one-to-one
        # correspondence. This is not a problem when going from attribute
        # name to localized name; in the reverse direction, we need more
        # context (i.e. we can't safely make them both be "solid"). A
        # similar issue exists with "start" which means no justification
        # has explicitly been set. If we set that to "none", "none" will
        # no longer have a single reverse translation.
        #
        self.attributeNamesDict = {
            "font-weight"             : "weight",
            "font-family"             : "family-name",
            "font-style"              : "style",
            "text-align"              : "justification",
            "text-indent"             : "indent",
            "font-size"               : "size",
            "background-color"        : "bg-color",
            "color"                   : "fg-color",
            "text-line-through-style" : "strikethrough",
            "text-underline-style"    : "underline",
            "text-position"           : "vertical-align",
            "writing-mode"            : "direction",
            "-moz-left"               : "left",
            "-moz-right"              : "right",
            "-moz-center"             : "center",
            "start"                   : "no justification",
            "underlinesolid"          : "single",
            "line-throughsolid"       : "solid"}

        # Keep track of the last object which appeared as a result of
        # the user routing the mouse pointer over an object. Also keep
        # track of the object which is associated with the mouse over
        # so that we can restore focus to it if need be.
        #
        self.lastMouseOverObject = None
        self.preMouseOverContext = [None, -1]
        self.inMouseOverObject = False

        self._inFocusMode = False
        self._focusModeIsSticky = False

        self._lastCommandWasCaretNav = False
        self._lastCommandWasStructNav = False
        self._lastCommandWasMouseButton = False

        self._sayAllContents = []

        # See bug 665522 - comment 5 regarding children. We're also seeing
        # stale names in both Gecko and other toolkits.
        app.setCacheMask(
            pyatspi.cache.DEFAULT ^ pyatspi.cache.CHILDREN ^ pyatspi.cache.NAME)

    def deactivate(self):
        """Called when this script is deactivated."""

        self._inSayAll = False
        self._sayAllIsInterrupted = False
        self._loadingDocumentContent = False
        self._lastCommandWasCaretNav = False
        self._lastCommandWasStructNav = False
        self._lastCommandWasMouseButton = False

    def getBookmarks(self):
        """Returns the "bookmarks" class for this script.
        """
        try:
            return self.bookmarks
        except AttributeError:
            self.bookmarks = GeckoBookmarks(self)
            return self.bookmarks

    def getBrailleGenerator(self):
        """Returns the braille generator for this script.
        """
        return BrailleGenerator(self)

    def getSpeechGenerator(self):
        """Returns the speech generator for this script.
        """
        return SpeechGenerator(self)

    def getTutorialGenerator(self):
        """Returns the tutorial generator for this script."""
        return TutorialGenerator(self)

    def getFormatting(self):
        """Returns the formatting strings for this script."""
        return Formatting(self)

    def getUtilities(self):
        """Returns the utilites for this script."""

        return Utilities(self)

    def getEnabledStructuralNavigationTypes(self):
        """Returns a list of the structural navigation object types
        enabled in this script.
        """

        enabledTypes = [GeckoStructuralNavigation.BLOCKQUOTE,
                        GeckoStructuralNavigation.BUTTON,
                        GeckoStructuralNavigation.CHECK_BOX,
                        GeckoStructuralNavigation.CHUNK,
                        GeckoStructuralNavigation.CLICKABLE,
                        GeckoStructuralNavigation.COMBO_BOX,
                        GeckoStructuralNavigation.ENTRY,
                        GeckoStructuralNavigation.FORM_FIELD,
                        GeckoStructuralNavigation.HEADING,
                        GeckoStructuralNavigation.IMAGE,
                        GeckoStructuralNavigation.LANDMARK,
                        GeckoStructuralNavigation.LINK,
                        GeckoStructuralNavigation.LIST,
                        GeckoStructuralNavigation.LIST_ITEM,
                        GeckoStructuralNavigation.LIVE_REGION,
                        GeckoStructuralNavigation.PARAGRAPH,
                        GeckoStructuralNavigation.RADIO_BUTTON,
                        GeckoStructuralNavigation.SEPARATOR,
                        GeckoStructuralNavigation.TABLE,
                        GeckoStructuralNavigation.TABLE_CELL,
                        GeckoStructuralNavigation.UNVISITED_LINK,
                        GeckoStructuralNavigation.VISITED_LINK]

        return enabledTypes

    def getStructuralNavigation(self):
        """Returns the 'structural navigation' class for this script.
        """
        types = self.getEnabledStructuralNavigationTypes()
        enable = _settingsManager.getSetting('structuralNavigationEnabled')
        return GeckoStructuralNavigation(self, types, enable)

    def setupInputEventHandlers(self):
        """Defines InputEventHandler fields for this script that can be
        called by the key and braille bindings.
        """

        default.Script.setupInputEventHandlers(self)
        self.inputEventHandlers.update(\
            self.structuralNavigation.inputEventHandlers)

        self.inputEventHandlers["goNextCharacterHandler"] = \
            input_event.InputEventHandler(
                Script.goNextCharacter,
                cmdnames.CARET_NAVIGATION_NEXT_CHAR)

        self.inputEventHandlers["goPreviousCharacterHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousCharacter,
                cmdnames.CARET_NAVIGATION_PREV_CHAR)

        self.inputEventHandlers["goNextWordHandler"] = \
            input_event.InputEventHandler(
                Script.goNextWord,
                cmdnames.CARET_NAVIGATION_NEXT_WORD)

        self.inputEventHandlers["goPreviousWordHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousWord,
                cmdnames.CARET_NAVIGATION_PREV_WORD)

        self.inputEventHandlers["goNextLineHandler"] = \
            input_event.InputEventHandler(
                Script.goNextLine,
                cmdnames.CARET_NAVIGATION_NEXT_LINE)

        self.inputEventHandlers["goPreviousLineHandler"] = \
            input_event.InputEventHandler(
                Script.goPreviousLine,
                cmdnames.CARET_NAVIGATION_PREV_LINE)

        self.inputEventHandlers["goTopOfFileHandler"] = \
            input_event.InputEventHandler(
                Script.goTopOfFile,
                cmdnames.CARET_NAVIGATION_FILE_START)

        self.inputEventHandlers["goBottomOfFileHandler"] = \
            input_event.InputEventHandler(
                Script.goBottomOfFile,
                cmdnames.CARET_NAVIGATION_FILE_END)

        self.inputEventHandlers["goBeginningOfLineHandler"] = \
            input_event.InputEventHandler(
                Script.goBeginningOfLine,
                cmdnames.CARET_NAVIGATION_LINE_START)

        self.inputEventHandlers["goEndOfLineHandler"] = \
            input_event.InputEventHandler(
                Script.goEndOfLine,
                cmdnames.CARET_NAVIGATION_LINE_END)

        self.inputEventHandlers["advanceLivePoliteness"] = \
            input_event.InputEventHandler(
                Script.advanceLivePoliteness,
                cmdnames.LIVE_REGIONS_ADVANCE_POLITENESS)

        self.inputEventHandlers["setLivePolitenessOff"] = \
            input_event.InputEventHandler(
                Script.setLivePolitenessOff,
                cmdnames.LIVE_REGIONS_SET_POLITENESS_OFF)

        self.inputEventHandlers["monitorLiveRegions"] = \
            input_event.InputEventHandler(
                Script.monitorLiveRegions,
                cmdnames.LIVE_REGIONS_MONITOR)

        self.inputEventHandlers["reviewLiveAnnouncement"] = \
            input_event.InputEventHandler(
                Script.reviewLiveAnnouncement,
                cmdnames.LIVE_REGIONS_REVIEW)

        self.inputEventHandlers["toggleCaretNavigationHandler"] = \
            input_event.InputEventHandler(
                Script.toggleCaretNavigation,
                cmdnames.CARET_NAVIGATION_TOGGLE)

        self.inputEventHandlers["sayAllHandler"] = \
            input_event.InputEventHandler(
                Script.sayAll,
                cmdnames.SAY_ALL)

        self.inputEventHandlers["panBrailleLeftHandler"] = \
            input_event.InputEventHandler(
                Script.panBrailleLeft,
                cmdnames.PAN_BRAILLE_LEFT,
                False) # Do not enable learn mode for this action

        self.inputEventHandlers["panBrailleRightHandler"] = \
            input_event.InputEventHandler(
                Script.panBrailleRight,
                cmdnames.PAN_BRAILLE_RIGHT,
                False) # Do not enable learn mode for this action

        self.inputEventHandlers["moveToMouseOverHandler"] = \
            input_event.InputEventHandler(
                Script.moveToMouseOver,
                cmdnames.MOUSE_OVER_MOVE)

        self.inputEventHandlers["togglePresentationModeHandler"] = \
            input_event.InputEventHandler(
                Script.togglePresentationMode,
                cmdnames.TOGGLE_PRESENTATION_MODE)

        self.inputEventHandlers["enableStickyFocusModeHandler"] = \
            input_event.InputEventHandler(
                Script.enableStickyFocusMode,
                cmdnames.SET_FOCUS_MODE_STICKY)

    def __getArrowBindings(self):
        """Returns an instance of keybindings.KeyBindings that use the
        arrow keys for navigating HTML content.
        """

        keyBindings = keybindings.KeyBindings()
        keyBindings.load(keymaps.arrowKeymap, self.inputEventHandlers)
        return keyBindings

    def getToolkitKeyBindings(self):
        """Returns the toolkit-specific keybindings for this script."""

        keyBindings = keybindings.KeyBindings()

        keyBindings.load(keymaps.commonKeymap, self.inputEventHandlers)

        if _settingsManager.getSetting('keyboardLayout') == \
                orca.settings.GENERAL_KEYBOARD_LAYOUT_DESKTOP:
            keyBindings.load(keymaps.desktopKeymap, self.inputEventHandlers)
        else:
            keyBindings.load(keymaps.laptopKeymap, self.inputEventHandlers)

        if _settingsManager.getSetting('caretNavigationEnabled'):
            for keyBinding in self.__getArrowBindings().keyBindings:
                keyBindings.add(keyBinding)

        bindings = self.structuralNavigation.keyBindings
        for keyBinding in bindings.keyBindings:
            keyBindings.add(keyBinding)

        return keyBindings

    def getAppPreferencesGUI(self):
        """Return a GtkGrid containing the application unique configuration
        GUI items for the current application."""

        grid = Gtk.Grid()
        grid.set_border_width(12)

        generalFrame = Gtk.Frame()
        grid.attach(generalFrame, 0, 0, 1, 1)

        label = Gtk.Label(label="<b>%s</b>" % guilabels.PAGE_NAVIGATION)
        label.set_use_markup(True)
        generalFrame.set_label_widget(label)

        generalAlignment = Gtk.Alignment.new(0.5, 0.5, 1, 1)
        generalAlignment.set_padding(0, 0, 12, 0)
        generalFrame.add(generalAlignment)
        generalGrid = Gtk.Grid()
        generalAlignment.add(generalGrid)

        label = guilabels.USE_CARET_NAVIGATION
        value = _settingsManager.getSetting('caretNavigationEnabled')
        self.controlCaretNavigationCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.controlCaretNavigationCheckButton.set_active(value) 
        generalGrid.attach(self.controlCaretNavigationCheckButton, 0, 0, 1, 1)

        label = guilabels.AUTO_FOCUS_MODE_CARET_NAV
        value = _settingsManager.getSetting('caretNavTriggersFocusMode')
        self.autoFocusModeCaretNavCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self.autoFocusModeCaretNavCheckButton.set_active(value)
        generalGrid.attach(self.autoFocusModeCaretNavCheckButton, 0, 1, 1, 1)

        label = guilabels.USE_STRUCTURAL_NAVIGATION
        value = self.structuralNavigation.enabled
        self.structuralNavigationCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.structuralNavigationCheckButton.set_active(value)
        generalGrid.attach(self.structuralNavigationCheckButton, 0, 2, 1, 1)

        label = guilabels.AUTO_FOCUS_MODE_STRUCT_NAV
        value = _settingsManager.getSetting('structNavTriggersFocusMode')
        self.autoFocusModeStructNavCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self.autoFocusModeStructNavCheckButton.set_active(value)
        generalGrid.attach(self.autoFocusModeStructNavCheckButton, 0, 3, 1, 1)

        label = guilabels.READ_PAGE_UPON_LOAD
        value = _settingsManager.getSetting('sayAllOnLoad')
        self.sayAllOnLoadCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self.sayAllOnLoadCheckButton.set_active(value)
        generalGrid.attach(self.sayAllOnLoadCheckButton, 0, 4, 1, 1)

        label = guilabels.CONTENT_LAYOUT_MODE
        value = _settingsManager.getSetting('layoutMode')
        self.layoutModeCheckButton = Gtk.CheckButton.new_with_mnemonic(label)
        self.layoutModeCheckButton.set_active(value)
        generalGrid.attach(self.layoutModeCheckButton, 0, 5, 1, 1)

        tableFrame = Gtk.Frame()
        grid.attach(tableFrame, 0, 1, 1, 1)

        label = Gtk.Label(label="<b>%s</b>" % guilabels.TABLE_NAVIGATION)
        label.set_use_markup(True)
        tableFrame.set_label_widget(label)

        tableAlignment = Gtk.Alignment.new(0.5, 0.5, 1, 1)
        tableAlignment.set_padding(0, 0, 12, 0)
        tableFrame.add(tableAlignment)
        tableGrid = Gtk.Grid()
        tableAlignment.add(tableGrid)

        label = guilabels.TABLE_SPEAK_CELL_COORDINATES
        value = _settingsManager.getSetting('speakCellCoordinates')
        self.speakCellCoordinatesCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.speakCellCoordinatesCheckButton.set_active(value)
        tableGrid.attach(self.speakCellCoordinatesCheckButton, 0, 0, 1, 1)

        label = guilabels.TABLE_SPEAK_CELL_SPANS
        value = _settingsManager.getSetting('speakCellSpan')
        self.speakCellSpanCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.speakCellSpanCheckButton.set_active(value)
        tableGrid.attach(self.speakCellSpanCheckButton, 0, 1, 1, 1)

        label = guilabels.TABLE_ANNOUNCE_CELL_HEADER
        value = _settingsManager.getSetting('speakCellHeaders')
        self.speakCellHeadersCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.speakCellHeadersCheckButton.set_active(value)
        tableGrid.attach(self.speakCellHeadersCheckButton, 0, 2, 1, 1)
           
        label = guilabels.TABLE_SKIP_BLANK_CELLS
        value = _settingsManager.getSetting('skipBlankCells')
        self.skipBlankCellsCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.skipBlankCellsCheckButton.set_active(value)
        tableGrid.attach(self.skipBlankCellsCheckButton, 0, 3, 1, 1)

        findFrame = Gtk.Frame()
        grid.attach(findFrame, 0, 2, 1, 1)

        label = Gtk.Label(label="<b>%s</b>" % guilabels.FIND_OPTIONS)
        label.set_use_markup(True)
        findFrame.set_label_widget(label)

        findAlignment = Gtk.Alignment.new(0.5, 0.5, 1, 1)
        findAlignment.set_padding(0, 0, 12, 0)
        findFrame.add(findAlignment)
        findGrid = Gtk.Grid()
        findAlignment.add(findGrid)

        verbosity = _settingsManager.getSetting('findResultsVerbosity')

        label = guilabels.FIND_SPEAK_RESULTS
        value = verbosity != settings.FIND_SPEAK_NONE
        self.speakResultsDuringFindCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.speakResultsDuringFindCheckButton.set_active(value)
        findGrid.attach(self.speakResultsDuringFindCheckButton, 0, 0, 1, 1)

        label = guilabels.FIND_ONLY_SPEAK_CHANGED_LINES
        value = verbosity == settings.FIND_SPEAK_IF_LINE_CHANGED
        self.changedLinesOnlyCheckButton = \
            Gtk.CheckButton.new_with_mnemonic(label)
        self.changedLinesOnlyCheckButton.set_active(value)
        findGrid.attach(self.changedLinesOnlyCheckButton, 0, 1, 1, 1)

        hgrid = Gtk.Grid()
        findGrid.attach(hgrid, 0, 2, 1, 1)

        self.minimumFindLengthLabel = \
              Gtk.Label(label=guilabels.FIND_MINIMUM_MATCH_LENGTH)
        self.minimumFindLengthLabel.set_alignment(0, 0.5)
        hgrid.attach(self.minimumFindLengthLabel, 0, 0, 1, 1)

        self.minimumFindLengthAdjustment = \
                   Gtk.Adjustment(_settingsManager.getSetting('findResultsMinimumLength'), 0, 20, 1)
        self.minimumFindLengthSpinButton = Gtk.SpinButton()
        self.minimumFindLengthSpinButton.set_adjustment(
            self.minimumFindLengthAdjustment)
        hgrid.attach(self.minimumFindLengthSpinButton, 1, 0, 1, 1)
        self.minimumFindLengthLabel.set_mnemonic_widget(
            self.minimumFindLengthSpinButton)

        grid.show_all()

        return grid

    def getPreferencesFromGUI(self):
        """Returns a dictionary with the app-specific preferences."""

        if not self.speakResultsDuringFindCheckButton.get_active():
            verbosity = settings.FIND_SPEAK_NONE
        elif self.changedLinesOnlyCheckButton.get_active():
            verbosity = settings.FIND_SPEAK_IF_LINE_CHANGED
        else:
            verbosity = settings.FIND_SPEAK_ALL

        return {
            'findResultsVerbosity': verbosity,
            'findResultsMinimumLength': self.minimumFindLengthSpinButton.get_value(),
            'sayAllOnLoad': self.sayAllOnLoadCheckButton.get_active(),
            'structuralNavigationEnabled': self.structuralNavigationCheckButton.get_active(),
            'structNavTriggersFocusMode': self.autoFocusModeStructNavCheckButton.get_active(),
            'caretNavigationEnabled': self.controlCaretNavigationCheckButton.get_active(),
            'caretNavTriggersFocusMode': self.autoFocusModeCaretNavCheckButton.get_active(),
            'speakCellCoordinates': self.speakCellCoordinatesCheckButton.get_active(),
            'layoutMode': self.layoutModeCheckButton.get_active(),
            'speakCellSpan': self.speakCellSpanCheckButton.get_active(),
            'speakCellHeaders': self.speakCellHeadersCheckButton.get_active(),
            'skipBlankCells': self.skipBlankCellsCheckButton.get_active()
        }

    def consumesKeyboardEvent(self, keyboardEvent):
        """Called when a key is pressed on the keyboard.

        Arguments:
        - keyboardEvent: an instance of input_event.KeyboardEvent

        Returns True if the event is of interest.
        """

        # We need to do this here. Orca caret and structural navigation
        # often result in the user being repositioned without our getting
        # a corresponding AT-SPI event. Without an AT-SPI event, script.py
        # won't know to dump the generator cache. See bgo#618827.
        #
        self.generatorCache = {}

        # The reason we override this method is that we only want
        # to consume keystrokes under certain conditions.  For
        # example, we only control the arrow keys when we're
        # managing caret navigation and we're inside document content.
        #
        # [[[TODO: WDW - this might be broken when we're inside a
        # text area that's inside document (or anything else that
        # we want to allow to control its own destiny).]]]

        user_bindings = None
        user_bindings_map = _settingsManager.getSetting('keyBindingsMap')
        if self.__module__ in user_bindings_map:
            user_bindings = user_bindings_map[self.__module__]
        elif "default" in user_bindings_map:
            user_bindings = user_bindings_map["default"]

        consumes = False
        if user_bindings:
            handler = user_bindings.getInputHandler(keyboardEvent)
            if handler and handler.function in self._caretNavigationFunctions:
                consumes = self.useCaretNavigationModel(keyboardEvent)
                self._lastCommandWasCaretNav = consumes
                self._lastCommandWasStructNav = False
                self._lastCommandWasMouseButton = False
            elif handler \
                 and (handler.function in self.structuralNavigation.functions \
                      or handler.function in self._liveRegionFunctions):
                consumes = self.useStructuralNavigationModel()
                self._lastCommandWasCaretNav = False
                self._lastCommandWasStructNav = consumes
                self._lastCommandWasMouseButton = False
            else:
                consumes = handler != None
                self._lastCommandWasCaretNav = False
                self._lastCommandWasStructNav = False
                self._lastCommandWasMouseButton = False
        if not consumes:
            handler = self.keyBindings.getInputHandler(keyboardEvent)
            if handler and handler.function in self._caretNavigationFunctions:
                consumes = self.useCaretNavigationModel(keyboardEvent)
                self._lastCommandWasCaretNav = consumes
                self._lastCommandWasStructNav = False
                self._lastCommandWasMouseButton = False
            elif handler \
                 and (handler.function in self.structuralNavigation.functions \
                      or handler.function in self._liveRegionFunctions):
                consumes = self.useStructuralNavigationModel()
                self._lastCommandWasCaretNav = False
                self._lastCommandWasStructNav = consumes
                self._lastCommandWasMouseButton = False
            else:
                consumes = handler != None
                self._lastCommandWasCaretNav = False
                self._lastCommandWasStructNav = False
                self._lastCommandWasMouseButton = False
        return consumes

    def textLines(self, obj, offset=None):
        """Creates a generator that can be used to iterate over each line
        of a text object, starting at the caret offset.

        Arguments:
        - obj: an Accessible that has a text specialization

        Returns an iterator that produces elements of the form:
        [SayAllContext, acss], where SayAllContext has the text to be
        spoken and acss is an ACSS instance for speaking the text.
        """

        self._sayAllIsInterrupted = False

        sayAllStyle = _settingsManager.getSetting('sayAllStyle')
        sayAllBySentence = sayAllStyle == settings.SAYALL_STYLE_SENTENCE
        if offset == None:
            contextObj, contextOffset = self.getCaretContext()
            if contextObj:
                [obj, characterOffset] = contextObj, contextOffset
            else:
                characterOffset = 0
        else:
            characterOffset = offset

        self._inSayAll = True
        done = False
        while not done:
            if sayAllBySentence:
                contents = self.utilities.getSentenceContentsAtOffset(obj, characterOffset)
            else:
                contents = self.getLineContentsAtOffset(obj, characterOffset)
            self._sayAllContents = contents
            for content in contents:
                obj, startOffset, endOffset, text = content
                if self.utilities.isLabellingContents(content, contents) \
                   or self.utilities.isInferredLabelForContents(content, contents):
                    continue

                utterances = self.getUtterancesFromContents([content], True)

                # TODO - JD: This is sad, but it's better than the old, broken
                # clumpUtterances(). We really need to fix the speechservers'
                # SayAll support. In the meantime, the generators should be
                # providing one ACSS per string.
                elements = list(filter(lambda x: isinstance(x, str), utterances[0]))
                voices = list(filter(lambda x: isinstance(x, ACSS), utterances[0]))
                if len(elements) != len(voices):
                    continue

                for i, element in enumerate(elements):
                    context = speechserver.SayAllContext(
                        obj, element, startOffset, endOffset)
                    self._sayAllContexts.append(context)
                    yield [context, voices[i]]

            obj = contents[-1][0]
            characterOffset = contents[-1][2]
            [obj, characterOffset] = self.findNextCaretInOrder(obj, characterOffset)
            done = (obj == None)

        self._inSayAll = False
        self._sayAllContents = []
        self._sayAllContexts = []

    def presentFindResults(self, obj, offset):
        """Updates the caret context to the match indicated by obj and
        offset.  Then presents the results according to the user's
        preferences.

        Arguments:
        -obj: The accessible object within the document
        -offset: The offset with obj where the caret should be positioned
        """

        # At some point in Firefox 3.2 we started getting detail1 values of
        # -1 for the caret-moved events for unfocused content during a find.
        # We don't want to base the new caret offset -- or the current line
        # on this value. We should be able to count on the selection range
        # instead -- across FF 3.0, 3.1, and 3.2.
        #
        enoughSelected = False
        text = self.utilities.queryNonEmptyText(obj)
        if text and text.getNSelections():
            [start, end] = text.getSelection(0)
            offset = max(offset, start)
            if end - start >= _settingsManager.getSetting('findResultsMinimumLength'):
                enoughSelected = True

        # Haing done that, update the caretContext. If the user wants
        # matches spoken, we also need to if we are on the same line
        # as before.
        #
        origObj, origOffset = self.getCaretContext()
        self.setCaretContext(obj, offset)
        verbosity = _settingsManager.getSetting('findResultsVerbosity')
        if enoughSelected and verbosity != settings.FIND_SPEAK_NONE:
            origExtents = self.utilities.getExtents(origObj, origOffset - 1, origOffset)
            newExtents = self.utilities.getExtents(obj, offset - 1, offset)
            lineChanged = not self.utilities.extentsAreOnSameLine(origExtents, newExtents)

            # If the user starts backspacing over the text in the
            # toolbar entry, he/she is indicating they want to perform
            # a different search. Because madeFindAnnounement may
            # be set to True, we should reset it -- but only if we
            # detect the line has also changed.  We're not getting
            # events from the Find entry, so we have to compare
            # offsets.
            #
            if self.utilities.isSameObject(origObj, obj) \
               and (origOffset > offset) and lineChanged:
                self.madeFindAnnouncement = False

            if lineChanged or not self.madeFindAnnouncement or \
               verbosity != settings.FIND_SPEAK_IF_LINE_CHANGED:
                self.presentLine(obj, offset)
                self.madeFindAnnouncement = True

    def sayAll(self, inputEvent, obj=None, offset=None):
        """Speaks the contents of the document beginning with the present
        location.  Overridden in this script because the sayAll could have
        been started on an object without text (such as an image).
        """

        if not self.inDocumentContent():
            return default.Script.sayAll(self, inputEvent, obj, offset)

        else:
            obj = obj or orca_state.locusOfFocus
            speech.sayAll(self.textLines(obj, offset),
                          self.__sayAllProgressCallback)

        return True

    def _rewindSayAll(self, context, minCharCount=10):
        if not self.inDocumentContent():
            return default.Script._rewindSayAll(self, context, minCharCount)

        if not _settingsManager.getSetting('rewindAndFastForwardInSayAll'):
            return False

        obj, start, end, string = self._sayAllContents[0]
        orca.setLocusOfFocus(None, obj, notifyScript=False)
        self.setCaretContext(obj, start)

        prevObj, prevOffset = self.findPreviousCaretInOrder(obj, start)
        self.sayAll(None, prevObj, prevOffset)
        return True

    def _fastForwardSayAll(self, context):
        if not self.inDocumentContent():
            return default.Script._fastForwardSayAll(self, context)

        if not _settingsManager.getSetting('rewindAndFastForwardInSayAll'):
            return False

        obj, start, end, string = self._sayAllContents[-1]
        orca.setLocusOfFocus(None, obj, notifyScript=False)
        self.setCaretContext(obj, end)

        nextObj, nextOffset = self.findNextCaretInOrder(obj, end)
        self.sayAll(None, nextObj, nextOffset)
        return True

    def __sayAllProgressCallback(self, context, progressType):
        if not self.inDocumentContent() or self._inFocusMode:
            default.Script.__sayAllProgressCallback(self, context, progressType)
            return

        if progressType == speechserver.SayAllContext.INTERRUPTED:
            if isinstance(orca_state.lastInputEvent, input_event.KeyboardEvent):
                self._sayAllIsInterrupted = True
                lastKey = orca_state.lastInputEvent.event_string
                if lastKey == "Down" and self._fastForwardSayAll(context):
                    return
                elif lastKey == "Up" and self._rewindSayAll(context):
                    return
                elif not self._lastCommandWasStructNav:
                    self.setCaretPosition(context.obj, context.currentOffset)
                    self.updateBraille(context.obj)

            self._inSayAll = False
            self._sayAllContents = []
            self._sayAllContexts = []
            return

        orca.setLocusOfFocus(None, context.obj, notifyScript=False)
        self.setCaretContext(context.obj, context.currentOffset)

    def _getCtrlShiftSelectionsStrings(self):
        return [messages.LINE_SELECTED_DOWN,
                messages.LINE_UNSELECTED_DOWN,
                messages.LINE_SELECTED_UP,
                messages.LINE_UNSELECTED_UP]

    def onActiveChanged(self, event):
        """Callback for object:state-changed:active accessibility events."""

        if self.findCommandRun:
            self.findCommandRun = False
            self.find()
            return

        if not event.detail1:
            return

        role = event.source.getRole()
        if role in [pyatspi.ROLE_DIALOG, pyatspi.ROLE_ALERT]:
            orca.setLocusOfFocus(event, event.source)

    def onBusyChanged(self, event):
        """Callback for object:state-changed:busy accessibility events."""

        if not self.inDocumentContent(event.source):
            msg = "INFO: Event source is not in document content"
            debug.println(debug.LEVEL_INFO, msg)
            super().onBusyChanged(event)
            return False

        if not self.inDocumentContent(orca_state.locusOfFocus):
            msg = "INFO: Ignoring: Locus of focus is not in document content"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        self._loadingDocumentContent = event.detail1

        obj, offset = self.getCaretContext()
        if not obj or self.utilities.isZombie(obj):
            self.clearCaretContext()

        if not _settingsManager.getSetting('onlySpeakDisplayedText'):
            if event.detail1:
                msg = messages.PAGE_LOADING_START
            elif event.source.name:
                msg = messages.PAGE_LOADING_END_NAMED % event.source.name
            else:
                msg = messages.PAGE_LOADING_END
            self.presentMessage(msg)

        if event.detail1:
            return True

        if self.useFocusMode(orca_state.locusOfFocus) != self._inFocusMode:
            self.togglePresentationMode(None)

        obj, offset = self.getCaretContext()
        if not obj:
            msg = "INFO: Could not get caret context"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if self.utilities.isFocusModeWidget(obj):
            msg = "INFO: Setting locus of focus to focusModeWidget %s" % obj
            debug.println(debug.LEVEL_INFO, msg)
            orca.setLocusOfFocus(event, obj)
            return True

        state = obj.getState()
        if self.utilities.isLink(obj) and state.contains(pyatspi.STATE_FOCUSED):
            msg = "INFO: Setting locus of focus to focused link %s" % obj
            debug.println(debug.LEVEL_INFO, msg)
            orca.setLocusOfFocus(event, obj)
            return True

        if offset > 0:
            msg = "INFO: Setting locus of focus to context obj %s" % obj
            debug.println(debug.LEVEL_INFO, msg)
            orca.setLocusOfFocus(event, obj)
            return True

        self.updateBraille(obj)
        if state.contains(pyatspi.STATE_FOCUSABLE):
            msg = "INFO: Not doing SayAll due to focusable context obj %s" % obj
            debug.println(debug.LEVEL_INFO, msg)
            speech.speak(self.speechGenerator.generateSpeech(obj))
        elif not _settingsManager.getSetting('sayAllOnLoad'):
            msg = "INFO: Not doing SayAll due to sayAllOnLoad being False"
            debug.println(debug.LEVEL_INFO, msg)
            self.speakContents(self.getLineContentsAtOffset(obj, offset))
        elif _settingsManager.getSetting('enableSpeech'):
            msg = "INFO: Doing SayAll"
            debug.println(debug.LEVEL_INFO, msg)
            self.sayAll(None)
        else:
            msg = "INFO: Not doing SayAll due to enableSpeech being False"
            debug.println(debug.LEVEL_INFO, msg)

        return True

    def onCaretMoved(self, event):
        """Callback for object:text-caret-moved accessibility events."""

        if self.utilities.isZombie(event.source):
            msg = "ERROR: Event source is Zombie"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if not self.inDocumentContent(event.source):
            msg = "INFO: Event source is not in document content"
            debug.println(debug.LEVEL_INFO, msg)
            super().onCaretMoved(event)
            return False

        if self._lastCommandWasCaretNav:
            msg = "INFO: Event ignored: Last command was caret nav"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if self._lastCommandWasStructNav:
            msg = "INFO: Event ignored: Last command was struct nav"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if self._lastCommandWasMouseButton:
            msg = "INFO: Event handled: Last command was mouse button"
            debug.println(debug.LEVEL_INFO, msg)
            orca.setLocusOfFocus(event, event.source)
            self.setCaretContext(event.source, event.detail1)
            return True

        if self.utilities.inFindToolbar() and not self.madeFindAnnouncement:
            msg = "INFO: Event handled: Presenting find results"
            debug.println(debug.LEVEL_INFO, msg)
            self.presentFindResults(event.source, event.detail1)
            return True

        if self.utilities.eventIsAutocompleteNoise(event):
            msg = "INFO: Event ignored: Autocomplete noise"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if self.utilities.textEventIsForNonNavigableTextObject(event):
            msg = "INFO: Event ignored: Event source is non-navigable text object"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if self.utilities.textEventIsDueToInsertion(event):
            msg = "INFO: Event handled: Updating position due to insertion"
            debug.println(debug.LEVEL_INFO, msg)
            self._saveLastCursorPosition(event.source, event.detail1)
            return True

        obj, offset = self.findFirstCaretContext(event.source, event.detail1)

        if self.utilities.caretMovedToSamePageFragment(event):
            msg = "INFO: Event handled: Caret moved to fragment"
            debug.println(debug.LEVEL_INFO, msg)
            orca.setLocusOfFocus(event, obj)
            self.setCaretContext(obj, offset)
            return True

        text = self.utilities.queryNonEmptyText(event.source)
        if not text:
            if event.source.getRole() == pyatspi.ROLE_LINK:
                msg = "INFO: Event handled: Was for non-text link"
                debug.println(debug.LEVEL_INFO, msg)
                orca.setLocusOfFocus(event, event.source)
                self.setCaretContext(event.source, event.detail1)
            else:
                msg = "INFO: Event ignored: Was for non-text non-link"
                debug.println(debug.LEVEL_INFO, msg)
            return True

        char = text.getText(event.detail1, event.detail1+1)
        isEditable = obj.getState().contains(pyatspi.STATE_EDITABLE)
        if not char and not isEditable:
            msg = "INFO: Event ignored: Was for empty char in non-editable text"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if char == self.EMBEDDED_OBJECT_CHARACTER:
            if not self.utilities.isTextBlockElement(obj):
                msg = "INFO: Event ignored: Was for embedded non-textblock"
                debug.println(debug.LEVEL_INFO, msg)
                return True

            msg = "INFO: Setting locusOfFocus, context to: %s, %i" % (obj, offset)
            debug.println(debug.LEVEL_INFO, msg)
            orca.setLocusOfFocus(event, obj)
            self.setCaretContext(obj, offset)
            return True

        if not _settingsManager.getSetting('caretNavigationEnabled') \
           or self._inFocusMode or isEditable:
            orca.setLocusOfFocus(event, event.source, False)
            self.setCaretContext(event.source, event.detail1)
            msg = "INFO: Setting locusOfFocus, context to: %s, %i" % \
                  (event.source, event.detail1)
            debug.println(debug.LEVEL_INFO, msg)
            super().onCaretMoved(event)
            return False

        self.setCaretContext(obj, offset)
        msg = "INFO: Setting context to: %s, %i" % (obj, offset)
        debug.println(debug.LEVEL_INFO, msg)
        super().onCaretMoved(event)
        return False

    def onCheckedChanged(self, event):
        """Callback for object:state-changed:checked accessibility events."""

        if not self.inDocumentContent(event.source):
            msg = "INFO: Event source is not in document content"
            debug.println(debug.LEVEL_INFO, msg)
            super().onCheckedChanged(event)
            return False

        obj, offset = self.getCaretContext()
        if obj != event.source:
            msg = "INFO: Event source is not context object"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        oldObj, oldState = self.pointOfReference.get('checkedChange', (None, 0))
        if hash(oldObj) == hash(obj) and oldState == event.detail1:
            msg = "INFO: Ignoring event, state hasn't changed"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        role = obj.getRole()
        if not (self._lastCommandWasCaretNav and role == pyatspi.ROLE_RADIO_BUTTON):
            msg = "INFO: Event is something default can handle"
            debug.println(debug.LEVEL_INFO, msg)
            super().onCheckedChanged(event)
            return False

        self.updateBraille(obj)
        speech.speak(self.speechGenerator.generateSpeech(obj, alreadyFocused=True))
        self.pointOfReference['checkedChange'] = hash(obj), event.detail1
        return True

    def onChildrenChanged(self, event):
        """Callback for object:children-changed accessibility events."""

        if self.handleAsLiveRegion(event):
            msg = "INFO: Event to be handled as live region"
            debug.println(debug.LEVEL_INFO, msg)
            self.liveMngr.handleEvent(event)
            return True

        if self._loadingDocumentContent:
            msg = "INFO: Ignoring because document content is being loaded."
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if not event.any_data or self.utilities.isZombie(event.any_data):
            msg = "INFO: Ignoring because any data is null or zombified."
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if not self.inDocumentContent(event.source):
            msg = "INFO: Event source is not in document content"
            debug.println(debug.LEVEL_INFO, msg)
            super().onChildrenChanged(event)
            return False

        obj, offset = self.getCaretContext()
        if obj and self.utilities.isZombie(obj):
            replicant = self.utilities.findReplicant(event.source, obj)
            if replicant:
                # Refrain from actually touching the replicant by grabbing
                # focus or setting the caret in it. Doing so will only serve
                # to anger it.
                msg = "INFO: Event handled by updating locusOfFocus and context"
                debug.println(debug.LEVEL_INFO, msg)
                orca.setLocusOfFocus(event, replicant, False)
                self.setCaretContext(replicant, offset)
                return True

        child = event.any_data
        if child.getRole() in [pyatspi.ROLE_ALERT, pyatspi.ROLE_DIALOG]:
            msg = "INFO: Setting locusOfFocus to event.any_data"
            debug.println(debug.LEVEL_INFO, msg)
            orca.setLocusOfFocus(event, child)
            return True

        if self.lastMouseRoutingTime and 0 < time.time() - self.lastMouseRoutingTime < 1:
            utterances = []
            utterances.append(messages.NEW_ITEM_ADDED)
            utterances.extend(self.speechGenerator.generateSpeech(child, force=True))
            speech.speak(utterances)
            self.lastMouseOverObject = child
            self.preMouseOverContext = self.getCaretContext()
            return True

        super().onChildrenChanged(event)
        return False

    def onDocumentLoadComplete(self, event):
        """Callback for document:load-complete accessibility events."""

        msg = "INFO: Updating loading state and resetting live regions"
        debug.println(debug.LEVEL_INFO, msg)
        self._loadingDocumentContent = False
        self.liveMngr.reset()
        return True

    def onDocumentLoadStopped(self, event):
        """Callback for document:load-stopped accessibility events."""

        msg = "INFO: Updating loading state"
        debug.println(debug.LEVEL_INFO, msg)
        self._loadingDocumentContent = False
        return True

    def onDocumentReload(self, event):
        """Callback for document:reload accessibility events."""

        msg = "INFO: Updating loading state"
        debug.println(debug.LEVEL_INFO, msg)
        self._loadingDocumentContent = True
        return True

    def onFocus(self, event):
        """Callback for focus: accessibility events."""

        # We should get proper state-changed events for these.
        if self.inDocumentContent(event.source):
            return

        # NOTE: This event type is deprecated and Orca should no longer use it.
        # This callback remains just to handle bugs in applications and toolkits
        # during the remainder of the unstable (3.11) development cycle.

        role = event.source.getRole()

        # Unfiled. When a context menu pops up, we seem to get a focus: event,
        # but no object:state-changed:focused event from Gecko.
        if role == pyatspi.ROLE_MENU:
            orca.setLocusOfFocus(event, event.source)
            return

        # Unfiled. When the Thunderbird 'do you want to replace this file'
        # attachment dialog pops up, the 'Replace' button emits a focus:
        # event, but we only seem to get the object:state-changed:focused
        # event when it gives up focus.
        if role == pyatspi.ROLE_PUSH_BUTTON:
            orca.setLocusOfFocus(event, event.source)

        # Some of the dialogs used by Thunderbird (and perhaps Firefox?) seem
        # to be using Gtk+ 2, along with its associated focused-event issues.
        # Unfortunately, because Gtk+ 2 doesn't expose a per-object toolkit,
        # we cannot know that a given widget is Gtk+ 2. Therefore, we'll put
        # our Gtk+ 2 toolkit script hacks here as well just to be safe.
        if role in [pyatspi.ROLE_TEXT, pyatspi.ROLE_PASSWORD_TEXT]:
            orca.setLocusOfFocus(event, event.source)

    def onFocusedChanged(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if not event.detail1:
            msg = "INFO: Ignoring because event source lost focus"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if self.utilities.isZombie(event.source):
            msg = "ERROR: Event source is Zombie"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if not self.inDocumentContent(event.source):
            msg = "INFO: Event source is not in document content"
            debug.println(debug.LEVEL_INFO, msg)
            super().onFocusedChanged(event)
            return False

        state = event.source.getState()
        if state.contains(pyatspi.STATE_EDITABLE):
            msg = "INFO: Event source is editable"
            debug.println(debug.LEVEL_INFO, msg)
            super().onFocusedChanged(event)
            return False

        role = event.source.getRole()
        if role in [pyatspi.ROLE_DIALOG, pyatspi.ROLE_ALERT]:
            msg = "INFO: Event handled: Setting locusOfFocus to event source"
            debug.println(debug.LEVEL_INFO, msg)
            orca.setLocusOfFocus(event, event.source)
            return True

        if self._lastCommandWasCaretNav:
            msg = "INFO: Event ignored: Last command was caret nav"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if self._lastCommandWasStructNav:
            msg = "INFO: Event ignored: Last command was struct nav"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if role in [pyatspi.ROLE_DOCUMENT_FRAME, pyatspi.ROLE_DOCUMENT_WEB]:
            if self.inDocumentContent(orca_state.locusOfFocus) \
               and not self.utilities.isZombie(orca_state.locusOfFocus):
                msg = "INFO: Event ignored: locusOfFocus already in document"
                debug.println(debug.LEVEL_INFO, msg)
                return True

            obj, offset = self.getCaretContext(event.source)
            if obj and self.utilities.isZombie(obj):
                msg = "INFO: Clearing context - obj is zombie"
                debug.println(debug.LEVEL_INFO, msg)
                self.clearCaretContext()
                obj, offset = self.getCaretContext(event.source)

            if obj:
                msg = "INFO: Event handled: Setting locusOfFocus to context"
                debug.println(debug.LEVEL_INFO, msg)
                orca.setLocusOfFocus(event, obj)
                return True

        if not state.contains(pyatspi.STATE_FOCUSABLE) \
           and not state.contains(pyatspi.STATE_FOCUSED):
            msg = "INFO: Event ignored: Source is not focusable or focused"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        super().onFocusedChanged(event)
        return False

    def onMouseButton(self, event):
        """Callback for mouse:button accessibility events."""

        self._lastCommandWasCaretNav = False
        self._lastCommandWasStructNav = False
        self._lastCommandWasMouseButton = True
        super().onMouseButton(event)
        return False

    def onNameChanged(self, event):
        """Callback for object:property-change:accessible-name events."""

        if event.source.getRole() == pyatspi.ROLE_FRAME:
            msg = "INFO: Flusing messages from live region manager"
            debug.println(debug.LEVEL_INFO, msg)
            self.liveMngr.flushMessages()

        return True

    def onShowingChanged(self, event):
        """Callback for object:state-changed:showing accessibility events."""

        if not self.inDocumentContent(event.source):
            msg = "INFO: Event source is not in document content"
            debug.println(debug.LEVEL_INFO, msg)
            super().onShowingChanged(event)
            return False

        return True

    def onTextDeleted(self, event):
        """Callback for object:text-changed:delete accessibility events."""

        if not self.inDocumentContent(event.source):
            msg = "INFO: Event source is not in document content"
            debug.println(debug.LEVEL_INFO, msg)
            super().onTextDeleted(event)
            return False

        if self.utilities.eventIsAutocompleteNoise(event):
            msg = "INFO: Ignoring event believed to be autocomplete noise"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if self.utilities.textEventIsDueToInsertion(event):
            msg = "INFO: Ignoring event believed to be due to text insertion"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        msg = "INFO: Clearing content cache due to text deletion"
        debug.println(debug.LEVEL_INFO, msg)
        # self.utilities.clearContentCache()
        self._destroyLineCache()

        state = event.source.getState()
        if not state.contains(pyatspi.STATE_EDITABLE):
            if self.inMouseOverObject \
               and self.utilities.isZombie(self.lastMouseOverObject):
                msg = "INFO: Restoring pre-mouseover context"
                debug.println(debug.LEVEL_INFO, msg)
                self.restorePreMouseOverContext()

            msg = "INFO: Done processing non-editable source"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        super().onTextDeleted(event)
        return False

    def onTextInserted(self, event):
        """Callback for object:text-changed:insert accessibility events."""

        if not self.inDocumentContent(event.source):
            msg = "INFO: Event source is not in document content"
            debug.println(debug.LEVEL_INFO, msg)
            super().onTextInserted(event)
            return False

        if self.utilities.eventIsAutocompleteNoise(event):
            msg = "INFO: Ignoring: Event believed to be autocomplete noise"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        msg = "INFO: Clearing content cache due to text insertion"
        debug.println(debug.LEVEL_INFO, msg)
        # self.utilities.clearContentCache()
        self._destroyLineCache()

        if self.handleAsLiveRegion(event):
            msg = "INFO: Event to be handled as live region"
            debug.println(debug.LEVEL_INFO, msg)
            self.liveMngr.handleEvent(event)
            return True

        if self.utilities.eventIsEOCAdded(event):
            msg = "INFO: Ignoring: Event was for embedded object char"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        text = self.utilities.queryNonEmptyText(event.source)
        if not text:
            msg = "INFO: Ignoring: Event source is not a text object"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        state = event.source.getState()
        if not state.contains(pyatspi.STATE_EDITABLE) \
           and event.source != orca_state.locusOfFocus:
            msg = "INFO: Done processing non-editable, non-locusOfFocus source"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        super().onTextInserted(event)
        return False

    def onTextSelectionChanged(self, event):
        """Callback for object:text-selection-changed accessibility events."""

        if self.utilities.isZombie(event.source):
            msg = "ERROR: Event source is Zombie"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if not self.inDocumentContent(event.source):
            msg = "INFO: Event source is not in document content"
            debug.println(debug.LEVEL_INFO, msg)
            super().onTextSelectionChanged(event)
            return False

        if self.utilities.inFindToolbar():
            msg = "INFO: Event handled: Presenting find results"
            debug.println(debug.LEVEL_INFO, msg)
            self.presentFindResults(event.source, -1)
            self._saveFocusedObjectInfo(orca_state.locusOfFocus)
            return True

        if not self.inDocumentContent(orca_state.locusOfFocus):
            msg = "INFO: Ignoring: Event in document content; focus is not"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if self.utilities.eventIsAutocompleteNoise(event):
            msg = "INFO: Ignoring: Event believed to be autocomplete noise"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if self.utilities.textEventIsForNonNavigableTextObject(event):
            msg = "INFO: Ignoring event for non-navigable text object"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        text = self.utilities.queryNonEmptyText(event.source)
        if not text:
            msg = "INFO: Ignoring: Event source is not a text object"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        char = text.getText(event.detail1, event.detail1+1)
        if char == self.EMBEDDED_OBJECT_CHARACTER:
            msg = "INFO: Ignoring: Event offset is at embedded object"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        obj, offset = self.getCaretContext()
        if obj and obj.parent and event.source in [obj.parent, obj.parent.parent]:
            msg = "INFO: Ignoring: Source is context ancestor"
            debug.println(debug.LEVEL_INFO, msg)
            return True

        super().onTextSelectionChanged(event)
        return False

    def handleProgressBarUpdate(self, event, obj):
        """Determine whether this progress bar event should be spoken or not.
        For Firefox, we don't want to speak the small "page load" progress
        bar. All other Firefox progress bars get passed onto the parent
        class for handling.

        Arguments:
        - event: if not None, the Event that caused this to happen
        - obj:  the Accessible progress bar object.
        """

        rolesList = [pyatspi.ROLE_PROGRESS_BAR, \
                     pyatspi.ROLE_STATUS_BAR, \
                     pyatspi.ROLE_FRAME, \
                     pyatspi.ROLE_APPLICATION]
        if not self.utilities.hasMatchingHierarchy(event.source, rolesList):
            default.Script.handleProgressBarUpdate(self, event, obj)

    def useFocusMode(self, obj):
        if self._focusModeIsSticky:
            return True

        if not orca.settings.structNavTriggersFocusMode \
           and self._lastCommandWasStructNav:
            return False

        if not orca.settings.caretNavTriggersFocusMode \
           and self._lastCommandWasCaretNav:
            return False

        return self.utilities.isFocusModeWidget(obj)

    def locusOfFocusChanged(self, event, oldFocus, newFocus):
        """Handles changes of focus of interest to the script."""

        if newFocus and self.utilities.isZombie(newFocus):
            msg = "ERROR: New focus is Zombie" % newFocus
            debug.println(debug.LEVEL_INFO, msg)
            return True

        if not self.inDocumentContent(newFocus):
            msg = "INFO: Locus of focus changed to non-document obj"
            self._madeFindAnnouncement = False
            self._inFocusMode = False
            debug.println(debug.LEVEL_INFO, msg)
            super().locusOfFocusChanged(event, oldFocus, newFocus)
            return False

        caretOffset = 0
        if self.utilities.inFindToolbar(oldFocus):
            newFocus, caretOffset = self.getCaretContext()

        text = self.utilities.queryNonEmptyText(newFocus)
        if text and (0 <= text.caretOffset < text.characterCount):
            caretOffset = text.caretOffset

        self.setCaretContext(newFocus, caretOffset)
        self.updateBraille(newFocus)
        speech.speak(self.speechGenerator.generateSpeech(newFocus, priorObj=oldFocus))
        self._saveFocusedObjectInfo(newFocus)

        if not self._focusModeIsSticky \
           and self.useFocusMode(newFocus) != self._inFocusMode:
            self.togglePresentationMode(None)

        return True

    def _destroyLineCache(self):
        """Removes all of the stored lines."""

        self.currentLineContents = []
        self.currentAttrs = {}

    def presentLine(self, obj, offset):
        """Presents the current line in speech and in braille.

        Arguments:
        - obj: the Accessible at the caret
        - offset: the offset within obj
        """

        contents = self.getLineContentsAtOffset(obj, offset)
        if not isinstance(orca_state.lastInputEvent, input_event.BrailleEvent):
            self.speakContents(self.currentLineContents)
        self.updateBraille(obj)

    def updateBraille(self, obj, extraRegion=None):
        """Updates the braille display to show the given object.

        Arguments:
        - obj: the Accessible
        - extra: extra Region to add to the end
        """

        if not _settingsManager.getSetting('enableBraille') \
           and not _settingsManager.getSetting('enableBrailleMonitor'):
            debug.println(debug.LEVEL_INFO, "BRAILLE: update disabled")
            return

        if not self.inDocumentContent() or self._inFocusMode:
            default.Script.updateBraille(self, obj, extraRegion)
            return

        if not obj:
            return

        line = self.getNewBrailleLine(clearBraille=True, addLine=True)

        [focusedObj, focusedOffset] = self.getCaretContext()
        contents = self.getLineContentsAtOffset(focusedObj, focusedOffset)
        contents = self.utilities.filterContentsForPresentation(contents)
        index = self.utilities.findObjectInContents(focusedObj, focusedOffset, contents)
        if not len(contents) or \
           (index == -1 and not self.utilities.isTextBlockElement(focusedObj)):
            default.Script.updateBraille(self, obj, extraRegion)
            return

        focusedRegion = None
        lastObj = None
        for i, content in enumerate(contents):
            [obj, startOffset, endOffset, string] = content
            [regions, fRegion] = self.brailleGenerator.generateBraille(
                obj, startOffset=startOffset, endOffset=endOffset, string=string)
            if i == index:
                focusedRegion = fRegion

            if line.regions and regions:
                if line.regions[-1].string:
                    lastChar = line.regions[-1].string[-1]
                else:
                    lastChar = ""
                if regions[0].string:
                    nextChar = regions[0].string[0]
                else:
                    nextChar = ""
                if self.utilities.needsSeparator(lastChar, nextChar):
                    self.addToLineAsBrailleRegion(" ", line)

            self.addBrailleRegionsToLine(regions, line)
            lastObj = obj

        if line.regions:
            line.regions[-1].string = line.regions[-1].string.rstrip(" ")

        # TODO - JD: This belongs in the generator.
        if lastObj and lastObj.getRole() != pyatspi.ROLE_HEADING:
            heading = self.utilities.ancestorWithRole(
                lastObj, [pyatspi.ROLE_HEADING], [pyatspi.ROLE_DOCUMENT_FRAME])
            if heading:
                level = self.utilities.headingLevel(heading)
                string = " %s" % object_properties.ROLE_HEADING_LEVEL_BRAILLE % level
                self.addToLineAsBrailleRegion(string, line)

        if extraRegion:
            self.addBrailleRegionToLine(extraRegion, line)

        self.setBrailleFocus(focusedRegion, getLinkMask=False)
        self.refreshBraille(panToCursor=True, getLinkMask=False)

    def sayCharacter(self, obj):
        """Speaks the character at the current caret position."""

        # We need to handle HTML content differently because of the
        # EMBEDDED_OBJECT_CHARACTER model of Gecko.  For all other
        # things, however, we can defer to the default scripts.
        #

        if not self.inDocumentContent() or obj.getState().contains(pyatspi.STATE_EDITABLE):
            default.Script.sayCharacter(self, obj)
            return

        [obj, characterOffset] = self.getCaretContext()
        if characterOffset >= 0:
            self.speakCharacterAtOffset(obj, characterOffset)

    def sayWord(self, obj):
        """Speaks the word at the current caret position."""

        # We need to handle HTML content differently because of the
        # EMBEDDED_OBJECT_CHARACTER model of Gecko.  For all other
        # things, however, we can defer to the default scripts.
        #
        if not self.inDocumentContent() or obj.getState().contains(pyatspi.STATE_EDITABLE):
            default.Script.sayWord(self, obj)
            return

        [obj, characterOffset] = self.getCaretContext()
        wordContents = self.utilities.getWordContentsAtOffset(obj, characterOffset)

        [textObj, startOffset, endOffset, word] = wordContents[0]
        self.speakMisspelledIndicator(textObj, startOffset)
        self.speakContents(wordContents)

    def sayLine(self, obj):
        """Speaks the line at the current caret position."""

        # We need to handle HTML content differently because of the
        # EMBEDDED_OBJECT_CHARACTER model of Gecko.  For all other
        # things, however, we can defer to the default scripts.
        #
        if not self.inDocumentContent() or obj.getState().contains(pyatspi.STATE_EDITABLE):
            default.Script.sayLine(self, obj)
            return

        [obj, characterOffset] = self.getCaretContext()
        self.speakContents(self.getLineContentsAtOffset(obj, characterOffset))

    def panBrailleLeft(self, inputEvent=None, panAmount=0):
        """In document content, we want to use the panning keys to browse the
        entire document.
        """
        if self.flatReviewContext \
           or not self.inDocumentContent() \
           or not self.isBrailleBeginningShowing():
            default.Script.panBrailleLeft(self, inputEvent, panAmount)
        else:
            self.goPreviousLine(inputEvent)
            while self.panBrailleInDirection(panToLeft=False):
                pass
            self.refreshBraille(False)
        return True

    def panBrailleRight(self, inputEvent=None, panAmount=0):
        """In document content, we want to use the panning keys to browse the
        entire document.
        """
        if self.flatReviewContext \
           or not self.inDocumentContent() \
           or not self.isBrailleEndShowing():
            default.Script.panBrailleRight(self, inputEvent, panAmount)
        elif self.goNextLine(inputEvent):
            while self.panBrailleInDirection(panToLeft=True):
                pass
            self.refreshBraille(False)
        return True

    ####################################################################
    #                                                                  #
    # Utility Methods                                                  #
    #                                                                  #
    ####################################################################

    def inDocumentContent(self, obj=None):
        """Returns True if the given object (defaults to the current
        locus of focus is in the document content).
        """

        if not obj:
            obj = orca_state.locusOfFocus
        try:
            return self.generatorCache['inDocumentContent'][obj]
        except:
            pass

        result = False
        while obj:
            try:
                role = obj.getRole()
            except:
                return False
            if role == pyatspi.ROLE_DOCUMENT_FRAME \
                    or role == pyatspi.ROLE_EMBEDDED:
                result = True
                break
            else:
                obj = obj.parent

        if 'inDocumentContent' not in self.generatorCache:
            self.generatorCache['inDocumentContent'] = {}

        if obj:
            self.generatorCache['inDocumentContent'][obj] = result
            
        return result

    def useCaretNavigationModel(self, keyboardEvent):
        """Returns True if we should do our own caret navigation.
        """

        if not _settingsManager.getSetting('caretNavigationEnabled') \
           or self._inFocusMode:
            return False

        if not self.inDocumentContent():
            return False

        if keyboardEvent.event_string in ["Page_Up", "Page_Down"]:
            return False

        if keyboardEvent.modifiers & keybindings.SHIFT_MODIFIER_MASK:
            return False

        if not orca_state.locusOfFocus:
            return False

        return True

    def useStructuralNavigationModel(self):
        """Returns True if we should do our own structural navigation.
        This should return False if we're in something like an entry
        or a list.
        """

        if not self.structuralNavigation.enabled or self._inFocusMode:
            return False

        if not self.inDocumentContent():
            return False

        return True

    def _getAttrDictionary(self, obj):
        if not obj:
            return {}

        try:
            return dict([attr.split(':', 1) for attr in obj.getAttributes()])
        except:
            return {}

    def handleAsLiveRegion(self, event):
        """Returns True if the given event (object:children-changed, object:
        text-insert only) should be considered a live region event"""

        if self._loadingDocumentContent \
           or not _settingsManager.getSetting('inferLiveRegions'):
            return False

        attrs = self._getAttrDictionary(event.source)
        if 'container-live' in attrs:
            return True

        return False

    def getChildIndex(self, obj, characterOffset):
        """Given an object that implements accessible text, determine
        the index of the child that is represented by an
        EMBEDDED_OBJECT_CHARACTER at characterOffset in the object's
        accessible text."""

        try:
            hypertext = obj.queryHypertext()
        except NotImplementedError:
            index = -1
        else:
            index = hypertext.getLinkIndex(characterOffset)

        return index
 
    def getTopOfFile(self):
        """Returns the object and first caret offset at the top of the
         document frame."""

        documentFrame = self.utilities.documentFrame()
        [obj, offset] = self.findFirstCaretContext(documentFrame, 0)

        return [obj, offset]

    def getBottomOfFile(self):
        """Returns the object and last caret offset at the bottom of the
         document frame."""

        documentFrame = self.utilities.documentFrame()
        text = self.utilities.queryNonEmptyText(documentFrame)
        if text:
            char = text.getText(text.characterCount - 1, text.characterCount)
            if char != self.EMBEDDED_OBJECT_CHARACTER:
                return [documentFrame, text.characterCount - 1]

        obj = self.getLastObject(documentFrame)
        offset = 0

        # If the last object is a link, it may be more efficient to check
        # for text that follows.
        #
        if obj and obj.getRole() == pyatspi.ROLE_LINK:
            text = self.utilities.queryNonEmptyText(obj.parent)
            if text:
                char = text.getText(text.characterCount - 1,
                                    text.characterCount)
                if char != self.EMBEDDED_OBJECT_CHARACTER:
                    return [obj.parent, text.characterCount - 1]

        # obj should now be the very last item in the entire document frame
        # and not have children of its own.  Therefore, it should have text.
        # If it doesn't, we don't want to be here.
        #
        text = self.utilities.queryNonEmptyText(obj)
        if text:
            offset = text.characterCount - 1
        else:
            obj = self.findPreviousObject(obj, documentFrame)

        while obj:
            [lastObj, lastOffset] = self.findNextCaretInOrder(obj, offset)
            if not lastObj \
               or self.utilities.isSameObject(lastObj, obj) \
               and (lastOffset == offset):
                break

            [obj, offset] = [lastObj, lastOffset]

        return [obj, offset]

    def getLastObject(self, documentFrame):
        """Returns the last object in the document frame"""

        try:
            lastChild = documentFrame[documentFrame.childCount - 1]
        except:
            lastChild = documentFrame
        while lastChild:
            lastObj = self.findNextObject(lastChild, documentFrame)
            if lastObj and lastObj != lastChild:
                lastChild = lastObj
            else:
                break

        return lastChild

    def getPageSummary(self, obj):
        """Returns the quantity of headings, forms, tables, visited links,
        and unvisited links on the page containing obj.
        """

        docframe = self.utilities.documentFrame()
        col = docframe.queryCollection()
        headings = 0
        forms = 0
        tables = 0
        vlinks = 0
        uvlinks = 0
        percentRead = None

        stateset = pyatspi.StateSet()
        roles = [pyatspi.ROLE_HEADING, pyatspi.ROLE_LINK, pyatspi.ROLE_TABLE,
                 pyatspi.ROLE_FORM]
        rule = col.createMatchRule(stateset.raw(), col.MATCH_NONE,
                                   "", col.MATCH_NONE,
                                   roles, col.MATCH_ANY,
                                   "", col.MATCH_NONE,
                                   False)

        matches = col.getMatches(rule, col.SORT_ORDER_CANONICAL, 0, True)
        col.freeMatchRule(rule)
        for obj in matches:
            role = obj.getRole()
            if role == pyatspi.ROLE_HEADING:
                headings += 1
            elif role == pyatspi.ROLE_FORM:
                forms += 1
            elif role == pyatspi.ROLE_TABLE \
                      and not self.utilities.isLayoutOnly(obj):
                tables += 1
            elif role == pyatspi.ROLE_LINK:
                if obj.getState().contains(pyatspi.STATE_VISITED):
                    vlinks += 1
                else:
                    uvlinks += 1

        return [headings, forms, tables, vlinks, uvlinks, percentRead]

    ####################################################################
    #                                                                  #
    # Methods to find previous and next objects.                       #
    #                                                                  #
    ####################################################################

    def findFirstCaretContext(self, obj, characterOffset):
        """Given an object and a character offset, find the first
        [obj, characterOffset] that is actually presenting something
        on the display.  The reason we do this is that the
        [obj, characterOffset] passed in may actually be pointing
        to an embedded object character.  In those cases, we dig
        into the hierarchy to find the 'real' thing.

        Arguments:
        -obj: an accessible object
        -characterOffset: the offset of the character where to start
        looking for real text

        Returns [obj, characterOffset] that points to real content.
        """

        try:
            role = obj.getRole()
        except:
            return [None, -1]

        if role == pyatspi.ROLE_TABLE and obj.childCount:
            child = obj[0]
            if child.getRole() in [pyatspi.ROLE_CAPTION, pyatspi.ROLE_LIST]:
                obj = child
            else:
                obj = obj.queryTable().getAccessibleAt(0, 0)
            return self.findFirstCaretContext(obj, 0)

        text = self.utilities.queryNonEmptyText(obj)
        if not text:
            return [obj, -1]

        character = text.getText(characterOffset, characterOffset + 1)
        if len(character) == 1 and character != self.EMBEDDED_OBJECT_CHARACTER:
            return [obj, characterOffset]

        try:
            childIndex = self.getChildIndex(obj, characterOffset)
            child = obj[childIndex]

            # Handle bogus empty paragraphs. Bug 677615.
            # Make that bogus empty text objects.
            textRoles = [pyatspi.ROLE_HEADING,
                         pyatspi.ROLE_PARAGRAPH,
                         pyatspi.ROLE_SECTION]
            if child.getRole() in textRoles \
               and not self.utilities.queryNonEmptyText(child):
                return self.findFirstCaretContext(obj, characterOffset + 1)

            return self.findFirstCaretContext(child, 0)

        except:
            return [obj, -1]

        return [obj, characterOffset]

    def findNextCaretInOrder(self, obj=None,
                             startOffset=-1,
                             includeNonText=True):
        """Given an object at a character offset, return the next
        caret context following an in-order traversal rule.

        Arguments:
        - root: the Accessible to start at.  If None, starts at the
        document frame.
        - startOffset: character position in the object text field
        (if it exists) to start at.  Defaults to -1, which means
        start at the beginning - that is, the next character is the
        first character in the object.
        - includeNonText: If False, only land on objects that support the
        accessible text interface; otherwise, include logical leaf
        nodes like check boxes, combo boxes, etc.

        Returns [obj, characterOffset] or [None, -1]
        """

        if not obj:
            obj = self.utilities.documentFrame()

        if not obj or not self.inDocumentContent(obj):
            return [None, -1]

        if obj.getRole() == pyatspi.ROLE_INVALID:
            debug.println(debug.LEVEL_SEVERE, \
                          "findNextCaretInOrder: object is invalid")
            return [None, -1]

        # We do not want to descend objects of certain role types.
        #
        doNotDescend = obj.getState().contains(pyatspi.STATE_FOCUSABLE) \
                       and obj.getRole() in [pyatspi.ROLE_COMBO_BOX,
                                             pyatspi.ROLE_LIST_BOX,
                                             pyatspi.ROLE_LIST,
                                             pyatspi.ROLE_PUSH_BUTTON,
                                             pyatspi.ROLE_TABLE_CELL,
                                             pyatspi.ROLE_TOGGLE_BUTTON,
                                             pyatspi.ROLE_TOOL_BAR]

        isHidden = self.utilities.isHidden(obj)
        isOffScreenLabel = self.utilities.isOffScreenLabel(obj, startOffset)
        skip = isHidden or isOffScreenLabel

        text = self.utilities.queryNonEmptyText(obj)
        if text and not skip:
            unicodeText = self.utilities.unicodeText(obj)

            # Delete the final space character if we find it.  Otherwise,
            # we'll arrow to it.  (We can't just strip the string otherwise
            # we skip over blank lines that one could otherwise arrow to.)
            #
            if len(unicodeText) > 1 and unicodeText[-1] == " ":
                unicodeText = unicodeText[0:len(unicodeText) - 1]

            nextOffset = startOffset + 1
            while 0 <= nextOffset < len(unicodeText):
                if unicodeText[nextOffset] != self.EMBEDDED_OBJECT_CHARACTER:
                    return [obj, nextOffset]
                elif obj.childCount:
                    try:
                        child = obj[self.getChildIndex(obj, nextOffset)]
                    except:
                        break
                    if child:
                        return self.findNextCaretInOrder(child,
                                                         -1,
                                                       includeNonText)
                    else:
                        nextOffset += 1
                else:
                    nextOffset += 1

        # If this is a list or combo box in an HTML form, we don't want
        # to place the caret inside the list, but rather treat the list
        # as a single object.  Otherwise, if it has children, look there.
        #
        elif obj.childCount and obj[0] and not doNotDescend and not skip:
            try:
                return self.findNextCaretInOrder(obj[0],
                                                 -1,
                                                 includeNonText)
            except:
                pass

        elif includeNonText and startOffset < 0 and not skip:
            extents = obj.queryComponent().getExtents(0)
            if (extents.width != 0) and (extents.height != 0):
                return [obj, 0]

        # If we're here, we need to start looking up the tree,
        # going no higher than the document frame, of course.
        #
        documentFrame = self.utilities.documentFrame()
        if self.utilities.isSameObject(obj, documentFrame):
            return [None, -1]

        while obj.parent and obj != obj.parent:
            characterOffsetInParent = \
                self.utilities.characterOffsetInParent(obj)
            if characterOffsetInParent >= 0:
                return self.findNextCaretInOrder(obj.parent,
                                                 characterOffsetInParent,
                                                 includeNonText)
            else:
                index = obj.getIndexInParent() + 1
                if index < obj.parent.childCount:
                    try:
                        return self.findNextCaretInOrder(
                            obj.parent[index],
                            -1,
                            includeNonText)
                    except:
                        pass
            obj = obj.parent

        return [None, -1]

    def findPreviousCaretInOrder(self,
                                 obj=None,
                                 startOffset=-1,
                                 includeNonText=True):
        """Given an object an a character offset, return the previous
        caret context following an in order traversal rule.

        Arguments:
        - root: the Accessible to start at.  If None, starts at the
        document frame.
        - startOffset: character position in the object text field
        (if it exists) to start at.  Defaults to -1, which means
        start at the end - that is, the previous character is the
        last character of the object.

        Returns [obj, characterOffset] or [None, -1]
        """

        if not obj:
            obj = self.utilities.documentFrame()

        if not obj or not self.inDocumentContent(obj):
            return [None, -1]

        if obj.getRole() == pyatspi.ROLE_INVALID:
            debug.println(debug.LEVEL_SEVERE, \
                          "findPreviousCaretInOrder: object is invalid")
            return [None, -1]

        # We do not want to descend objects of certain role types.
        #
        doNotDescend = obj.getState().contains(pyatspi.STATE_FOCUSABLE) \
                       and obj.getRole() in [pyatspi.ROLE_COMBO_BOX,
                                             pyatspi.ROLE_LIST_BOX,
                                             pyatspi.ROLE_LIST,
                                             pyatspi.ROLE_PUSH_BUTTON,
                                             pyatspi.ROLE_TABLE_CELL,
                                             pyatspi.ROLE_TOGGLE_BUTTON,
                                             pyatspi.ROLE_TOOL_BAR]

        isHidden = self.utilities.isHidden(obj)
        isOffScreenLabel = self.utilities.isOffScreenLabel(obj, startOffset)
        skip = isHidden or isOffScreenLabel

        text = self.utilities.queryNonEmptyText(obj)
        if text and not skip:
            unicodeText = self.utilities.unicodeText(obj)

            # Delete the final space character if we find it.  Otherwise,
            # we'll arrow to it.  (We can't just strip the string otherwise
            # we skip over blank lines that one could otherwise arrow to.)
            #
            if len(unicodeText) > 1 and unicodeText[-1] == " ":
                unicodeText = unicodeText[0:len(unicodeText) - 1]

            if (startOffset == -1) or (startOffset > len(unicodeText)):
                startOffset = len(unicodeText)
            previousOffset = startOffset - 1
            while previousOffset >= 0:
                if unicodeText[previousOffset] \
                    != self.EMBEDDED_OBJECT_CHARACTER:
                    return [obj, previousOffset]
                elif obj.childCount:
                    child = obj[self.getChildIndex(obj, previousOffset)]
                    if child:
                        return self.findPreviousCaretInOrder(child,
                                                             -1,
                                                             includeNonText)
                    else:
                        previousOffset -= 1
                else:
                    previousOffset -= 1

        # If this is a list or combo box in an HTML form, we don't want
        # to place the caret inside the list, but rather treat the list
        # as a single object.  Otherwise, if it has children, look there.
        #
        elif obj.childCount and obj[obj.childCount - 1] and not doNotDescend \
             and not skip:
            try:
                return self.findPreviousCaretInOrder(
                    obj[obj.childCount - 1],
                    -1,
                    includeNonText)
            except:
                pass

        elif includeNonText and startOffset < 0 and not skip:
            extents = obj.queryComponent().getExtents(0)
            if (extents.width != 0) and (extents.height != 0):
                return [obj, 0]

        # If we're here, we need to start looking up the tree,
        # going no higher than the document frame, of course.
        #
        documentFrame = self.utilities.documentFrame()
        if self.utilities.isSameObject(obj, documentFrame):
            return [None, -1]

        while obj.parent and obj != obj.parent:
            characterOffsetInParent = \
                self.utilities.characterOffsetInParent(obj)
            if characterOffsetInParent >= 0:
                return self.findPreviousCaretInOrder(obj.parent,
                                                     characterOffsetInParent,
                                                     includeNonText)
            else:
                index = obj.getIndexInParent() - 1
                if index >= 0:
                    try:
                        return self.findPreviousCaretInOrder(
                            obj.parent[index],
                            -1,
                            includeNonText)
                    except:
                        pass
            obj = obj.parent

        return [None, -1]

    def findPreviousObject(self, obj, documentFrame):
        if not obj:
            return None

        for relation in obj.getRelationSet():
            if relation.getRelationType() == pyatspi.RELATION_FLOWS_FROM:
                return relation.getTarget(0)

        if obj == documentFrame:
            obj, offset = self.getCaretContext()
            for child in documentFrame:
                if self.utilities.characterOffsetInParent(child) < offset:
                    return child

        index = obj.getIndexInParent() - 1
        if not 0 <= index < obj.parent.childCount:
            obj = obj.parent
            index = obj.getIndexInParent() - 1

        previousObj = obj.parent[index]
        while previousObj and previousObj.childCount:
            previousObj = previousObj[previousObj.childCount - 1]

        return previousObj

    def findNextObject(self, obj, documentFrame):
        if not obj:
            return None

        for relation in obj.getRelationSet():
            if relation.getRelationType() == pyatspi.RELATION_FLOWS_TO:
                return relation.getTarget(0)

        if obj == documentFrame:
            obj, offset = self.getCaretContext()
            for child in documentFrame:
                if self.utilities.characterOffsetInParent(child) > offset:
                    return child

        if obj and obj.childCount:
            return obj[0]

        nextObj = None
        while obj and not nextObj:
            index = obj.getIndexInParent() + 1
            if 0 < index < obj.parent.childCount:
                nextObj = obj.parent[index]
            elif obj.parent != documentFrame:
                obj = obj.parent
            else:
                break

        return nextObj

    ####################################################################
    #                                                                  #
    # Methods to get information about current object.                 #
    #                                                                  #
    ####################################################################

    def clearCaretContext(self):
        """Deletes all knowledge of a character context for the current
        document frame."""

        documentFrame = self.utilities.documentFrame()
        self._destroyLineCache()
        try:
            del self._documentFrameCaretContext[hash(documentFrame)]
        except:
            pass

    def setCaretContext(self, obj=None, characterOffset=-1):
        """Sets the caret context for the current document frame."""

        # We keep a context for each page tab shown.
        # [[[TODO: WDW - probably should figure out how to destroy
        # these contexts when a tab is killed.]]]
        #
        documentFrame = self.utilities.documentFrame()

        if not documentFrame:
            return

        self._documentFrameCaretContext[hash(documentFrame)] = \
            [obj, characterOffset]

    def getTextLineAtCaret(self, obj, offset=None, startOffset=None, endOffset=None):
        """To-be-removed. Returns the string, caretOffset, startOffset."""

        if self._inFocusMode or not self.inDocumentContent(obj) \
           or obj.getState().contains(pyatspi.STATE_EDITABLE):
            return super().getTextLineAtCaret(obj, offset, startOffset, endOffset)

        text = self.utilities.queryNonEmptyText(obj)
        if offset is None:
            try:
                offset = max(0, text.caretOffset)
            except:
                offset = 0

        if text and startOffset is not None and endOffset is not None:
            return text.getText(startOffset, endOffset), offset, startOffset

        contextObj, contextOffset = self.getCaretContext()
        if contextObj == obj:
            caretOffset = contextOffset
        else:
            caretOffset = offset

        contents = self.getLineContentsAtOffset(obj, offset)
        contents = list(filter(lambda x: x[0] == obj, contents))
        if len(contents) == 1:
            index = 0
        else:
            index = self.utilities.findObjectInContents(obj, offset, contents)

        if index > -1:
            candidate, startOffset, endOffset, string = contents[index]
            if not self.EMBEDDED_OBJECT_CHARACTER in string:
                return string, caretOffset, startOffset

        return '', 0, 0

    def searchForCaretLocation(self, acc):
        """Attempts to locate the caret on the page independent of our
        caret context. This functionality is needed when a page loads
        and the URL is for a fragment (anchor, id, named object) within
        that page.

        Arguments:
        - acc: The top-level accessible in which we suspect to find the
          caret (most likely the document frame).

        Returns the [obj, caretOffset] containing the caret if it can
        be determined. Otherwise [None, -1] is returned.
        """

        context = [None, -1]
        while acc:
            try:
                offset = acc.queryText().caretOffset
            except:
                acc = None
            else:
                context = [acc, offset]
                childIndex = self.getChildIndex(acc, offset)
                if childIndex >= 0 and acc.childCount:
                    acc = acc[childIndex]
                else:
                    break

        return context

    def getCaretContext(self, includeNonText=True):
        """Returns the current [obj, caretOffset] if defined.  If not,
        it returns the first [obj, caretOffset] found by an in order
        traversal from the beginning of the document."""

        # We keep a context for each page tab shown.
        # [[[TODO: WDW - probably should figure out how to destroy
        # these contexts when a tab is killed.]]]
        #
        documentFrame = self.utilities.documentFrame()

        if not documentFrame:
            return [None, -1]

        try:
            return self._documentFrameCaretContext[hash(documentFrame)]
        except:
            # If we don't have a context, we should attempt to see if we
            # can find the caret first. Failing that, we'll start at the
            # top.
            #
            [obj, caretOffset] = self.searchForCaretLocation(documentFrame)
            self._documentFrameCaretContext[hash(documentFrame)] = \
                self.findNextCaretInOrder(obj,
                                          max(-1, caretOffset - 1),
                                          includeNonText)

        [obj, caretOffset] = \
            self._documentFrameCaretContext[hash(documentFrame)]

        return [obj, caretOffset]

    def getCharacterAtOffset(self, obj, characterOffset):
        """Returns the character at the given characterOffset in the
        given object or None if the object does not implement the
        accessible text specialization.
        """

        try:
            unicodeText = self.utilities.unicodeText(obj)
            return unicodeText[characterOffset]
        except:
            return ""

    def getLineContentsAtOffset(self, obj, offset):
        if not obj:
            return []

        if self.utilities.findObjectInContents(obj, offset, self.currentLineContents) == -1:
            self.currentLineContents = self.utilities.getLineContentsAtOffset(
                obj, offset, _settingsManager.getSetting('layoutMode'))

        return self.currentLineContents

    def getObjectContentsAtOffset(self, obj, characterOffset):
        """Returns an ordered list where each element is composed of
        an [obj, startOffset, endOffset, string] tuple.  The list is 
        created via an in-order traversal of the document contents 
        starting and stopping at the given object.
        """

        return self.utilities.getObjectsFromEOCs(obj, characterOffset)

    ####################################################################
    #                                                                  #
    # Methods to speak current objects.                                #
    #                                                                  #
    ####################################################################

    def getUtterancesFromContents(self, contents, eliminatePauses=False):
        """Returns a list of [text, acss] tuples based upon the list
        of [obj, startOffset, endOffset, string] tuples passed in.

        Arguments:
        -contents: a list of [obj, startOffset, endOffset, string] tuples
        """

        if not len(contents):
            return []

        utterances = []
        contents = self.utilities.filterContentsForPresentation(contents, True)
        lastObj = None
        for content in contents:
            [obj, startOffset, endOffset, string] = content
            if not self.utilities.justEnteredObject(obj, startOffset, endOffset) \
               and not self.utilities.isTextBlockElement(obj):
                formatType = 'focused'
            else:
                formatType = 'unfocused'
            utterance = self.speechGenerator.generateSpeech(
                obj, startOffset=startOffset, endOffset=endOffset, string=string,
                formatType=formatType)
            if eliminatePauses:
                utterance = list(filter(lambda x: not isinstance(x, Pause), utterance))
            if utterance and utterance[0]:
                utterances.append(utterance)
            lastObj = obj

        # TODO - JD: This belongs in the generator.
        if lastObj and lastObj.getRole() != pyatspi.ROLE_HEADING:
            heading = self.utilities.ancestorWithRole(
                lastObj, [pyatspi.ROLE_HEADING], [pyatspi.ROLE_DOCUMENT_FRAME])
            if heading:
                utterance = self.speechGenerator.getRoleName(heading)
                utterances.append(utterance)

        if not utterances:
            if eliminatePauses:
                string = ""
            else:
                string = messages.BLANK
            utterances = [string, self.voices[settings.DEFAULT_VOICE]]

        return utterances

    def speakContents(self, contents):
        """Speaks each string in contents using the associated voice/acss"""

        speech.speak(self.getUtterancesFromContents(contents))

    def speakCharacterAtOffset(self, obj, characterOffset):
        """Speaks the character at the given characterOffset in the
        given object."""
        character = self.getCharacterAtOffset(obj, characterOffset)
        self.speakMisspelledIndicator(obj, characterOffset)
        if obj:
            if character and character != self.EMBEDDED_OBJECT_CHARACTER:
                self.speakCharacter(character)
            elif not obj.getState().contains(pyatspi.STATE_EDITABLE):
                # We won't have a character if we move to the end of an
                # entry (in which case we're not on a character and therefore
                # have nothing to say), or when we hit a component with no
                # text (e.g. checkboxes) or reset the caret to the parent's
                # characterOffset (lists).  In these latter cases, we'll just
                # speak the entire component.
                #
                utterances = self.speechGenerator.generateSpeech(obj)
                speech.speak(utterances)

    ####################################################################
    #                                                                  #
    # Methods to navigate to previous and next objects.                #
    #                                                                  #
    ####################################################################

    def setCaretPosition(self, obj, characterOffset):
        """Sets the caret position to the given character offset in the
        given object.
        """

        if self.flatReviewContext:
            self.toggleFlatReviewMode()

        self.setCaretContext(obj, characterOffset)
        if self._focusModeIsSticky:
            return

        try:
            state = obj.getState()
        except:
            return

        orca.setLocusOfFocus(None, obj, notifyScript=False)
        if state.contains(pyatspi.STATE_FOCUSABLE):
            obj.queryComponent().grabFocus()

        text = self.utilities.queryNonEmptyText(obj)
        if text:
            text.setCaretOffset(characterOffset)

        if self.useFocusMode(obj) != self._inFocusMode:
            self.togglePresentationMode(None)

        obj.clearCache()
        self._saveFocusedObjectInfo(obj)

    def moveToMouseOver(self, inputEvent):
        """Positions the caret offset to the next character or object
        in the mouse over which has just appeared.
        """

        if not self.lastMouseOverObject:
            self.presentMessage(messages.MOUSE_OVER_NOT_FOUND)
            return

        if not self.inMouseOverObject:
            obj = self.lastMouseOverObject
            offset = 0
            if obj and not obj.getState().contains(pyatspi.STATE_FOCUSABLE):
                [obj, offset] = self.findFirstCaretContext(obj, offset)

            if obj and obj.getState().contains(pyatspi.STATE_FOCUSABLE):
                obj.queryComponent().grabFocus()
            elif obj:
                contents = self.getObjectContentsAtOffset(obj, offset)
                # If we don't have anything to say, let's try one more
                # time.
                #
                if len(contents) == 1 and not contents[0][3].strip():
                    [obj, offset] = self.findNextCaretInOrder(obj, offset)
                    contents = self.getObjectContentsAtOffset(obj, offset)
                self.setCaretPosition(obj, offset)
                self.speakContents(contents)
                self.updateBraille(obj)
            self.inMouseOverObject = True
        else:
            # Route the mouse pointer where it was before both to "clean up
            # after ourselves" and also to get the mouse over object to go
            # away.
            #
            x, y = self.oldMouseCoordinates
            eventsynthesizer.routeToPoint(x, y)
            self.restorePreMouseOverContext()

    def restorePreMouseOverContext(self):
        """Cleans things up after a mouse-over object has been hidden."""

        obj, offset = self.preMouseOverContext
        if obj and not obj.getState().contains(pyatspi.STATE_FOCUSABLE):
            [obj, offset] = self.findFirstCaretContext(obj, offset)

        if obj and obj.getState().contains(pyatspi.STATE_FOCUSABLE):
            obj.queryComponent().grabFocus()
        elif obj:
            self.setCaretPosition(obj, offset)
            self.speakContents(self.getObjectContentsAtOffset(obj, offset))
            self.updateBraille(obj)
        self.inMouseOverObject = False
        self.lastMouseOverObject = None

    def goNextCharacter(self, inputEvent):
        """Positions the caret offset to the next character or object
        in the document window.
        """
        [obj, characterOffset] = self.getCaretContext()
        while obj:
            [obj, characterOffset] = self.findNextCaretInOrder(obj,
                                                               characterOffset)
            if obj and obj.getState().contains(pyatspi.STATE_VISIBLE):
                break

        if not obj:
            [obj, characterOffset] = self.getBottomOfFile()

        self.setCaretPosition(obj, characterOffset)
        self.speakCharacterAtOffset(obj, characterOffset)
        self.updateBraille(obj)

    def goPreviousCharacter(self, inputEvent):
        """Positions the caret offset to the previous character or object
        in the document window.
        """
        [obj, characterOffset] = self.getCaretContext()
        while obj:
            [obj, characterOffset] = self.findPreviousCaretInOrder(
                obj, characterOffset)
            if obj and obj.getState().contains(pyatspi.STATE_VISIBLE):
                break

        if not obj:
            [obj, characterOffset] = self.getTopOfFile()

        self.setCaretPosition(obj, characterOffset)
        self.speakCharacterAtOffset(obj, characterOffset)
        self.updateBraille(obj)

    def goPreviousWord(self, inputEvent):
        """Positions the caret offset to beginning of the previous
        word or object in the document window.
        """

        [obj, characterOffset] = self.getCaretContext()

        # Make sure we have a word.
        #
        [obj, characterOffset] = \
            self.findPreviousCaretInOrder(obj, characterOffset)

        contents = self.utilities.getWordContentsAtOffset(obj, characterOffset)
        if not len(contents):
            return

        [obj, startOffset, endOffset, string] = contents[0]
        if len(contents) == 1 \
           and endOffset - startOffset == 1 \
           and self.getCharacterAtOffset(obj, startOffset) == " ":
            # Our "word" is just a space. This can happen if the previous
            # word was a mark of punctuation surrounded by whitespace (e.g.
            # " | ").
            #
            [obj, characterOffset] = \
                self.findPreviousCaretInOrder(obj, startOffset)
            contents = self.utilities.getWordContentsAtOffset(obj, characterOffset)
            if len(contents):
                [obj, startOffset, endOffset, string] = contents[0]

        self.setCaretPosition(obj, startOffset)
        self.updateBraille(obj)
        self.speakMisspelledIndicator(obj, startOffset)
        self.speakContents(contents)

    def goNextWord(self, inputEvent):
        """Positions the caret offset to the end of next word or object
        in the document window.
        """

        [obj, characterOffset] = self.getCaretContext()

        # Make sure we have a word.
        #
        characterOffset = max(0, characterOffset)
        [obj, characterOffset] = \
            self.findNextCaretInOrder(obj, characterOffset)

        contents = self.utilities.getWordContentsAtOffset(obj, characterOffset)
        if not (len(contents) and contents[-1][2]):
            return

        [obj, startOffset, endOffset, string] = contents[-1]
        if string and string[-1].isspace():
            endOffset -= 1
        self.setCaretPosition(obj, endOffset)
        self.updateBraille(obj)
        self.speakMisspelledIndicator(obj, startOffset)
        self.speakContents(contents)

    def goPreviousLine(self, inputEvent):
        """Positions the caret offset at the previous line in the document
        window, attempting to preserve horizontal caret position.

        Returns True if we actually moved.
        """

        if self._inSayAll \
           and _settingsManager.getSetting('rewindAndFastForwardInSayAll'):
            return True

        [obj, characterOffset] = self.getCaretContext()
        thisLine = self.getLineContentsAtOffset(obj, characterOffset)
        if not (thisLine and thisLine[0]):
            return False

        startObj, startOffset = thisLine[0][0], thisLine[0][1]
        prevObj, prevOffset = self.findPreviousCaretInOrder(startObj, startOffset)
        if prevObj == startObj:
            prevObj, prevOffset = self.findPreviousCaretInOrder(prevObj, prevOffset)

        if not prevObj:
            return False

        prevLine = self.getLineContentsAtOffset(prevObj, prevOffset)
        if prevLine:
            prevObj, prevOffset = prevLine[0][0], prevLine[0][1]

        [obj, caretOffset] = self.findFirstCaretContext(prevObj, prevOffset)
        self.setCaretPosition(obj, caretOffset)
        self.presentLine(prevObj, prevOffset)

        return True

    def goNextLine(self, inputEvent):
        """Positions the caret offset at the next line in the document
        window, attempting to preserve horizontal caret position.

        Returns True if we actually moved.
        """

        if self._inSayAll \
           and _settingsManager.getSetting('rewindAndFastForwardInSayAll'):
            return True

        [obj, characterOffset] = self.getCaretContext()
        thisLine = self.getLineContentsAtOffset(obj, characterOffset)
        if not (thisLine and thisLine[0]):
            return False

        lastObj, lastOffset = thisLine[-1][0], thisLine[-1][2]
        nextObj, nextOffset = self.findNextCaretInOrder(lastObj, lastOffset - 1)
        if nextObj and self.getCharacterAtOffset(nextObj, nextOffset).isspace():
            nextObj, nextOffset = self.findNextCaretInOrder(nextObj, nextOffset)

        if not nextObj:
            return False

        nextLine = self.getLineContentsAtOffset(nextObj, nextOffset)
        if nextLine:
            nextObj, nextOffset = nextLine[0][0], nextLine[0][1]

        [obj, caretOffset] = self.findFirstCaretContext(nextObj, nextOffset)
        self.setCaretPosition(obj, caretOffset)
        self.presentLine(nextObj, nextOffset)

        return True

    def goBeginningOfLine(self, inputEvent):
        """Positions the caret offset at the beginning of the line."""

        [obj, characterOffset] = self.getCaretContext()
        line = self.getLineContentsAtOffset(obj, characterOffset)
        obj, characterOffset = self.findFirstCaretContext(line[0][0], line[0][1])
        self.setCaretPosition(obj, characterOffset)
        if not isinstance(orca_state.lastInputEvent, input_event.BrailleEvent):
            self.speakCharacterAtOffset(obj, characterOffset)
        self.updateBraille(obj)

    def goEndOfLine(self, inputEvent):
        """Positions the caret offset at the end of the line."""

        [obj, characterOffset] = self.getCaretContext()
        line = self.getLineContentsAtOffset(obj, characterOffset)
        obj, characterOffset = line[-1][0], line[-1][2] - 1
        self.setCaretPosition(obj, characterOffset)
        if not isinstance(orca_state.lastInputEvent, input_event.BrailleEvent):
            self.speakCharacterAtOffset(obj, characterOffset)
        self.updateBraille(obj)

    def goTopOfFile(self, inputEvent):
        """Positions the caret offset at the beginning of the document."""

        [obj, characterOffset] = self.getTopOfFile()
        self.setCaretPosition(obj, characterOffset)
        self.presentLine(obj, characterOffset)

    def goBottomOfFile(self, inputEvent):
        """Positions the caret offset at the end of the document."""

        [obj, characterOffset] = self.getBottomOfFile()
        self.setCaretPosition(obj, characterOffset)
        self.presentLine(obj, characterOffset)

    def advanceLivePoliteness(self, inputEvent):
        """Advances live region politeness level."""
        if _settingsManager.getSetting('inferLiveRegions'):
            self.liveMngr.advancePoliteness(orca_state.locusOfFocus)
        else:
            self.presentMessage(messages.LIVE_REGIONS_OFF)

    def monitorLiveRegions(self, inputEvent):
        if not _settingsManager.getSetting('inferLiveRegions'):
            _settingsManager.setSetting('inferLiveRegions', True)
            self.presentMessage(messages.LIVE_REGIONS_MONITORING_ON)
        else:
            _settingsManager.setSetting('inferLiveRegions', False)
            self.liveMngr.flushMessages()
            self.presentMessage(messages.LIVE_REGIONS_MONITORING_OFF)

    def setLivePolitenessOff(self, inputEvent):
        if _settingsManager.getSetting('inferLiveRegions'):
            self.liveMngr.setLivePolitenessOff()
        else:
            self.presentMessage(messages.LIVE_REGIONS_OFF)

    def reviewLiveAnnouncement(self, inputEvent):
        if _settingsManager.getSetting('inferLiveRegions'):
            self.liveMngr.reviewLiveAnnouncement( \
                                    int(inputEvent.event_string[1:]))
        else:
            self.presentMessage(messages.LIVE_REGIONS_OFF)

    def enableStickyFocusMode(self, inputEvent):
        self._inFocusMode = True
        self._focusModeIsSticky = True
        self.presentMessage(messages.MODE_FOCUS_IS_STICKY)

    def togglePresentationMode(self, inputEvent):
        if self._inFocusMode:
            [obj, characterOffset] = self.getCaretContext()
            try:
                parentRole = obj.parent.getRole()
            except:
                parentRole = None
            if parentRole == pyatspi.ROLE_LIST_BOX:
                self.setCaretContext(obj.parent, -1)
            elif parentRole == pyatspi.ROLE_MENU:
                self.setCaretContext(obj.parent.parent, -1)

            self.presentMessage(messages.MODE_BROWSE)
        else:
            self.presentMessage(messages.MODE_FOCUS)
        self._inFocusMode = not self._inFocusMode
        self._focusModeIsSticky = False

    def toggleCaretNavigation(self, inputEvent):
        """Toggles between Firefox native and Orca caret navigation."""

        if _settingsManager.getSetting('caretNavigationEnabled'):
            for keyBinding in self.__getArrowBindings().keyBindings:
                self.keyBindings.removeByHandler(keyBinding.handler)
            _settingsManager.setSetting('caretNavigationEnabled', False)
            string = messages.CARET_CONTROL_GECKO
        else:
            _settingsManager.setSetting('caretNavigationEnabled', True)
            for keyBinding in self.__getArrowBindings().keyBindings:
                self.keyBindings.add(keyBinding)
            string = messages.CARET_CONTROL_ORCA

        debug.println(debug.LEVEL_CONFIGURATION, string)
        self.presentMessage(string)

    def speakWordUnderMouse(self, acc):
        """Determine if the speak-word-under-mouse capability applies to
        the given accessible.

        Arguments:
        - acc: Accessible to test.

        Returns True if this accessible should provide the single word.
        """
        if self.inDocumentContent(acc):
            try:
                ai = acc.queryAction()
            except NotImplementedError:
                return True
        default.Script.speakWordUnderMouse(self, acc)
