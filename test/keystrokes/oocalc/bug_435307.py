#!/usr/bin/python

"""Test to verify bug #435307 is still fixed.
   OOo Calc output traceback for UnboundLocalError: local variable 
   'focusRegion' referenced before assignment.
"""

from macaroon.playback import *

sequence = MacroSequence()

######################################################################
# 1. Start oocalc. There is a bug_435307.params file that will
#    automatically load fruit.ods.
#
sequence.append(WaitForWindowActivate("fruit - OpenOffice.org Calc",None))

######################################################################
# 2. Type Control-Home to position the text caret in cell A1.
#
sequence.append(KeyComboAction("<Control>Home"))

######################################################################
# 3. Press the right arrow to move to cell B2.
#
sequence.append(KeyComboAction("Right"))

######################################################################
# 4. Type Alt-w to bring up the Windows menu.
#
sequence.append(KeyComboAction("<Alt>w"))
sequence.append(WaitForFocus("New Window", acc_role=pyatspi.ROLE_MENU_ITEM))

######################################################################
# 5. Type Alt-f to select the Freeze menu item.
#
# BRAILLE LINE:  'soffice Application fruit - OpenOffice.org Calc Frame fruit - OpenOffice.org Calc RootPane ScrollPane Document view4 Sheet Sheet1 Table Apples Cell B1 '
# VISIBLE:  'Apples Cell B1 ', cursor=1
# SPEECH OUTPUT: 'Apples B1'
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("Sheet Sheet1", acc_role=pyatspi.ROLE_TABLE))

######################################################################
# 6. Type Alt-w to bring up the Windows menu.
#
sequence.append(KeyComboAction("<Alt>w"))
sequence.append(WaitForFocus("New Window", acc_role=pyatspi.ROLE_MENU_ITEM))

######################################################################
# 7. Type Alt-f to select the Freeze menu item.
#
# BRAILLE LINE:  'soffice Application fruit - OpenOffice.org Calc Frame fruit - OpenOffice.org Calc RootPane ScrollPane Document view3 Sheet Sheet1 Table Apples Cell B1 '
# VISIBLE:  'Apples Cell B1 ', cursor=1
# SPEECH OUTPUT: 'Apples B1'
#
sequence.append(KeyComboAction("<Alt>f"))

######################################################################
# 8. Enter Alt-f, Alt-c to close the Calc spreadsheet window.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("<Alt>c"))
sequence.append(WaitAction("object:property-change:accessible-name",
                           None,
                           None,
                           pyatspi.ROLE_ROOT_PANE,
                           30000))

######################################################################
# 9. Enter Alt-f, right arrow, down arrow and Return,
#    (File->New->Spreadsheet), to get the application back
#    to the state it was in when the test started.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Text Document", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Spreadsheet", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Return"))
sequence.append(WaitAction("object:property-change:accessible-name",
                           None,
                           None,
                           pyatspi.ROLE_ROOT_PANE,
                           30000))

######################################################################
# 10. Wait for things to get back to normal.
#
sequence.append(PauseAction(3000))

sequence.start()
