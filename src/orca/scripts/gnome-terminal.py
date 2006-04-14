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

import orca.default as default
import orca.util as util
import orca.orca as orca

########################################################################
#                                                                      #
# The GnomeTerminal script class.                                      #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for the given application.

        Arguments:
        - app: the application to create a script for.
        """

        default.Script.__init__(self, app)

    def onWindowActivated(self, event):
        # Sets the context to the top level window first, so we can
        # get information about it the window we just moved to.
        #
        orca.setLocusOfFocus(event, event.source)

        # Now we find the focused object and set the locus of focus to it.
        #
        obj = util.findFocusedObject(self.app)
        if obj:
            orca.setLocusOfFocus(event, obj)
        else:
            default.Script.onWindowActivated(self, event)
