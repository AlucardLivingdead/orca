#!/usr/bin/python

"""Test of combobox output using the gtk-demo Printing demo, which
gets us a labelled combo box.
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
# Once gtk-demo is running, invoke the Printing demo 
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Printing", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the Printing demo window appears, navigate to the "Only print"
# combo box on the "Page Setup" tab.
# 
#sequence.append(WaitForWindowActivate("Print",None))
sequence.append(WaitForFocus("General", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(KeyComboAction("Right"))

sequence.append(WaitForFocus("Page Setup", acc_role=pyatspi.ROLE_PAGE_TAB))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction         ("Tab"))
sequence.append(WaitForFocus("All sheets", acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(utils.AssertPresentationAction(
    "All sheets combo box item",
    ["BRAILLE LINE:  'gtk-demo Application Print Dialog TabList Page Setup Page Layout Filler Only print: All sheets Combo'",
     "     VISIBLE:  'All sheets Combo', cursor=1",
     "SPEECH OUTPUT: 'Layout Only print: All sheets combo box'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "All sheets combo box item Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Print Dialog TabList Page Setup Page Layout Filler Only print: All sheets Combo'",
     "     VISIBLE:  'All sheets Combo', cursor=1",
     "SPEECH OUTPUT: 'Only print: combo box All sheets item 1 of 3.",
     "SPEECH OUTPUT: 'Alt o'"]))

########################################################################
# Down arrow to select the "Even sheets" item in the combo box.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:selection-changed",
                           None,
                           None,
                           pyatspi.ROLE_COMBO_BOX,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Event sheets combo box item",
    ["BRAILLE LINE:  'gtk-demo Application Print Dialog TabList Page Setup Page Layout Filler Only print: Even sheets Combo'",
     "     VISIBLE:  'Even sheets Combo', cursor=1",
     "SPEECH OUTPUT: 'Even sheets'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Even sheets combo box item Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Print Dialog TabList Page Setup Page Layout Filler Only print: Even sheets Combo'",
     "     VISIBLE:  'Even sheets Combo', cursor=1",
     "SPEECH OUTPUT: 'Only print: combo box Even sheets item 2 of 3.",
     "SPEECH OUTPUT: 'Alt o'"]))

########################################################################
# Put things back the way they were and close the demo.
#
sequence.append(KeyComboAction("Up"))
sequence.append(KeyComboAction("<Alt>c", 500))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction("Home"))

sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TREE_TABLE,
                           5000))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
