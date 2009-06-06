# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of line navigation output of Firefox. 
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "bug-577239.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

sequence.append(WaitForFocus("",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Set Gecko's arrowToLineBeginning setting to False
#
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("<Control>space"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(WaitForWindowActivate("Orca Preferences for Firefox",None))
sequence.append(WaitForFocus("Speech", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(KeyComboAction("End"))
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Alt>p"))
sequence.append(WaitForFocus("Position cursor at start of line when navigating vertically", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("<Alt>o"))
sequence.append(TypeAction(" "))
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file",
    ["BRAILLE LINE:  'this is a page to test how well Orca works with list items.'",
     "     VISIBLE:  'this is a page to test how well ', cursor=1",
     "SPEECH OUTPUT: 'this is a page to test how well Orca works with list items.'"]))

########################################################################
# Down Arrow.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Line Down",
    ["BRAILLE LINE:  'this is an ordered list:'",
     "     VISIBLE:  'this is an ordered list:', cursor=1",
     "SPEECH OUTPUT: 'this is an ordered list:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  '1. This is a short list item.'",
     "     VISIBLE:  '1. This is a short list item.', cursor=1",
     "SPEECH OUTPUT: '1. This is a short list item.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  '2. This is a list item that spans multiple lines. If Orca can successfully read to the end of this list item, it will have read several lines of text within this'",
     "     VISIBLE:  '2. This is a list item that span', cursor=1",
     "SPEECH OUTPUT: '2. This is a list item that spans multiple lines. If Orca can successfully read to the end of this list item, it will have read several lines of text within this'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'single item. And, yes, I realize that this is not deathless prose. In fact, it is prose that should probably be put out of its misery.'",
     "     VISIBLE:  'single item. And, yes, I realize', cursor=1",
     "SPEECH OUTPUT: 'single item. And, yes, I realize that this is not deathless prose. In fact, it is prose that should probably be put out of its misery.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'This is an example of an unordered list:'",
     "     VISIBLE:  'This is an example of an unorder', cursor=(1|8)",
     "SPEECH OUTPUT: 'This is an example of an unordered list:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down",
    ["BRAILLE LINE:  '• This is a short list item.'",
     "     VISIBLE:  '• This is a short list item.', cursor=1",
     "SPEECH OUTPUT: 'bullet This is a short list item.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["BRAILLE LINE:  '• This is a list item that spans multiple lines. If Orca can successfully read to the end of this list item, it will have read several lines of text within this'",
     "     VISIBLE:  '• This is a list item that spans', cursor=1",
     "SPEECH OUTPUT: 'bullet This is a list item that spans multiple lines. If Orca can successfully read to the end of this list item, it will have read several lines of text within this'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Down",
    ["BRAILLE LINE:  'single item. And, yes, I realize that this is not deathless prose. In fact, it is prose that should probably be put out of its misery.'",
     "     VISIBLE:  'single item. And, yes, I realize', cursor=1",
     "SPEECH OUTPUT: 'single item. And, yes, I realize that this is not deathless prose. In fact, it is prose that should probably be put out of its misery.'"]))

########################################################################
# Up Arrow.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "1. Line Up",
    ["BRAILLE LINE:  '• This is a list item that spans multiple lines. If Orca can successfully read to the end of this list item, it will have read several lines of text within this'",
     "     VISIBLE:  '• This is a list item that spans', cursor=1",
     "SPEECH OUTPUT: 'bullet This is a list item that spans multiple lines. If Orca can successfully read to the end of this list item, it will have read several lines of text within this'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Up",
    ["BRAILLE LINE:  '• This is a short list item.'",
     "     VISIBLE:  '• This is a short list item.', cursor=1",
     "SPEECH OUTPUT: 'bullet This is a short list item.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Up",
    ["BRAILLE LINE:  'This is an example of an unordered list:'",
     "     VISIBLE:  'This is an example of an unorder', cursor=1",
     "SPEECH OUTPUT: 'This is an example of an unordered list:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Up",
    ["BRAILLE LINE:  'single item. And, yes, I realize that this is not deathless prose. In fact, it is prose that should probably be put out of its misery.'",
     "     VISIBLE:  'single item. And, yes, I realize', cursor=1",
     "SPEECH OUTPUT: 'single item. And, yes, I realize that this is not deathless prose. In fact, it is prose that should probably be put out of its misery.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Up",
    ["BRAILLE LINE:  '2. This is a list item that spans multiple lines. If Orca can successfully read to the end of this list item, it will have read several lines of text within this'",
     "     VISIBLE:  '2. This is a list item that span', cursor=1",
     "SPEECH OUTPUT: '2. This is a list item that spans multiple lines. If Orca can successfully read to the end of this list item, it will have read several lines of text within this'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Up",
    ["BRAILLE LINE:  '1. This is a short list item.'",
     "     VISIBLE:  '1. This is a short list item.', cursor=1",
     "SPEECH OUTPUT: '1. This is a short list item.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Up",
    ["BRAILLE LINE:  'this is an ordered list:'",
     "     VISIBLE:  'this is an ordered list:', cursor=1",
     "SPEECH OUTPUT: 'this is an ordered list:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Up",
    ["BRAILLE LINE:  'this is a page to test how well Orca works with list items.'",
     "     VISIBLE:  'this is a page to test how well ', cursor=1",
     "SPEECH OUTPUT: 'this is a page to test how well Orca works with list items.'"]))

########################################################################
# Set Gecko's arrowToLineBeginning setting back to True
#
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("<Control>space"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(WaitForWindowActivate("Orca Preferences for Firefox",None))
sequence.append(WaitForFocus("Speech", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(KeyComboAction("End"))
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Alt>p"))
sequence.append(WaitForFocus("Position cursor at start of line when navigating vertically", acc_role=pyatspi.ROLE_CHECK_BOX))
sequence.append(KeyComboAction("<Alt>o"))
sequence.append(TypeAction(" "))
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
