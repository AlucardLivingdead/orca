#!/usr/bin/python

"""Test of tear off menu item output using the gtk-demo menus demo.
"""

from macaroon.playback.keypress_mimic import *

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))

########################################################################
# Once gtk-demo is running, invoke the menus demo
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Menus", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the menus demo window appears, go to the tear off menu item
#
#sequence.append(WaitForWindowActivate("menus",None))
sequence.append(WaitForFocus("Flip", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("F10"))

sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_MENU))
sequence.append(KeyComboAction("Down"))

sequence.append(WaitForFocus("item  2 - 1",
                             acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(KeyComboAction("Up"))

sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEAROFF_MENU_ITEM))
sequence.append(KeyComboAction("F10"))

sequence.append(WaitForFocus("Flip", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Down"))

sequence.append(WaitForFocus("Close", acc_role=pyatspi.ROLE_PUSH_BUTTON))

########################################################################
# Close the menus demo window
#
sequence.append(KeyComboAction("Return", 500))

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
