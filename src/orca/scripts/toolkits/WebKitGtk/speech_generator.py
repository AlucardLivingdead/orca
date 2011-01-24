# Orca
#
# Copyright (C) 2010 Joanmarie Diggs
#
# Author: Joanmarie Diggs <joanied@gnome.org>
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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs"
__license__   = "LGPL"

import pyatspi

import orca.rolenames as rolenames
import orca.speech_generator as speech_generator

from orca.orca_i18n import _

########################################################################
#                                                                      #
# Custom SpeechGenerator                                               #
#                                                                      #
########################################################################

class SpeechGenerator(speech_generator.SpeechGenerator):
    """Provides a speech generator specific to WebKitGtk widgets."""

    def __init__(self, script):
        speech_generator.SpeechGenerator.__init__(self, script)

    def _generateRoleName(self, obj, **args):
        result = []
        acss = self.voice(speech_generator.SYSTEM)
        role = args.get('role', obj.getRole())
        force = args.get('force', False)

        doNotSpeak = [pyatspi.ROLE_UNKNOWN]
        if not force:
            doNotSpeak.extend([pyatspi.ROLE_FORM,
                               pyatspi.ROLE_LABEL,
                               pyatspi.ROLE_MENU_ITEM,
                               pyatspi.ROLE_PARAGRAPH,
                               pyatspi.ROLE_SECTION,
                               pyatspi.ROLE_TABLE_CELL])

        if not (role in doNotSpeak):
            if role == pyatspi.ROLE_IMAGE:
                link = self._script.utilities.ancestorWithRole(
                    obj, [pyatspi.ROLE_LINK], [pyatspi.ROLE_DOCUMENT_FRAME])
                if link:
                    result.append(rolenames.getSpeechForRoleName(link))

            if role == pyatspi.ROLE_HEADING:
                level = self._script.utilities.headingLevel(obj)
                if level:
                    # Translators: the %(level)d is in reference to a heading
                    # level in HTML (e.g., For <h3>, the level is 3)
                    # and the %(role)s is in reference to a previously
                    # translated rolename for the heading.
                    #
                    result.append(_("%(role)s level %(level)d") % {
                        'role': rolenames.getSpeechForRoleName(obj, role),
                        'level': level})
                else:
                    result.append(rolenames.getSpeechForRoleName(obj, role))
            else:
                result.append(rolenames.getSpeechForRoleName(obj, role))

            if result:
                result.extend(acss)

            if role == pyatspi.ROLE_LINK \
               and obj.childCount and obj[0].getRole() == pyatspi.ROLE_IMAGE:
                # If this is a link with a child which is an image, we
                # want to indicate that.
                #
                acss = self.voice(speech_generator.HYPERLINK)
                result.append(rolenames.getSpeechForRoleName(obj[0]))
                result.extend(acss)

        return result
