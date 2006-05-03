# Orca
#
# Copyright 2004-2006 Sun Microsystems Inc.
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

"""Manages the settings for Orca.  This will defer to user settings first, but
fallback to local settings if the user settings doesn't exist (e.g., in the
case of gdm) or doesn't have the specified attribute.
"""

import re
import sys

import debug
from acss import ACSS
from orca_i18n import _           # for gettext support

# These are the settings that Orca supports the user customizing.
#
userCustomizableSettings = [
    "orcaModifierKeys",
    "enableSpeech",
    "speechServerFactory",
    "speechServerInfo",
    "voices",
    "speechVerbosityLevel",
    "enableEchoByWord",
    "enableKeyEcho",
    "enablePrintableKeys",
    "enableModifierKeys",
    "enableLockingKeys",
    "enableFunctionKeys",
    "enableActionKeys",
    "enableBraille",
    "brailleVerbosityLevel",
    "brailleRolenameStyle",
    "enableBrailleMonitor",
    "enableMagnifier",
    "magX",
    "magY",
    "verbalizePunctuationStyle",
]

# The name of the modules that hold the user interface for setting
# Orca preferences.  Each module is expected to have the method,
# showPreferencesUI, which will prompt the user for preferences.
#
guiPreferencesModule    = "orca_gui_prefs"
consolePreferencesModule= "orca_console_prefs"

# A list of keys that can serve as the Orca modifier key.  The list is
# so we can provide better cross platform support (e.g., Sun keyboard
# vs. PC-104 keyboard layouts).  When any of these keys is pressed,
# the orca.MODIFIER_ORCA bit will be set in the 'modifiers' field of
# a KeyboardEvent input event.  The keys are currently compared to the
# event_string of a keyboard input event from AT-SPI.
#
orcaModifierKeys        = ["Insert", "KP_Insert"]

# Verbosity levels (see setBrailleVerbosityLevel and
# setSpeechVerbosityLevel).  These will have an impact on the various
# individual verbosity levels for rolenames, accelerators, etc.
#
VERBOSITY_LEVEL_BRIEF   = 0
VERBOSITY_LEVEL_VERBOSE = 1
speechVerbosityLevel    = VERBOSITY_LEVEL_VERBOSE
brailleVerbosityLevel   = VERBOSITY_LEVEL_VERBOSE

BRAILLE_ROLENAME_STYLE_SHORT = 0 # three letter abbreviations
BRAILLE_ROLENAME_STYLE_LONG  = 1 # full rolename
brailleRolenameStyle    = BRAILLE_ROLENAME_STYLE_LONG

# Speech punctuation levels (see verbalizePunctuationStyle).
#
PUNCTUATION_STYLE_NONE = 0
PUNCTUATION_STYLE_SOME = 1
PUNCTUATION_STYLE_ALL  = 2
verbalizePunctuationStyle = PUNCTUATION_STYLE_ALL

# The absolue amount to change the speech rate when
# increasing or decreasing speech.  This is a numerical
# value that represents an ACSS rate value.
#
speechRateDelta         = 5

# If True, enable speech.
#
enableSpeech            = True
enableSpeechCallbacks   = True

# If True, speech has been temporarily silenced.
#
silenceSpeech           = False

# Settings that apply to the particular speech engine to
# use as well details on the default voices to use.
#
speechFactoryModules    = ["espeechfactory","gnomespeechfactory"]
speechServerFactory     = "gnomespeechfactory"
speechServerInfo        = None # None means let the factory decide.

DEFAULT_VOICE           = "default"
UPPERCASE_VOICE         = "uppercase"
HYPERLINK_VOICE         = "hyperlink"

voices = {
    DEFAULT_VOICE   : ACSS({}),
    UPPERCASE_VOICE : ACSS({ACSS.AVERAGE_PITCH : 6}),
    HYPERLINK_VOICE : ACSS({ACSS.AVERAGE_PITCH : 8})
}

# If True, enable braille.
#
enableBraille           = True

# If True, enable braille monitor.
#
enableBrailleMonitor    = False

# If True, enable magnification.
#
enableMagnifier         = False
magX                    = 1.5
magY                    = 1.5

# if True, enable word echo.
# Note that it is allowable for both enableEchoByWord and enableKeyEcho
# to be True
#
enableEchoByWord        = False

# If True, enable key echo.
# Note that it is allowable for both enableEchoByWord and enableKeyEcho
# to be True
#
enableKeyEcho           = False

# If True and key echo is enabled, echo Alphanumeric and punctuation keys.
#
enablePrintableKeys     = True

# If True and key echo is enabled, echo Modifier keys.
#
enableModifierKeys      = True

# If True and key echo is enabled, echo Locking keys.
#
enableLockingKeys       = True

# If True and key echo is enabled, echo Function keys.
#
enableFunctionKeys      = True

# If True and key echo is enabled, echo Action keys.
#
enableActionKeys        = True


# If True, reads all the table cells in the current row rather than just
# the current one.
#
readTableCellRow        = False

# Script developer feature.  If False, just the default script
# will be used.  Helps determine difference between custom
# scripts and the default script behavior.
#
enableCustomScripts     = True

# Latent support to allow the user to override/define keybindings
# and braille bindings.  Unsupported and undocumented for now.
# Use at your own risk.
#
keyBindingsMap          = {}
brailleBindingsMap      = {}

# Script developer feature.  If False, no AT-SPI object values
# will be cached locally.  Helps determine if there might be a
# problem related to the cache being out of sync with the real
# objects.
#
cacheValues             = True

# Assists with learn mode (what you enter when you press Insert+F1
# and exit when you press escape.
#
learnModeEnabled        = False

# Which packages to search, and the order in which to search,
# for custom scripts.  These packages are expected to be on
# the PYTHONPATH and/or subpackages of the "orca" package.
# REMEMBER: to make something a package, the directory has to
# have a __init__.py file in it.
#
scriptPackages          = ["orca-scripts", "scripts"]

# A list that helps us map application names to script module
# names.  The key is the name of an application, and the value is
# the name of a script module.  There are some default values here,
# but one may call the setScriptMapping method of this module to
# extend or override any mappings.
#
_scriptMappings = []

def setScriptMapping(regExpression, moduleName):
    """Tells this module what script module to look for a given
    application name.  The mappings are stored as a list and each
    new mapping is added to the beginning of the list, meaning it
    takes precedence over all other mappings.

    Arguments:
    - regExpression: a regular expression used to match against an
                     application name
    - moduleName:    the name of the Python module containing the script
                     class definition for the application
    """

    _scriptMappings.insert(0, [regExpression, moduleName])

def getScriptModuleName(app):
    """Returns the module name of the script to use for a given
    application.  Any script mapping set via the setScriptMapping
    method is searched first, with the ultimate fallback being the
    name of the application itself.

    Arguments:
    - app: the application to find a script module name for
    """

    for mapping in _scriptMappings:
        regExpression = mapping[0]
        moduleName = mapping[1]
        if regExpression.match(app.name):
            debug.println(
                debug.LEVEL_FINEST,
                "Script mapping for %s is %s" % (app.name, moduleName))
            return moduleName

    return app.name

# Note to translators: the regular expression here represents a
# string to match in the localized application name as seen by
# at-poke.  For most cases, the application name is the name of
# the binary used to start the application, but this is an
# unreliable assumption.  The only reliable way to do the
# translation is by running the application and then viewing its
# name in the main window of at-poke.
#
setScriptMapping(re.compile(_('[\S\s]*StarOffice[\s\S]*')), "StarOffice")
setScriptMapping(re.compile(_('soffice.bin')), "StarOffice")
setScriptMapping(re.compile(_('[Ee]volution')), "Evolution")
setScriptMapping(re.compile(_('Deer Park')), "Mozilla")
setScriptMapping(re.compile(_('Bon Echo')), "Mozilla")
