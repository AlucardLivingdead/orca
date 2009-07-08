#!/usr/bin/python

"""Test of column header output using the gtk-demo List Store demo
   under the Tree View area.
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
# Once gtk-demo is running, invoke the List Store demo
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Tree View", 1000))
sequence.append(KeyComboAction("Return", 500))
sequence.append(KeyComboAction("<Shift>Right"))
sequence.append(WaitAction("object:state-changed:expanded",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))

sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("List Store", 1000))

########################################################################
# When the GtkListStore demo window appears, navigate the table headers.
#
sequence.append(KeyComboAction("Return", 1000))
#sequence.append(WaitForWindowActivate("GtkListStore demo",None))
sequence.append(WaitForFocus("Bug number",
                             acc_role=pyatspi.ROLE_TABLE_COLUMN_HEADER))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Severity",
                             acc_role=pyatspi.ROLE_TABLE_COLUMN_HEADER))
sequence.append(utils.AssertPresentationAction(
    "Severity column header",
    ["BRAILLE LINE:  'gtk-demo Application GtkListStore demo Frame ScrollPane Table Severity ColumnHeader'",
     "     VISIBLE:  'Severity ColumnHeader', cursor=1",
     "SPEECH OUTPUT: 'Severity column header'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right", 500))
sequence.append(WaitForFocus("Description",
                             acc_role=pyatspi.ROLE_TABLE_COLUMN_HEADER))
sequence.append(utils.AssertPresentationAction(
    "Description column header",
    ["BRAILLE LINE:  'gtk-demo Application GtkListStore demo Frame ScrollPane Table Description ColumnHeader'",
     "     VISIBLE:  'Description ColumnHeader', cursor=1",
     "SPEECH OUTPUT: 'Description column header'"]))

########################################################################
# Now go down into the table to see if we read the column headers as we
# move from column to column.  You should end up in the "scrollable
# notebooks and hidden tabs" cell.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down", 500))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TABLE))
sequence.append(utils.AssertPresentationAction(
    "Enter table for first time",
    ["BRAILLE LINE:  'gtk-demo Application GtkListStore demo Frame ScrollPane Table'",
     "     VISIBLE:  'Table', cursor=1",
     "BRAILLE LINE:  'gtk-demo Application GtkListStore demo Frame ScrollPane Table Description ColumnHeader < > Fixed? 60482 Normal scrollable notebooks and hidden tabs'",
     "     VISIBLE:  'scrollable notebooks and hidden ', cursor=1",
     "SPEECH OUTPUT: 'table'",
     "SPEECH OUTPUT: 'Description column header Fixed? check box not checked 60482 Normal scrollable notebooks and hidden tabs'"]))

########################################################################
# Now move to the cell to the left containing the word "Normal".
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left", 5000))
sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Normal cell",
    ["BRAILLE LINE:  'gtk-demo Application GtkListStore demo Frame ScrollPane Table Severity ColumnHeader < > Fixed? 60482 Normal scrollable notebooks and hidden tabs'",
     "     VISIBLE:  'Normal scrollable notebooks and ', cursor=1",
     "SPEECH OUTPUT: 'Severity column header Normal'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Normal cell basic Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application GtkListStore demo Frame ScrollPane Table Severity ColumnHeader < > Fixed? 60482 Normal scrollable notebooks and hidden tabs'",
     "     VISIBLE:  'Normal scrollable notebooks and ', cursor=1",
     "SPEECH OUTPUT: 'table Severity cell Normal column 3 of 4 row 1 of 14'"]))

########################################################################
# Do a detailed "Where Am I" via KP_Enter.
#
# JD to WDW: This test was changed. Multiple utterances are now just
# one. Do we care? 
#
# WDW to JD: No - it's OK.  If pauses are needed (which we can learn via
# end user testing), we can add '+ ["."] +' things in the formatting
# strings as needed.
#
# In addition, something I would consider a bug fix: Before we
# didn't speak the name ("Fixed?") of the checkbox at the start of the row;
# now we do.
#
# WDW to JD: I agree.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Normal cell detailed Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application GtkListStore demo Frame ScrollPane Table Severity ColumnHeader < > Fixed? 60482 Normal scrollable notebooks and hidden tabs'",
     "     VISIBLE:  'Normal scrollable notebooks and ', cursor=1",
     "BRAILLE LINE:  'gtk-demo Application GtkListStore demo Frame ScrollPane Table Severity ColumnHeader < > Fixed? 60482 Normal scrollable notebooks and hidden tabs'",
     "     VISIBLE:  'Normal scrollable notebooks and ', cursor=1",
     "SPEECH OUTPUT: 'table Severity cell Normal column 3 of 4 row 1 of 14'",
     "SPEECH OUTPUT: 'table Severity cell Normal column 3 of 4 row 1 of 14 Fixed? check box not checked 60482 Normal scrollable notebooks and hidden tabs'"]))

########################################################################
# Now move to the cell to the left containing the number "60482".
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "60482 cell",
    ["BRAILLE LINE:  'gtk-demo Application GtkListStore demo Frame ScrollPane Table Bug number ColumnHeader < > Fixed? 60482 Normal scrollable notebooks and hidden tabs'",
     "     VISIBLE:  '60482 Normal scrollable notebook', cursor=1",
     "SPEECH OUTPUT: 'Bug number column header 60482'"]))

########################################################################
# Now move to the cell to the left containing the checkbox.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left", 500))
sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Checkbox cell",
    ["BRAILLE LINE:  'gtk-demo Application GtkListStore demo Frame ScrollPane Table Fixed? ColumnHeader < > Fixed? 60482 Normal scrollable notebooks and hidden tabs'",
     "     VISIBLE:  '< > Fixed? 60482 Normal scrollab', cursor=1",
     "SPEECH OUTPUT: 'Fixed? column header check box not checked'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Checkbox cell basic Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application GtkListStore demo Frame ScrollPane Table Fixed? ColumnHeader < > Fixed? 60482 Normal scrollable notebooks and hidden tabs'",
     "     VISIBLE:  '< > Fixed? 60482 Normal scrollab', cursor=1",
     "SPEECH OUTPUT: 'table Fixed? cell check box not checked column 1 of 4 row 1 of 14'"]))

########################################################################
# Do a detailed "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Checkbox cell detailed Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application GtkListStore demo Frame ScrollPane Table Fixed? ColumnHeader < > Fixed? 60482 Normal scrollable notebooks and hidden tabs'",
     "     VISIBLE:  '< > Fixed? 60482 Normal scrollab', cursor=1",
     "BRAILLE LINE:  'gtk-demo Application GtkListStore demo Frame ScrollPane Table Fixed? ColumnHeader < > Fixed? 60482 Normal scrollable notebooks and hidden tabs'",
     "     VISIBLE:  '< > Fixed? 60482 Normal scrollab', cursor=1",
     "SPEECH OUTPUT: 'table Fixed? cell check box not checked column 1 of 4 row 1 of 14'",
     "SPEECH OUTPUT: 'table Fixed? cell check box not checked column 1 of 4 row 1 of 14 Fixed? check box not checked 60482 Normal scrollable notebooks and hidden tabs'"]))
 
########################################################################
# Close the GtkListStore demo
#
sequence.append(KeyComboAction("<Alt>F4", 1000))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction("<Control>f"))

sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Tree View", 1000))
sequence.append(KeyComboAction("Return", 500))
sequence.append(KeyComboAction("<Shift>Left"))
sequence.append(WaitAction("object:state-changed:expanded",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))

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
