# Orca
#
# Copyright 2006 Sun Microsystems Inc.
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

# TODO:
#
# - Adjust routines names to start with _ when only used in this module.
# - Improve reclaimation of "old" speech servers in setupServers().
# - Implement the Help button callback.
# - Need to add comments to each method.

"""Displays a GUI for the user to set Orca preferences."""

import os
import sys
import debug
import gettext
import gtk
import gtk.glade
import locale

import acss
import orca
import orca_prefs
import platform
import settings
import speech as speech
import speechserver as speechserver

from orca_i18n import _  # for gettext support

OS = None

class GladeWrapper:
    """
    Superclass for glade based applications. Just derive from this
    and your subclass should create methods whose names correspond to
    the signal handlers defined in the glade file. Any other attributes
    in your class will be safely ignored.

    This class will give you the ability to do:
        subclass_instance.GtkWindow.method(...)
        subclass_instance.widget_name...
    """

    def __init__(self, Filename, WindowName):
        # Load glade file.
        self.widgets = gtk.glade.XML(Filename, WindowName, gettext.textdomain())
        self.GtkWindow = getattr(self, WindowName)

        instance_attributes = {}
        for attribute in dir(self.__class__):
            instance_attributes[attribute] = getattr(self, attribute)
        self.widgets.signal_autoconnect(instance_attributes)

    def __getattr__(self, attribute):   # Called when no attribute in __dict__
        widget = self.widgets.get_widget(attribute)
        if widget is None:
            raise AttributeError("Widget [" + attribute + "] not found")
        self.__dict__[attribute] = widget   # Add reference to cache.

        return widget

class orcaSetupGUI(GladeWrapper):

    def _init(self):
        """Initialize the Orca configuration GUI. Read the users current
        set of preferences and set the GUI state to match. Setup speech
        support and populate the combo box lists on the Speech Tab pane 
        accordingly.
        """

        self.initializing = True
        self.prefsDict = orca_prefs.readPreferences()
        self.defaultVoice   = self.prefsDict["voices"]["default"]
        self.uppercaseVoice = self.prefsDict["voices"]["uppercase"]
        self.hyperlinkVoice = self.prefsDict["voices"]["hyperlink"]

        self.speechSystemsModel = self.initComboBox(self.speechSystems)
        self.speechServersModel = self.initComboBox(self.speechServers)
        self.voicesModel = self.initComboBox(self.voices)

        self.setKeyEchoItems()

        # Use this because callbacks will often hang when not running
        # with bonobo main in use.
        #
        settings.enableSpeechCallbacks = False

        factories = speech.getSpeechServerFactories()
        if len(factories) == 0:
            self.prefsDict["enableSpeech"] = False
            return

        speech.init()

        workingFactories = []
        for self.factory in factories:
            try:
                self.factoryInfos = \
                    self.factory.SpeechServer.getSpeechServerInfos()
                workingFactories.append([self.factory, self.factoryInfos])
            except:
                pass

        if debug.debugLevel <= debug.LEVEL_FINEST:
            print "orca_gui_prefs._init: workingFactories: ", workingFactories

        self.factoryChoices = {}
        if len(workingFactories) == 0:
            debug.println(debug.LEVEL_SEVERE, _("Speech not available."))
            debug.printStack(debug.LEVEL_FINEST)
            self.prefsDict["enableSpeech"] = False
            return
        elif len(workingFactories) > 1:
            i = 1
            for workingFactory in workingFactories:
                self.factoryChoices[i] = workingFactory
                name = workingFactory[0].SpeechServer.getFactoryName()
                self.speechSystemsModel.append((i, name))
                i += 1
            [self.factory, self.factoryInfos] = self.factoryChoices[1]
        else:
            self.factoryChoices[1] = workingFactories[0]
            name = workingFactories[0][0].SpeechServer.getFactoryName()
            self.speechSystemsModel.append((1, name))
            [self.factory, self.factoryInfos] = workingFactories[0]

        if debug.debugLevel <= debug.LEVEL_FINEST:
            print "orca_gui_prefs._init: factoryChoices: ", self.factoryChoices
            print "orca_gui_prefs._init: factoryInfos: ", self.factoryInfos
            print "orca_gui_prefs._init: factory: ", self.factory

        self.serverChoices = None
        self.setupServers(self.factory)
        self.setupVoices(self.server)
        self.prefsDict["enableSpeech"] = True
        self.initGUIState()
        self.initializing = False

    def setVoiceSettingForVoiceType(self, voiceType):
        familyName = self.getFamilyNameForVoiceType(voiceType)
        if familyName:
            self.setVoiceChoice(self.families, familyName)

        rate = self.getRateForVoiceType(voiceType)
        if rate:
            self.rateScale.set_value(rate)

        pitch = self.getPitchForVoiceType(voiceType)
        if pitch:
            self.pitchScale.set_value(pitch)

        volume = self.getVolumeForVoiceType(voiceType)
        if volume:
            self.volumeScale.set_value(volume)

    def initGUIState(self):
        prefs = self.prefsDict

        # Speech pane.
        #
        self.setSystemChoice(self.factoryChoices, prefs["speechServerFactory"])

        serverPrefs = prefs["speechServerInfo"]
        if serverPrefs:
            self.setServerChoice(self.serverChoices, serverPrefs[0])

        voiceType = self.voiceType.get_active_text()
        self.voiceType.set_active(0)
        self.setVoiceSettingForVoiceType(voiceType)

        if prefs["verbalizePunctuationStyle"] == \
                               settings.PUNCTUATION_STYLE_NONE:
            self.noneButton.set_active(True)
        elif prefs["verbalizePunctuationStyle"] == \
                               settings.PUNCTUATION_STYLE_SOME:
            self.someButton.set_active(True)
        else:
            self.allButton.set_active(True)

        if prefs["speechVerbosityLevel"] == _("Brief"):
            self.speechBriefButton.set_active(True)
        else:
            self.speechVerboseButton.set_active(True)

        # Braille pane.
        #
        self.brailleSupportCheckbutton.set_active(prefs["enableBraille"])
        self.brailleMonitorCheckbutton.set_active(prefs["enableBrailleMonitor"])
        state = prefs["brailleRolenameStyle"] == \
                            settings.BRAILLE_ROLENAME_STYLE_SHORT
        self.abbrevRolenames.set_active(state)
        if prefs["brailleVerbosityLevel"] == _("Brief"):
            self.brailleBriefButton.set_active(True)
        else:
            self.brailleVerboseButton.set_active(True)

        # Key Echo pane.
        #
        self.keyEchoCheckbutton.set_active(prefs["enableKeyEcho"])
        self.printableCheckbutton.set_active(prefs["enablePrintableKeys"])
        self.modifierCheckbutton.set_active(prefs["enableModifierKeys"])
        self.lockingCheckbutton.set_active(prefs["enableLockingKeys"])
        self.functionCheckbutton.set_active(prefs["enableFunctionKeys"])
        self.actionCheckbutton.set_active(prefs["enableActionKeys"])
        self.echoByWordCheckbutton.set_active(prefs["enableEchoByWord"])

    def setupServers(self, factory):
        self.factoryInfos = factory.SpeechServer.getSpeechServerInfos()
        self.servers = []
        for info in self.factoryInfos:
            try:
                self.server = self.factory.SpeechServer.getSpeechServer(info)
                if self.server:
                    self.servers.append(self.server)
            except:
                pass

        self.serverChoices = {}
        if len(self.servers) == 0:
            debug.println(debug.LEVEL_SEVERE, _("Speech not available."))
            debug.printStack(debug.LEVEL_FINEST)
            self.prefsDict["enableSpeech"] = False
            return
        if len(self.servers) > 1:
            i = 1
            for self.server in self.servers:
                self.serverChoices[i] = self.server
                name = self.server.getInfo()[0]
                self.speechServersModel.append((i, name))
                i += 1
            self.server = self.serverChoices[1]
        else:
            self.serverChoices[1] = self.servers[0]
            name = self.servers[0].getInfo()[0]
            self.speechServersModel.append((1, name))
            self.server = self.servers[0]

        self.speechServers.set_active(0)

        if debug.debugLevel <= debug.LEVEL_FINEST:
            print "orca_gui_prefs.setupServers: serverChoices: ", \
                   self.serverChoices
            print "orca_gui_prefs.setupServers: server: ", self.server

    def setupVoices(self, server):
        self.families = server.getVoiceFamilies()

        self.voiceChoices = {}
        if len(self.families) == 0:
            debug.println(debug.LEVEL_SEVERE, _("Speech not available."))
            debug.printStack(debug.LEVEL_FINEST)
            self.prefsDict["enableSpeech"] = False
            return
        if len(self.families) > 1:
            i = 1
            for family in self.families:
                name = family[speechserver.VoiceFamily.NAME]
                self.acss = acss.ACSS({acss.ACSS.FAMILY : family})
                self.voiceChoices[i] = self.acss
                self.voicesModel.append((i, name))
                i += 1
            self.defaultACSS = self.voiceChoices[1]
        else:
            name = self.families[0][speechserver.VoiceFamily.NAME]
            self.voicesModel.append((1, name))
            self.defaultACSS = \
                acss.ACSS({acss.ACSS.FAMILY : self.families[0]})
            self.voiceChoices[1] = self.defaultACSS

        if not self.initializing:
            self.voices.set_active(0)

        if debug.debugLevel <= debug.LEVEL_FINEST:
            print "orca_gui_prefs.setupVoices: voiceChoices: ", \
                   self.voiceChoices

    def getVoiceForVoiceType(self, voiceType):
        if voiceType == _("Default"):
            voice = self.defaultVoice
        elif voiceType == _("Uppercase"):
            voice = self.uppercaseVoice
        elif voiceType == _("Hyperlink"):
            voice = self.hyperlinkVoice
        else:
            voice = self.defaultVoice

        return voice

    def getKeyForVoiceType(self, voiceType, key, useDefault=True):
        """Look for the value of the given key, in the voice dictionary
           for the given voice type.

        Arguments:
        - voiceType: the voice type (Default, Uppercase or Hyperlink).
        - key: the key to look for in the voice dictionary.
        - useDefault: if True, and the key isn't found for the given voice
                      type, the look for it in the default voice dictionary 
                      as well.

        Returns the value of the given key.
        """

        if voiceType == _("Default"):
            voice = self.defaultVoice
        elif voiceType == _("Uppercase"):
            voice = self.uppercaseVoice
            if not voice.has_key(key):
                if not useDefault:
                    return None
                voice = self.defaultVoice
        elif voiceType == _("Hyperlink"):
            voice = self.hyperlinkVoice
            if not voice.has_key(key):
                if not useDefault:
                    return None
                voice = self.defaultVoice
        else:
            voice = self.defaultVoice

        if voice.has_key(key):
            return voice[key]
        else:
            return None

    def getFamilyNameForVoiceType(self, voiceType):
        familyName = None
        family = self.getKeyForVoiceType(voiceType, "family")

        if family:
            if family.has_key("name"):
                familyName = family["name"]

        return familyName

    def setFamilyNameForVoiceType(self, voiceType, value):
        family = self.getKeyForVoiceType(voiceType, "family", False)
        if family:
            family["name"] = value
        else:
            voice = self.getVoiceForVoiceType(voiceType)
            voice["family"] = {}
            voice["family"]["name"] = value

    def getRateForVoiceType(self, voiceType):
        return self.getKeyForVoiceType(voiceType, "rate", True)

    def setRateForVoiceType(self, voiceType, value):
        voice = self.getVoiceForVoiceType(voiceType)
        voice["rate"] = value

    def getPitchForVoiceType(self, voiceType):
        return self.getKeyForVoiceType(voiceType, "average-pitch", True)

    def setPitchForVoiceType(self, voiceType, value):
        voice = self.getVoiceForVoiceType(voiceType)
        voice["average-pitch"] = value

    def getVolumeForVoiceType(self, voiceType):
        return self.getKeyForVoiceType(voiceType, "gain", True)

    def setVolumeForVoiceType(self, voiceType, value):
        voice = self.getVoiceForVoiceType(voiceType)
        voice["gain"] = value

    def setSystemChoice(self, factoryChoices, systemName):
        model = self.speechSystemsModel
        i = 1
        for factory in factoryChoices.values():
            name = factory[0].__name__
            if name == systemName:
                self.speechSystems.set_active(i-1)
                return
            i += 1

    def setServerChoice(self, serverChoices, serverName):
        model = self.speechServersModel
        i = 1
        for server in serverChoices.values():
            name = server.getInfo()[0]
            if name == serverName:
                self.speechServers.set_active(i-1)
                return
            i += 1

    def setVoiceChoice(self, families, voiceName):
        model = self.voicesModel
        i = 1
        for family in families:
            name = family[speechserver.VoiceFamily.NAME]
            if name == voiceName:
                self.voices.set_active(i-1)
                return
            i += 1

    def showGUI(self):
        self.orcaSetupWindow.show()

    def initComboBox(self, combobox):
        cell = gtk.CellRendererText()
        combobox.pack_start(cell, True)
        combobox.add_attribute(cell, 'text', 1)
        model = gtk.ListStore(int, str)
        combobox.set_model(model)

        return model

    def setKeyEchoItems(self):
        if self.keyEchoCheckbutton.get_active():
            enable = True
        else:
            enable = False
        self.printableCheckbutton.set_sensitive(enable)
        self.modifierCheckbutton.set_sensitive(enable)
        self.lockingCheckbutton.set_sensitive(enable)
        self.functionCheckbutton.set_sensitive(enable)
        self.actionCheckbutton.set_sensitive(enable)

    def speechSystemsChanged(self, widget):
        iter = widget.get_active_iter()
        model = widget.get_model()

        index = model.get_value(iter, 0)
        self.factory = self.factoryChoices[index][0]
        self.speechServersModel.clear()
        self.setupServers(self.factory)

        self.server = self.serverChoices[1]
        self.setupVoices(self.server)

    def speechServersChanged(self, widget):
        iter = widget.get_active_iter()
        model = widget.get_model()

        index = model.get_value(iter, 0)
        self.voicesModel.clear()
        self.server = self.serverChoices[index]
        self.setupVoices(self.server)

    def voiceFamilyChanged(self, widget):
        iter = widget.get_active_iter()
        model = widget.get_model()

        name = model.get_value(iter, 1)
        voiceType = self.voiceType.get_active_text()
        self.setFamilyNameForVoiceType(voiceType, name)

    def brailleSupportChecked(self, widget):
        self.prefsDict["enableBraille"] = widget.get_active()

    def brailleMonitorChecked(self, widget):
        self.prefsDict["enableBrailleMonitor"] = widget.get_active()

    def keyEchoChecked(self, widget):
        self.prefsDict["enableKeyEcho"] = widget.get_active()
        self.setKeyEchoItems()

    def printableKeysChecked(self, widget):
        self.prefsDict["enablePrintableKeys"] = widget.get_active()

    def modifierKeysChecked(self, widget):
        self.prefsDict["enableModifierKeys"] = widget.get_active()

    def lockingKeysChecked(self, widget):
        self.prefsDict["enableLockingKeys"] = widget.get_active()

    def functionKeysChecked(self, widget):
        self.prefsDict["enableFunctionKeys"] = widget.get_active()

    def actionKeysChecked(self, widget):
        self.prefsDict["enableActionKeys"] = widget.get_active()

    def echoByWordChecked(self, widget):
        self.prefsDict["enableEchoByWord"] = widget.get_active()

    def voiceTypeChanged(self, widget):
        voiceType = widget.get_active_text()
        self.setVoiceSettingForVoiceType(voiceType)

    def rateValueChanged(self, widget):
        rate = widget.get_value()
        voiceType = self.voiceType.get_active_text()
        self.setRateForVoiceType(voiceType, rate)

    def pitchValueChanged(self, widget):
        pitch = widget.get_value()
        voiceType = self.voiceType.get_active_text()
        self.setPitchForVoiceType(voiceType, pitch)

    def volumeValueChanged(self, widget):
        volume = widget.get_value()
        voiceType = self.voiceType.get_active_text()
        self.setVolumeForVoiceType(voiceType, volume)

    def punctuationLevelChanged(self, widget):
        if widget.get_active():
            if widget.get_label() == _("None"):
                self.prefsDict["verbalizePunctuationStyle"] = \
                    settings.PUNCTUATION_STYLE_NONE
            elif widget.get_label() == _("Some"):
                self.prefsDict["verbalizePunctuationStyle"] = \
                    settings.PUNCTUATION_STYLE_SOME
            else:
                self.prefsDict["verbalizePunctuationStyle"] = \
                    settings.PUNCTUATION_STYLE_ALL

    def speechVerbosityChanged(self, widget):
        if widget.get_active():
            if widget.get_label() == _("Brief"):
                self.prefsDict["speechVerbosityLevel"] = \
                    settings.VERBOSITY_LEVEL_BRIEF
            else:
                self.prefsDict["speechVerbosityLevel"] = \
                    settings.VERBOSITY_LEVEL_VERBOSE


    def abbrevRolenamesChecked(self, widget):
        if widget.get_active():
            self.prefsDict["brailleRolenameStyle"] = \
                settings.BRAILLE_ROLENAME_STYLE_SHORT
        else:
            self.prefsDict["brailleRolenameStyle"] = \
                settings.BRAILLE_ROLENAME_STYLE_LONG

    def brailleVerbosityChanged(self, widget):
        if widget.get_active():
            if widget.get_label() == _("Brief"):
                self.prefsDict["brailleVerbosityLevel"] = \
                    settings.VERBOSITY_LEVEL_BRIEF
            else:
                self.prefsDict["brailleVerbosityLevel"] = \
                    settings.VERBOSITY_LEVEL_VERBOSE

    def helpButtonClicked(self, widget):
        print "Help not currently implemented."

    def cancelButtonClicked(self, widget):
        self.orcaSetupWindow.hide()

    def applyButtonClicked(self, widget):

        self.voices = {
            settings.DEFAULT_VOICE   : self.defaultVoice,
            settings.UPPERCASE_VOICE : self.uppercaseVoice,
            settings.HYPERLINK_VOICE : self.hyperlinkVoice
        }

        self.prefsDict["enableSpeech"] = True
        self.prefsDict["speechServerFactory"] = self.factory
        self.prefsDict["speechServerInfo"] = self.server
        self.prefsDict["voices"] = self.voices

        if orca_prefs.writePreferences(self.prefsDict):
            self.say(_("Accessibility support for GNOME has just been enabled."))
            self.say(_("You need to log out and log back in for the change to take effect."))

        orca.loadUserSettings()
        self.orcaSetupWindow.hide()

    def windowDestroyed(self, widget):
        global OS

        OS = None

    def say(text, stop=False):
        if stop:
            speech.stop()

        speech.speak(text)


def showPreferencesUI():
    global OS

    if not OS:
        gladeFile = os.path.join(platform.prefix,
                                 platform.datadirname,
                                 platform.package,
                                 "glade",
                                 "orca-setup.glade")
        OS = orcaSetupGUI(gladeFile, "orcaSetupWindow")
        OS._init()
    else:
        OS.showGUI()

def main():
    locale.setlocale(locale.LC_ALL, '')

    showPreferencesUI()

    gtk.main()
    sys.exit(0)

if __name__ == "__main__":
    main()
