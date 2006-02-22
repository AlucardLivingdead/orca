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

"""Provides a SpeechServer factory for gnome-speech drivers.
"""

import bonobo

import atspi
import debug
import settings
import speech
import speechserver

from acss import ACSS
from chnames import chnames

from orca_i18n import _           # for gettext support

atspi.ORBit.load_typelib('GNOME_Speech')
import GNOME.Speech, GNOME__POA.Speech

class _SayAll:
    def __init__(self, iterator, context, id, progressCallback):
        self.utteranceIterator   = iterator
        self.currentContext      = context
        self.idForCurrentContext = id
        self.progressCallback    = progressCallback
                 
class _Speaker(GNOME__POA.Speech.SpeechCallback):
    """Implements gnome-speech's SpeechCallback class.  The gnome-speech
    server only allows one speech callback to be registered with a speaker
    and there's no way to unregister it.  So...we need to handle stuff
    like that on our own.  This class handles this for us and also delegates
    all calls to the 'real' gnome speech speaker.
    """

    def __init__(self, gnome_speaker):
        self.gnome_speaker = gnome_speaker
        if settings.getSetting("enableSpeechCallbacks", True):
            gnome_speaker.registerSpeechCallback(self._this())
        self.__callbacks = []
        
    def registerCallback(self, callback):
        self.__callbacks.append(callback)

    def deregisterCallback(self, callback):
        self.__callbacks.remove(callback)
        
    def notify(self, type, id, offset):
        """Called by GNOME Speech when the GNOME Speech driver generates
        a callback.

        Arguments:
        - type:   one of GNOME.Speech.speech_callback_speech_started,
                         GNOME.Speech.speech_callback_speech_progress,
                         GNOME.Speech.speech_callback_speech_ended
        - id:     the id of the utterance (returned by say)
        - offset: the character offset into the utterance (for progress)
        """
        for callback in self.__callbacks:
            callback.notify(type, id, offset)

    def say(self, text):
        return self.gnome_speaker.say(text)

    def stop(self):
        self.gnome_speaker.stop()
        
    def getSupportedParameters(self):
        return self.gnome_speaker.getSupportedParameters()
    
    def getParameterValue(self, name):
        return self.gnome_speaker.getParameterValue(name)

    def setParameterValue(self, name, value):
        return self.gnome_speaker.setParameterValue(name, value)

    def unref(self):
        try:
            self.gnome_speaker.unref()
        except:
            pass
        
class SpeechServer(speechserver.SpeechServer):
    """Provides SpeechServer implementation for gnome-speech."""

    def __activateDriver(iid):
        driver = bonobo.activation.activate_from_id(iid,
                                                    0,
                                                    False)
        driver = driver._narrow(GNOME.Speech.SynthesisDriver)
        isInitialized = driver.isInitialized()
        if not isInitialized:
            isInitialized = driver.driverInit()
        if not isInitialized:
            driver = None
	return driver

    __activateDriver = staticmethod(__activateDriver)

    def getFactoryName():
        """Returns a localized name describing this factory."""
        return _("GNOME Speech Services")

    getFactoryName = staticmethod(getFactoryName)

    def getSpeechServerInfos():
        """Enumerate available speech servers.

        Returns a list of [name, id] values identifying the available
        speech servers.  The name is a human consumable string and the
        id is an object that can be used to create a speech server
        via the getSpeechServer method.
        """

        # Get a list of all the drivers on the system and find out how many
        # of them work.
        #
        servers = bonobo.activation.query(
            "repo_ids.has('IDL:GNOME/Speech/SynthesisDriver:0.3')")

        speechServerInfos = []

        for server in servers:
            try:
                driver = SpeechServer.__activateDriver(server.iid)
                if driver:
                    speechServerInfos.append([driver.driverName, server.iid])
            except:
                debug.printException(debug.LEVEL_WARNING)

        return speechServerInfos

    getSpeechServerInfos = staticmethod(getSpeechServerInfos)

    def getSpeechServer(info=None):
        """
        """
	server = None

        gservers = bonobo.activation.query(
            "repo_ids.has('IDL:GNOME/Speech/SynthesisDriver:0.3')")

        if len(gservers) == 0:
            return None

        gserver = None

        # All this logic is to attempt to fall back to a working
        # driver if the desired one cannot be found or is not
        # not working.
        #
	if not info:
	    gserver = gservers[0]
	else:
            for s in gservers:
                if s.iid == info[1]:
		    gserver = s
		    break

	if not gserver:
	    return server

	try:
	    driver = SpeechServer.__activateDriver(gserver.iid)
	    server = SpeechServer(driver, gserver.iid)
	except:
	    if info:
		return server
	    for s in gservers:
		try:
		    driver = SpeechServer.__activateDriver(s.iid)
	            if driver:
		        server = SpeechServer(driver, s.iid)
		except:
		    debug.printException(debug.LEVEL_WARNING)
		    pass

	return server

    getSpeechServer = staticmethod(getSpeechServer)

    def __init__(self, driver, iid):
        speechserver.SpeechServer.__init__(self)
        self.__speakers   = {}
        self.__pitchInfo  = {}
        self.__rateInfo   = {}
        self.__volumeInfo = {}
        self.__driver = driver
        self.__driverName = driver.driverName
	self.__iid = iid
        self.__sayAll = None
        
    def __getRate(self, speaker):
        """Gets the voice-independent ACSS rate value of a voice."""

	if not self.__rateInfo.has_key(speaker):
	    return 50

	[minRate, averageRate, maxRate] = self.__rateInfo[speaker]
	rate = speaker.getParameterValue("rate")
	if rate < averageRate:
	    return int(((rate - minRate) / (averageRate - minRate)) * 50)
	elif rate > averageRate:
  	    return 50 \
                   + int(((rate - averageRate) / (maxRate - averageRate)) * 50)
	else:
	    return 50

    def __setRate(self, speaker, acssRate):
	"""Determines the voice-specific rate setting for the
	voice-independent ACSS rate value.
	"""

	if not self.__rateInfo.has_key(speaker):
	    return

	[minRate, averageRate, maxRate] = self.__rateInfo[speaker]
	if acssRate < 50:
	    rate = minRate + acssRate * (averageRate - minRate) / 50
	elif acssRate > 50:
	    rate = averageRate \
		   + (acssRate - 50) * (maxRate - averageRate) / 50
	else:
	    rate = averageRate

	speaker.setParameterValue("rate", rate)

    def __setPitch(self, speaker, acssPitch):
	"""Determines the voice-specific pitch setting for the
	voice-independent ACSS pitch value.
	"""

	if not self.__pitchInfo.has_key(speaker):
	    return

	[minPitch, averagePitch, maxPitch] = self.__pitchInfo[speaker]
	if acssPitch < 5:
	    pitch = minPitch + acssPitch * (averagePitch - minPitch) / 5
	elif acssPitch > 5:
	    pitch = averagePitch \
                    + (acssPitch - 5) * (maxPitch - averagePitch) / 5
	else:
	    pitch = averagePitch

	speaker.setParameterValue("pitch", pitch)

    def __setVolume(self, speaker, acssGain):
	"""Determines the voice-specific rate setting for the
	voice-independent ACSS rate value.
	"""

	if not self.__volumeInfo.has_key(speaker):
	    return

	[minVolume, averageVolume, maxVolume] = self.__volumeInfo[speaker]
	volume = minVolume + acssGain * (maxVolume - minVolume) / 10

	speaker.setParameterValue("volume", volume)

    def __getSpeaker(self, acss=None):

        voices = settings.getSetting(settings.VOICES, None)
	defaultACSS = voices[settings.DEFAULT_VOICE]

	if not acss:
	    acss = defaultACSS

        if self.__speakers.has_key(acss.name()):
            return self.__speakers[acss.name()]

	# Create a new voice for all unique ACSS's we see.
	#
	familyName = None
	if acss.has_key(ACSS.FAMILY):
	    family = acss[ACSS.FAMILY]
            familyName = family[speechserver.VoiceFamily.NAME]
	elif defaultACSS.has_key(ACSS.FAMILY):
	    family = defaultACSS[ACSS.FAMILY]
            familyName = family[speechserver.VoiceFamily.NAME]

        voices = self.__driver.getAllVoices()
        found = False
        for voice in voices:
            if (not familyName) or (voice.name == familyName):
                found = True
                break

        if not found:
            return None

        s = self.__driver.createSpeaker(voice)
        speaker = _Speaker(s._narrow(GNOME.Speech.Speaker))
        speaker.registerCallback(self)
        
	parameters = speaker.getSupportedParameters()
	for parameter in parameters:
	    if parameter.name == "rate":
		self.__rateInfo[speaker] = \
		    [parameter.min, parameter.current, parameter.max]
	    elif parameter.name == "pitch":
		self.__pitchInfo[speaker] = \
		    [parameter.min, parameter.current, parameter.max]
	    elif parameter.name == "volume":
		self.__volumeInfo[speaker] = \
		    [parameter.min, parameter.current, parameter.max]

        if acss.has_key(ACSS.RATE):
            self.__setRate(speaker, acss[ACSS.RATE])

        if acss.has_key(ACSS.AVERAGE_PITCH):
            self.__setPitch(speaker, acss[ACSS.AVERAGE_PITCH])

        if acss.has_key(ACSS.GAIN):
            self.__setVolume(speaker, acss[ACSS.GAIN])

        self.__speakers[acss.name()] = speaker

	return speaker

    def notify(self, type, id, offset):
        """Called by GNOME Speech when the GNOME Speech driver generates
        a callback.  This is for internal use only.

        Arguments:
        - type:   one of GNOME.Speech.speech_callback_speech_started,
                         GNOME.Speech.speech_callback_speech_progress,
                         GNOME.Speech.speech_callback_speech_ended
        - id:     the id of the utterance (returned by say)
        - offset: the character offset into the utterance (for progress)
        """
        if self.__sayAll:
            if self.__sayAll.idForCurrentContext == id:
                context = self.__sayAll.currentContext
                if type == GNOME.Speech.speech_callback_speech_started:
                    context.currentOffset = context.startOffset
                    self.__sayAll.progressCallback(
                        self.__sayAll.currentContext,
                        speechserver.SayAllContext.PROGRESS)
                elif type == GNOME.Speech.speech_callback_speech_progress:
                    context.currentOffset = context.startOffset + offset
                    self.__sayAll.progressCallback(
                        self.__sayAll.currentContext,
                        speechserver.SayAllContext.PROGRESS)
                elif type == GNOME.Speech.speech_callback_speech_ended:
                    try:
                        [self.__sayAll.currentContext, acss] = \
                            self.__sayAll.utteranceIterator.next()
                        self.__sayAll.idForCurrentContext = self.__speak(
                            self.__sayAll.currentContext.utterance,
                            acss)
                    except StopIteration:
                        context.currentOffset = context.endOffset
                        self.__sayAll.progressCallback(
                            self.__sayAll.currentContext,
                            speechserver.SayAllContext.COMPLETED)
                        self.__sayAll = None

    def getInfo(self):
        """Returns [driverName, serverId]
        """
        return [self.__driverName, self.__iid]

    def getVoiceFamilies(self):
        """Returns a list of speechserver.VoiceFamily instances
        representing all the voice families known by the speech server.
        """

        families = []
        try:
            for voice in self.__driver.getAllVoices():
                props = {
                    speechserver.VoiceFamily.NAME   : voice.name,
                    speechserver.VoiceFamily.LOCALE : voice.language
                }
                families.append(speechserver.VoiceFamily(props))
        except:
            debug.printException(debug.LEVEL_SEVERE)
            pass

        return families

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
        self.speak(text, acss)

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
        self.speak(character, acss)

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
        i = 0
        for text in list:
            self.speak(text, acss, i == 0)
            i += 1

    def __speak(self, text=None, acss=None, interrupt=True):
        """Speaks all queued text immediately.  If text is not None,
        it is added to the queue before speaking.

        Arguments:
        - text:      optional text to add to the queue before speaking
        - acss:      acss.ACSS instance; if None,
		     the default voice settings will be used.
		     Otherwise, the acss settings will be
		     used to augment/override the default
		     voice settings.
        - interrupt: if True, stops any speech in progress before
                     speaking the text

        Returns an id of the thing being spoken or -1 if nothing is to
        be spoken.
        """

        speaker = self.__getSpeaker(acss)
        if acss and not acss.has_key(ACSS.RATE):
            voices = settings.getSetting(settings.VOICES, None)
            defaultACSS = voices[settings.DEFAULT_VOICE]
	    if defaultACSS.has_key(ACSS.RATE):
                self.__setRate(speaker, defaultACSS[ACSS.RATE])

        if not text:
            if interrupt:
                speech.stop()
            return -1

        # If the text to speak is a single character, see if we have a
        # customized character pronunciation
        #
        if len(text) == 1:
            try:
                text = chnames[text.lower()]
            except:
                pass
        else:
            text = text.replace("...", _(" dot dot dot"), 1)

        # Send the text to the GNOME Speech speaker
        #
        debug.println(debug.LEVEL_INFO, "SPEECH OUTPUT: '" + text + "'")

        try:
            # [[[TODO: WDW - back this stop out for now.  The problem is
            # that we end up clipping too much speech, especially in the
            # case where we want to speak the contents of a popup before
            # speaking the object with focus.]]]
            #
            #if interrupt:
            #    speaker.stop()
            self.__lastText = [text, acss]
            return speaker.say(text)
        except:
            # On failure, remember what we said, reset our connection to the
            # speech synthesis driver, and try to say it again.
            #
            debug.printException(debug.LEVEL_SEVERE)
            debug.println(debug.LEVEL_SEVERE, "Restarting speech...")
            self.reset()
            return -1
        
    def speak(self, text=None, acss=None, interrupt=True):
        """Speaks all queued text immediately.  If text is not None,
        it is added to the queue before speaking.

        Arguments:
        - text:      optional text to add to the queue before speaking
        - acss:      acss.ACSS instance; if None,
		     the default voice settings will be used.
		     Otherwise, the acss settings will be
		     used to augment/override the default
		     voice settings.
        - interrupt: if True, stops any speech in progress before
                     speaking the text

        Returns an id of the thing being spoken or -1 if nothing is to
        be spoken.
        """
        print "HERE",text
        if self.__sayAll:
            self.stop()

        self.__speak(text, acss, interrupt)

    def sayAll(self, utteranceIterator, progressCallback):
        """Iterates through the given utteranceIterator, speaking
        each utterance one at a time.

        Arguments:
        - utteranceIterator: iterator/generator whose next() function
                             returns a new string to be spoken
        - progressCallback:  called as progress is made
        """
        try:
            [context, acss] = utteranceIterator.next()
            self.__sayAll = _SayAll(utteranceIterator,
                                    context,
                                    self.__speak(context.utterance, acss),
                                    progressCallback)
        except StopIteration:
            pass
            
    def increaseSpeechRate(self, step=5):
        """Increases the speech rate.

        [[[TODO: WDW - this is a hack for now.  Need to take min/max
        values in account, plus also need to take into account that
        different engines provide different rate ranges.]]]
        """

        voices = settings.getSetting(settings.VOICES, None)
        acss = voices[settings.DEFAULT_VOICE]
	speaker = self.__getSpeaker(acss)

        rateDelta = settings.getSetting(settings.SPEECH_RATE_DELTA,
                                        step)

	try:
            rate = min(100, self.__getRate(speaker) + rateDelta)
	    acss[ACSS.RATE] = rate
	    self.__setRate(speaker, rate)
            debug.println(debug.LEVEL_CONFIGURATION,
            	          "speech.increaseSpeechRate: rate is now " \
                          " %d" % rate)
            self.speak(_("faster."))
        except:
            debug.printException(debug.LEVEL_SEVERE)

    def decreaseSpeechRate(self, step=5):
        """Decreases the rate of speech for the given ACSS.  If
        acssName is None, the rate decrease will be applied to all
        known ACSSs.

        [[[TODO: WDW - this is a hack for now.  Need to take min/max
        values in account, plus also need to take into account that
        different engines provide different rate ranges.]]]

        Arguments:
        -acssName: the ACSS whose speech rate should be decreased
        """

        voices = settings.getSetting(settings.VOICES, None)
	acss = voices[settings.DEFAULT_VOICE]
	speaker = self.__getSpeaker(acss)

        rateDelta = settings.getSetting(settings.SPEECH_RATE_DELTA,
                                        step)

	try:
            rate = max(1, self.__getRate(speaker) - rateDelta)
	    acss[ACSS.RATE] = rate
	    self.__setRate(speaker, rate)
            debug.println(debug.LEVEL_CONFIGURATION,
            	          "speech.decreaseSpeechRate: rate is now " \
                          " %d" % rate)
            self.speak(_("slower."))
        except:
            debug.printException(debug.LEVEL_SEVERE)

    def stop(self):
        """Stops ongoing speech and flushes the queue."""
        if self.__sayAll:
            self.__sayAll.progressCallback(
                self.__sayAll.currentContext,
                speechserver.SayAllContext.INTERRUPTED)
            self.__sayAll = None
        for name in self.__speakers.keys():
            try:
                self.__speakers[name].stop()
            except:
                pass

    def shutdown(self):
        """Shuts down the speech engine."""
        for speaker in self.__speakers.values():
            speaker.unref()
        self.__speakers = {}
        try:
            self.__driver.unref()
        except:
            pass

        self.__driver = None

    def reset(self, text=None, acss=None):
        """Resets the speech engine."""

        speakers = self.__speakers
        self.shutdown()

        servers = bonobo.activation.query(
            "repo_ids.has('IDL:GNOME/Speech/SynthesisDriver:0.3')")

        for server in servers:
	    if server.iid == self.__iid:
                try:
                    self.__driver = self.__activateDriver(self.__iid)
                    self.__speakers = {}
                    for name in speakers.keys():
                        self.__getSpeaker(speakers[name])
                    if text:
                        self.speak(text, acss)
                    break
                except:
                    debug.printException(debug.LEVEL_SEVERE)
                    self.__driver = None
                    pass
