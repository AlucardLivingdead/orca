# - coding: utf-8 -

# Copyright (C) 2010, J. Félix Ontañón <felixonta@gmail.com>
# Copyright (C) 2011, J. Ignacio Álvarez <neonigma@gmail.com>

# This file is part of Pluglib.

# Pluglib is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pluglib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pluglib.  If not, see <http://www.gnu.org/licenses/>.

import time
from pluglib.interfaces import *
import input_event as input_event

from settings_manager import SettingsManager

from orca_i18n import _         # for gettext support
from orca_i18n import ngettext  # for ngettext support
from orca_i18n import C_        # to provide qualified translatable strings

import notification_messages as notification_messages
print notification_messages

class callPresenter(IPresenter):
    inputEventHandlers = {}

    _settingsManager = SettingsManager()
    if _settingsManager is None:
        print "Could not load the settings manager. Exiting."
        sys.exit(1)

    def __init__(self):

        print "Init call presenter..."
        self.inputEventHandlers["presentTimeHandler"] = \
            input_event.InputEventHandler(
                callPresenter.presentTime,
                # Translators: Orca can present the current time to the
                # user when the user presses
                # a shortcut key.
                #
                _("Present current time."))

        self.inputEventHandlers["presentDateHandler"] = \
            input_event.InputEventHandler(
                callPresenter.presentDate,
                # Translators: Orca can present the current date to the
                # user when the user presses
                # a shortcut key.
                #
                _("Present current date."))
        
        self.inputEventHandlers.update(notification_messages.inputEventHandlers)

    def presentTime(self, inputEvent):
        """ Presents the current time. """
        timeFormat = self._settingsManager.getSetting('presentTimeFormat')
        message = time.strftime(timeFormat, time.localtime())
        super(callPresenter, self).presentMessage(message)
        return True

    def presentDate(self, inputEvent):
        """ Presents the current date. """
        dateFormat = self._settingsManager.getSetting('presentDateFormat')
        message = time.strftime(dateFormat, time.localtime())
        super(callPresenter, self).presentMessage(message)
        return True

class testPlugin(IPlugin, IPresenter):
    name = 'Test Plugin'
    description = 'A testing plugin for code tests' 
    version = '0.1pre'
    authors = ['J. Félix Ontañón <felixonta@gmail.com>', 'J. Ignacio Álvarez <neonigma@gmail.com>']
    website = 'http://fontanon.org'
    icon = 'gtk-missing-image'

    def __init__(self):
        print 'Hello World (plugin started)!'
        cp = callPresenter()



IPlugin.register(testPlugin)
