# Orca
#
# Copyright 2004-2007 Sun Microsystems Inc.
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

""" Custom script for Thunderbird 3.
"""

__id__        = "$Id: $"
__version__   = "$Revision: $"
__date__      = "$Date: $"
__copyright__ = "Copyright (c) 2005-2007 Sun Microsystems Inc."
__license__   = "LGPL"

import orca.atspi as atspi
import orca.debug as debug
import orca.default as default
import orca.rolenames as rolenames
import orca.settings as settings
import orca.speech as speech
import orca.util as util
import orca.Gecko as Gecko

from orca.orca_i18n import _


########################################################################
#                                                                      #
# The Thunderbird script class.                                        #
#                                                                      #
########################################################################

class Script(Gecko.Script):

    _containingPanelName = ""

    def __init__(self, app):
        """ Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        # Set the debug level for all the methods in this script.
        #
        self.debugLevel = debug.LEVEL_FINEST

        Gecko.Script.__init__(self, app)


    def _debug(self, msg):
        """ Convenience method for printing debug messages
        """
        debug.println(self.debugLevel, "Thunderbird.py: "+msg)


    def onFocus(self, event):
        """ Called whenever an object gets focus.

        Arguments:
        - event: the Event
        
        """
        obj = event.source
        top = util.getTopLevel(obj)
        consume = False

        self._debug("onFocus: name='%s', role='%s', top name='%s', top role='%s'" \
                    % (obj.name, obj.role, top.name, top.role))

        # Don't speak a chrome URL.
        if obj.name.startswith("_(chrome://"):
            return

        # Handle dialogs.
        if top.role == rolenames.ROLE_DIALOG:

            self._speakEnclosingPanel(obj)

            if obj.role == rolenames.ROLE_ENTRY:
                consume = self._handleTextEntry(obj)

        if not consume:
            Gecko.Script.onFocus(self, event)
            

    def _speakEnclosingPanel(self, obj):
        # Speak the enclosing panel if it is named. Going two
        # containers up the hierarchy appears to be far enough
        # to find a named panel, if there is one.
        
        self._debug("_speakEnclosingPanel")

        parent = obj.parent
        if not parent:
            return
        
        if parent.name != "" and \
               (not parent.name.startswith(_("chrome://"))) and \
               parent.role == rolenames.ROLE_PANEL:
            
            # Speak the panel name only once.
            if parent.name != self._containingPanelName:
                self._containingPanelName = parent.name
                utterances = []
                text = _("%s panel") % parent.name
                utterances.append(text)
                speech.speakUtterances(utterances)
            
        else:
            grandparent = parent.parent
            if grandparent and \
                   grandparent.name != "" and \
                   (not grandparent.name.startswith(_("chrome://"))) and \
                   grandparent.role == rolenames.ROLE_PANEL:
                
                # Speak the panel name only once.
                if grandparent.name != self._containingPanelName:
                    self._containingPanelName = grandparent.name
                    utterances = []
                    text = _("%s panel") % grandparent.name
                    utterances.append(text)
                    speech.speakUtterances(utterances)

                        
    def _handleTextEntry(self, obj):
        # Handle preferences that contain editable text fields. If
        # the object with keyboard focus is editable text field,
        # examine the previous and next sibling to get the order
        # for speaking the preference objects.
        #
        # Returns whether to consume the event.
        
        self._debug("_handleTextEntry: childCount=%d, index=%d" % \
                    (obj.parent.childCount, obj.index))

        if not obj.text:
            return False
        
        if obj.index > 0:
            prev = obj.parent.child(obj.index - 1)
            self._debug("_handleTextEntry: prev='%s', role='%s'" \
                    % (prev.name, prev.role))
            
        if obj.parent.childCount > obj.index:
            next = obj.parent.child(obj.index + 1)
            self._debug("_handleTextEntry: next='%s', role='%s'" \
                    % (next.name, next.role))

        # Get the entry text.
        [word, startOffset, endOffset] = obj.text.getTextAtOffset(0,
            atspi.Accessibility.TEXT_BOUNDARY_LINE_START)
        if len(word) == 0:
            # The above may incorrectly return an empty string
            # if the entry contains a single character.
            [word, startOffset, endOffset] = obj.text.getTextAtOffset(0,
                atspi.Accessibility.TEXT_BOUNDARY_CHAR)

        self._debug("_handleTextEntry: word='%s'" % word)

        # Determine the order for speaking the component parts.
        if len(word) > 0:
            if prev and prev.role == rolenames.ROLE_LABEL:
                if next and next.role == rolenames.ROLE_LABEL:
                    text = _("%s text %s %s") % (obj.name, word, next.name)
                else:
                    text = _("%s text %s") % (obj.name, word)
            else:
                if next and next.role == rolenames.ROLE_LABEL:
                    text = _("%s text %s %s") % (obj.name, word, next.name)
                else:
                    text = _("text %s %s") % (word, obj.name)
                    
            speech.speakUtterances([text])
            return True

        return False
