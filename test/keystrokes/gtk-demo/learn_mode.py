#!/usr/bin/python

"""Test of learn mode.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))

########################################################################
# Once gtk-demo is running, enter learn mode and press some keys.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("F1"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Enter learn mode",
    ["BRAILLE LINE:  'Learn mode.  Press escape to exit.'",
     "     VISIBLE:  'Learn mode.  Press escape to exi', cursor=0",
     "SPEECH OUTPUT: 'Entering learn mode.  Press any key to hear its function.  To exit learn mode, press the escape key.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(TypeAction("f"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Orca command: check text attributes",
    ["BRAILLE LINE:  'KP_Insert'",
     "     VISIBLE:  'KP_Insert', cursor=0",
     "BRAILLE LINE:  'Reads the attributes associated with the current text character.'",
     "     VISIBLE:  'Reads the attributes associated ', cursor=0",
     "SPEECH OUTPUT: 'KP_Insert'",
     "SPEECH OUTPUT: 'Reads the attributes associated with the current text character.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(TypeAction(" "))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Orca command: bring up preferences",
    ["BRAILLE LINE:  'KP_Insert'",
     "     VISIBLE:  'KP_Insert', cursor=0",
     "BRAILLE LINE:  'Displays the preferences configuration dialog.'",
     "     VISIBLE:  'Displays the preferences configu', cursor=0",
     "SPEECH OUTPUT: 'KP_Insert'",
     "SPEECH OUTPUT: 'Displays the preferences configuration dialog.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "Orca command: flat review current word",
    ["BRAILLE LINE:  'Speaks or spells the current flat review item or word.'",
     "     VISIBLE:  'Speaks or spells the current fla', cursor=0",
     "SPEECH OUTPUT: 'Speaks or spells the current flat review item or word.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("5"))
sequence.append(utils.AssertPresentationAction(
    "Regular typing command",
    ["BRAILLE LINE:  '5'",
     "     VISIBLE:  '5', cursor=0",
     "SPEECH OUTPUT: '5'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Escape"))
sequence.append(utils.AssertPresentationAction(
    "Exit learn mode",
    ["BRAILLE LINE:  'Exiting learn mode.'",
     "     VISIBLE:  'Exiting learn mode.', cursor=0",
     "SPEECH OUTPUT: 'Exiting learn mode.'"]))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
