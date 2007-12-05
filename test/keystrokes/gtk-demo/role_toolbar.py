#!/usr/bin/python

"""Test of toolbar output using the gtk-demo Application Main Window
   demo.
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
# Once gtk-demo is running, invoke the Application Main Window demo
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Application main window", 1000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return", 500))
#sequence.append(WaitForWindowActivate("Application Window",None))
sequence.append(WaitForFocus("Open", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Open button initial focus",
    ["BRAILLE LINE:  'gtk-demo Application Window Application main window $l'",
     "     VISIBLE:  'Application main window $l', cursor=24",
     "BRAILLE LINE:  'gtk-demo Application Window  $l'",
     "     VISIBLE:  'gtk-demo Application Window  $l', cursor=29",
     "BRAILLE LINE:  'gtk-demo Application Window  $l'",
     "     VISIBLE:  'gtk-demo Application Window  $l', cursor=29",
     "BRAILLE LINE:  'gtk-demo Application GTK+ Code Demos Frame TabList Widget (double click for demo) Page ScrollPane TreeTable Widget (double click for demo) ColumnHeader Application main window TREE LEVEL 1'",
     "     VISIBLE:  'Application main window TREE LEV', cursor=1",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame'",
     "     VISIBLE:  'Application Window Frame', cursor=1",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ToolBar Open Button'",
     "     VISIBLE:  'Open Button', cursor=1",
     "SPEECH OUTPUT: 'Widget (double click for demo) page'",
     "SPEECH OUTPUT: 'Widget (double click for demo) column header'",
     "SPEECH OUTPUT: 'Application main window'",
     "SPEECH OUTPUT: 'tree level 1'",
     "SPEECH OUTPUT: 'Application Window frame'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Open button'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Open button Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ToolBar Open Button'",
     "     VISIBLE:  'Open Button', cursor=1",
     "SPEECH OUTPUT: 'tool bar'",
     "SPEECH OUTPUT: 'Open'",
     "SPEECH OUTPUT: 'button'",
     "SPEECH OUTPUT: ''"]))

########################################################################
# Arrow Right to the triangular button next to the "Open" button.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Open triangle toggle button",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ToolBar & y ToggleButton'",
     "     VISIBLE:  '& y ToggleButton', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'toggle button not pressed'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Open triangle toggle button Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ToolBar & y ToggleButton'",
     "     VISIBLE:  '& y ToggleButton', cursor=1",
     "SPEECH OUTPUT: 'tool bar'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'toggle button'",
     "SPEECH OUTPUT: 'not pressed'"]))

########################################################################
# Arrow Right to the the "Quit" button.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Quit", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Quit button",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ToolBar Quit Button'",
     "     VISIBLE:  'Quit Button', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Quit button'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Quit button Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ToolBar Quit Button'",
     "     VISIBLE:  'Quit Button', cursor=1",
     "SPEECH OUTPUT: 'tool bar'",
     "SPEECH OUTPUT: 'Quit'",
     "SPEECH OUTPUT: 'button'",
     "SPEECH OUTPUT: ''"]))

########################################################################
# Close the Application Window demo window
#
sequence.append(KeyComboAction("<Alt>F4"))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
