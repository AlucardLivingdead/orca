#!/usr/bin/python

"""Test of menu checkbox output using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Open the "View" menu.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>v"))
sequence.append(utils.AssertPresentationAction(
    "View menu",
    ["BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar View Menu'",
     "     VISIBLE:  'View Menu', cursor=1",
     "BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar Toolbars Menu'",
     "     VISIBLE:  'Toolbars Menu', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'View menu'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Toolbars menu'"]))

########################################################################
# When focus is on Toolbars, Up Arrow to the "Full Screen" check menu
# item. The following should be presented in speech and braille:
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Up Arrow in View menu",
    ["BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar < > Full Screen CheckItem(F11)'",
     "     VISIBLE:  '< > Full Screen CheckItem(F11)', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Full Screen check item not checked F11'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  'Minefield Application Minefield Frame ToolBar Application MenuBar < > Full Screen CheckItem(F11)'",
     "     VISIBLE:  '< > Full Screen CheckItem(F11)', cursor=1",
     "SPEECH OUTPUT: 'tool bar'",
     "SPEECH OUTPUT: 'View menu'",
     "SPEECH OUTPUT: 'Full Screen'",
     "SPEECH OUTPUT: 'check item'",
     "SPEECH OUTPUT: 'not checked'",
     "SPEECH OUTPUT: 'F11'",
     "SPEECH OUTPUT: 'item 10 of 10'",
     "SPEECH OUTPUT: ''"]))

########################################################################
# Dismiss the menu by pressing Escape and wait for the location bar
# to regain focus.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
