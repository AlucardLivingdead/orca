# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of line navigation output of Firefox on a page with multi-
line table cells and sections.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the local "simple form" test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "multi-line.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

sequence.append(WaitForFocus("Mutli-Line Test",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file",
    ["BRAILLE LINE:  'Table test'",
     "     VISIBLE:  'Table test', cursor=1",
     "SPEECH OUTPUT: 'Table test'"]))

########################################################################
# Down Arrow.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'foo bar'",
     "     VISIBLE:  'foo bar', cursor=1",
     "SPEECH OUTPUT: 'foo bar'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'foo'",
     "     VISIBLE:  'foo', cursor=1",
     "SPEECH OUTPUT: 'foo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'foo'",
     "     VISIBLE:  'foo', cursor=1",
     "SPEECH OUTPUT: 'foo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'bar'",
     "     VISIBLE:  'bar', cursor=1",
     "SPEECH OUTPUT: 'bar'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'bar'",
     "     VISIBLE:  'bar', cursor=1",
     "SPEECH OUTPUT: 'bar'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Hello h3'",
     "     VISIBLE:  'Hello h3', cursor=1",
     "SPEECH OUTPUT: 'Hello heading  '",
     "SPEECH OUTPUT: 'level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '• This is a test Link  that is not very interesting.'",
     "     VISIBLE:  '• This is a test Link  that is', cursor=1",
     "SPEECH OUTPUT: '• This is a test link  that is not very interesting.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '• But it looks like Link  a real-world example.'",
     "     VISIBLE:  '• But it looks like Link  a re', cursor=1",
     "SPEECH OUTPUT: '• But it looks like link  a real-world example.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '• And that's Link  why this silly test is here.'",
     "     VISIBLE:  '• And that's Link  why this si', cursor=1",
     "SPEECH OUTPUT: '• And that's link  why this silly test is here.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'So it's far more interesting Link  than it looks.'",
     "     VISIBLE:  'So it's far more interesting Lin', cursor=1",
     "SPEECH OUTPUT: 'So it's far more interesting link  than it looks.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'World h3'",
     "     VISIBLE:  'World h3', cursor=1",
     "SPEECH OUTPUT: 'World heading  '",
     "SPEECH OUTPUT: 'level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '• The thing is Link  we can't copy content.'",
     "     VISIBLE:  '• The thing is Link  we can't ', cursor=1",
     "SPEECH OUTPUT: '• The thing is link  we can't copy content.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '• So we must Link  create silly tests.'",
     "     VISIBLE:  '• So we must Link  create sill', cursor=1",
     "SPEECH OUTPUT: '• So we must link  create silly tests.'",]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '• Oh Link  well.'",
     "     VISIBLE:  '• Oh Link  well.', cursor=1",
     "SPEECH OUTPUT: '• Oh link  well.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'At least it's over Link .'",
     "     VISIBLE:  'At least it's over Link .', cursor=1",
     "SPEECH OUTPUT: 'At least it's over link .'"]))

########################################################################
# Up Arrow.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '• Oh Link  well.'",
     "     VISIBLE:  '• Oh Link  well.', cursor=1",
     "SPEECH OUTPUT: '• Oh link  well.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '• So we must Link  create silly tests.'",
     "     VISIBLE:  '• So we must Link  create sill', cursor=1",
     "SPEECH OUTPUT: '• So we must link  create silly tests.'",]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '• The thing is Link  we can't copy content.'",
     "     VISIBLE:  '• The thing is Link  we can't ', cursor=1",
     "SPEECH OUTPUT: '• The thing is link  we can't copy content.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'World h3'",
     "     VISIBLE:  'World h3', cursor=1",
     "SPEECH OUTPUT: 'World heading  '",
     "SPEECH OUTPUT: 'level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'So it's far more interesting Link  than it looks.'",
     "     VISIBLE:  'So it's far more interesting Lin', cursor=1",
     "SPEECH OUTPUT: 'So it's far more interesting link  than it looks.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '• And that's Link  why this silly test is here.'",
     "     VISIBLE:  '• And that's Link  why this si', cursor=1",
     "SPEECH OUTPUT: '• And that's link  why this silly test is here.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '• But it looks like Link  a real-world example.'",
     "     VISIBLE:  '• But it looks like Link  a re', cursor=1",
     "SPEECH OUTPUT: '• But it looks like link  a real-world example.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '• This is a test Link  that is not very interesting.'",
     "     VISIBLE:  '• This is a test Link  that is', cursor=1",
     "SPEECH OUTPUT: '• This is a test link  that is not very interesting.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Hello h3'",
     "     VISIBLE:  'Hello h3', cursor=1",
     "SPEECH OUTPUT: 'Hello heading  '",
     "SPEECH OUTPUT: 'level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'bar'",
     "     VISIBLE:  'bar', cursor=1",
     "SPEECH OUTPUT: 'bar'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'bar'",
     "     VISIBLE:  'bar', cursor=1",
     "SPEECH OUTPUT: 'bar'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'foo'",
     "     VISIBLE:  'foo', cursor=1",
     "SPEECH OUTPUT: 'foo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'foo'",
     "     VISIBLE:  'foo', cursor=1",
     "SPEECH OUTPUT: 'foo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'foo bar'",
     "     VISIBLE:  'foo bar', cursor=1",
     "SPEECH OUTPUT: 'foo bar'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Table test'",
     "     VISIBLE:  'Table test', cursor=1",
     "SPEECH OUTPUT: 'Table test'"]))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
