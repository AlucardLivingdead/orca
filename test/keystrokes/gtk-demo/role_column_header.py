#!/usr/bin/python

"""Test of column header output using the gtk-demo List Store demo
   under the Tree View area.
"""

from macaroon.playback.keypress_mimic import *

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(WaitForFocus        ([0, 0, 0, 0, 0, 0], pyatspi.ROLE_TREE_TABLE))

########################################################################
# Once gtk-demo is running.  Down arrow to the List Store demo and
# invoke it.
#
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("<Shift>Right"))
sequence.append(WaitForEvent("object:state-changed:expanded",
                             [0, 0, 0, 0, 0, 0, 23],
                             pyatspi.ROLE_TABLE_CELL))
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Down"))
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Return"))

########################################################################
# When the GtkListStore demo window appears, navigate the table headers
# 
#sequence.append(WaitForWindowActivate("GtkListStore demo",None))
# "Bug number"
sequence.append(WaitForFocus        ([1, 0, 1, 0, 1], pyatspi.ROLE_TABLE_COLUMN_HEADER))
sequence.append(KeyComboAction         ("Right"))

# "Severity"
sequence.append(WaitForFocus        ([1, 0, 1, 0, 2], pyatspi.ROLE_TABLE_COLUMN_HEADER))
sequence.append(KeyComboAction         ("Right"))

# "Description"
sequence.append(WaitForFocus        ([1, 0, 1, 0, 3], pyatspi.ROLE_TABLE_COLUMN_HEADER))

########################################################################
# Now go down into the table to see if we read the column headers as we
# move from column to column.
#
sequence.append(KeyComboAction         ("Down"))
# ""
sequence.append(WaitForFocus        ([1, 0, 1, 0], pyatspi.ROLE_TABLE))
sequence.append(KeyComboAction         ("Left"))

sequence.append(WaitForEvent("object:active-descendant-changed",
                             [1, 0, 1, 0],
                             pyatspi.ROLE_TABLE))
sequence.append(KeyComboAction         ("Left"))

sequence.append(WaitForEvent("object:active-descendant-changed",
                             [1, 0, 1, 0],
                             pyatspi.ROLE_TABLE))
sequence.append(KeyComboAction         ("Left"))

########################################################################
# Close the GtkListStore demo
#
sequence.append(WaitForEvent("object:active-descendant-changed",
                             [1, 0, 1, 0],
                             pyatspi.ROLE_TABLE))
sequence.append(KeyComboAction         ("<Alt>F4"))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(WaitForFocus        ([0, 0, 0, 0, 0, 0], pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Up"))

sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("Up"))

sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction         ("<Shift>Left"))

sequence.append(WaitForEvent("object:state-changed:expanded",
                             [0, 0, 0, 0, 0, 0, 23],
                             pyatspi.ROLE_TABLE_CELL))
sequence.append(KeyComboAction         ("Home"))

sequence.append(WaitForEvent("object:active-descendant-changed",
                             [0, 0, 0, 0, 0, 0],
                             pyatspi.ROLE_TREE_TABLE))

sequence.start()
