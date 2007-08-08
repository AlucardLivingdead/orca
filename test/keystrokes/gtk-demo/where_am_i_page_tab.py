#!/usr/bin/python

"""Test "Where Am I" on page tabs using the gtk-demo Printing demo
"""

from macaroon.playback.keypress_mimic import *

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
# When the Printing demo window appears, navigate between the page tabs
# 
#sequence.append(WaitForWindowActivate("Print",None))
sequence.append(WaitForFocus("General", acc_role=pyatspi.ROLE_PAGE_TAB))

# Do "where am i"
sequence.append(KeyComboAction("KP_Enter", 500))

# Detailed "where am I"
sequence.append(KeyComboAction("KP_Enter", 3000))
sequence.append(KeyComboAction("KP_Enter"))

sequence.append(KeyComboAction("Right", 500))

sequence.append(WaitForFocus("Page Setup", acc_role=pyatspi.ROLE_PAGE_TAB))

# Do "where am i"
sequence.append(KeyComboAction("KP_Enter", 500))

# Detailed "where am I"
sequence.append(KeyComboAction("KP_Enter", 3000))
sequence.append(KeyComboAction("KP_Enter"))

sequence.append(KeyComboAction("Left", 500))

sequence.append(WaitForFocus("General", acc_role=pyatspi.ROLE_PAGE_TAB))

########################################################################
# Close the demo
#
sequence.append(KeyComboAction         ("<Alt>c", 500))

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
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_INVALID, timeout=3000))

sequence.start()
