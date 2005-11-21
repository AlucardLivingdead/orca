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

"""Provides an abtract class for working with speech servers.

A speech server (class SpeechServer) provides the ability to tell the
machine to speak.  Each speech server provides a set of known
voices (identified by name) which can be combined with various
attributes to create aural style sheets.
"""

class VoiceFamily(dict):
    """Holds the family description for a voice."""

    NAME   = "name"
    GENDER = "gender"
    LOCALE = "locale"

    MALE   = "male"
    FEMALE = "female"

    settings = {
        NAME   : None,
        GENDER : None,
        LOCALE : None
    }

    def __init__(self, props):
        """Create and initialize VoiceFamily."""
        self.update(VoiceFamily.settings)
        if props:
            self.update(props)

class SpeechServer:

    """Provides speech server abstraction."""

    def getFactoryName():
 	"""Returns a localized name describing this factory."""
	pass

    getFactoryName = staticmethod(getFactoryName)

    def getSpeechServerInfos():
        """Enumerate available speech servers.

        Returns a list of [name, id] values identifying the available
        speech servers.  The name is a human consumable string and the
	id is an object that can be used to create a speech server
	via the getSpeechServer method.
        """
        pass

    getSpeechServerInfos = staticmethod(getSpeechServerInfos)

    def getSpeechServer(info):
        """Gets a given SpeechServer based upon the info.
        """
        pass

    getSpeechServer = staticmethod(getSpeechServer)

    def __init__(self):
        pass

    def getInfo(self):
        """Returns [name, id]
        """
        pass

    def getVoiceFamilies(self):
        """Returns a list of VoiceFamily instances representing all
        voice families known by the speech server."""
        pass

    def queueText(self, text="", acss=None):
        """Adds the text to the queue.

        Arguments:
        - text: text to be spoken
        - acss: acss.ACSS instance; if None,
		the default voice settings will be used.
		Otherwise, the acss settings will be
		used to augment/override the default
		voice settings.

        Output is produced by the next call to speak.
        """
        pass

    def queueTone(self, pitch=440, duration=50):
        """Adds a tone to the queue.

        Output is produced by the next call to speak.
        """
        pass

    def queueSilence(self, duration=50):
        """Adds silence to the queue.

        Output is produced by the next call to speak.
        """
        pass

    def speakCharacter(self, character, acss=None):
        """Speaks a single character immediately.

        Arguments:
        - character: text to be spoken
        - acss:      acss.ACSS instance; if None,
		     the default voice settings will be used.
		     Otherwise, the acss settings will be
		     used to augment/override the default
		     voice settings.
        """
        pass

    def speakUtterances(self, list, acss=None):
        """Speaks the given list of utterances immediately.

        Arguments:
        - list: list of strings to be spoken
        - acss: acss.ACSS instance; if None,
		the default voice settings will be used.
		Otherwise, the acss settings will be
		used to augment/override the default
		voice settings.
        """
        pass

    def speak(self, text=None, acss=None):
        """Speaks all queued text immediately.  If text is not None,
        it is added to the queue before speaking.

        Arguments:
        - text: text to be spoken
        - acss: acss.ACSS instance; if None,
		the default voice settings will be used.
		Otherwise, the acss settings will be
		used to augment/override the default
		voice settings.
        """
        pass

    def increaseSpeechRate(self, step=5):
        """Increases the speech rate.
        """
        pass

    def decreaseSpeechRate(self, step=5):
        """Decreases the speech rate.
        """
        pass

    def stop(self):
        """Stops ongoing speech and flushes the queue."""
        pass

    def shutdown(self):
        """Shuts down the speech engine."""
        pass
