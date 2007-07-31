#!/usr/bin/python

"""Test of icon output using the gtk-demo Icon View Basics demo under
   the Icon View area.
"""

from macaroon.playback.keypress_mimic import *

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(WaitForFocus        ([0, 0, 0, 0, 0, 0], pyatspi.ROLE_TREE_TABLE))

########################################################################
# Once gtk-demo is running, invoke the Icon View Basics demo
#
sequence.append(TypeAction           ("Icon View"))
sequence.append(WaitForFocus        ([1, 0, 0, 0], pyatspi.ROLE_TEXT))
sequence.append(KeyComboAction         ("Return"))
sequence.append(KeyComboAction         ("<Shift>Right"))

sequence.append(TypeAction           ("Icon View Basics"))
sequence.append(WaitForFocus        ([1, 0, 0, 0], pyatspi.ROLE_TEXT))
sequence.append(KeyComboAction         ("Return"))

########################################################################
# Once the GtkIconView demo is up, arrow around a few icons
#
#sequence.append(WaitForWindowActivate("GtkIconView demo",None))
# ""
sequence.append(WaitForFocus        ([1, 0, 1, 0], pyatspi.ROLE_LAYERED_PANE))
sequence.append(KeyComboAction         ("Down"))

# "bin"
sequence.append(WaitForFocus        ([1, 0, 1, 0, 0], pyatspi.ROLE_ICON))
sequence.append(KeyComboAction         ("Right"))

# "boot"
sequence.append(WaitForFocus        ([1, 0, 1, 0, 1], pyatspi.ROLE_ICON))
sequence.append(KeyComboAction         ("Right"))

########################################################################
# Close the GtkIconView demo window
#
# "cdrom"
sequence.append(WaitForFocus        ([1, 0, 1, 0, 2], pyatspi.ROLE_ICON))
sequence.append(KeyComboAction         ("<Alt>F4"))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(WaitForFocus        ([0, 0, 0, 0, 0, 0], pyatspi.ROLE_TREE_TABLE))

sequence.append(TypeAction           ("Icon View"))
sequence.append(WaitForFocus        ([1, 0, 0, 0], pyatspi.ROLE_TEXT))
sequence.append(KeyComboAction         ("Return"))
sequence.append(KeyComboAction         ("<Shift>Left"))
sequence.append(KeyComboAction         ("Home"))

sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))

sequence.start()
