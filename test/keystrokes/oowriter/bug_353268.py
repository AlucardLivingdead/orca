#!/usr/bin/python

"""Test to verify bug #353268 is still fixed.
   Orca is double reading lines in openoffice with latest Ubuntu live CD.
"""

from macaroon.playback import *

sequence = MacroSequence()

######################################################################
# 1. Start oowriter.
#
sequence.append(WaitForWindowActivate("Untitled1 - OpenOffice.org Writer",None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 2. Enter Alt-f, right arrow and Return.  (File->New->Text Document).
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Text Document", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 3. Enter a couple lines of text:
#    "Line 1"
#    "Line 2"
#
sequence.append(TypeAction("Line 1"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(TypeAction("Line 2"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 4. Enter Control-Home to return to the top of the document.
#
# BRAILLE OUTPUT:  'soffice Application Untitled2 - OpenOffice.org Writer Frame Untitled2 - OpenOffice.org Writer RootPane ScrollPane Document view Line 1 $l'
# VISIBLE:  'Line 1 $l', cursor=1
# SPEECH OUTPUT: 'Line 1'
#
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 5. Arrow down over the first line of text.
#
# BRAILLE OUTPUT:  'soffice Application Untitled2 - OpenOffice.org Writer Frame Untitled2 - OpenOffice.org Writer RootPane ScrollPane Document view Line 2 $l'
# VISIBLE:  'Line 2 $l', cursor=1
# SPEECH OUTPUT: 'Line 2'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 6. Arrow down over the second line of text.
#
# BRAILLE OUTPUT:  'soffice Application Untitled2 - OpenOffice.org Writer Frame Untitled2 - OpenOffice.org Writer RootPane ScrollPane Document view Line 2 $l'
# VISIBLE:  ' Line 2 $l', cursor=1
# SPEECH OUTPUT: 'blank'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 7. Enter Alt-f, Alt-c to close the Writer application.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("<Alt>c"))
sequence.append(WaitForFocus("Save", acc_role=pyatspi.ROLE_PUSH_BUTTON))

######################################################################
# 8. Enter Tab and Return to discard the current changes.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Discard", acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(KeyComboAction("Return"))

sequence.start()
