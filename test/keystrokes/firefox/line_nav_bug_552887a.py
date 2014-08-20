#!/usr/bin/python

"""Test of the fix for one of the two issues in bug 552887."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'Line 1'",
     "     VISIBLE:  'Line 1', cursor=1",
     "SPEECH OUTPUT: 'Line 1",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'Line 1 Line 2 h2'",
     "     VISIBLE:  'Line 1 Line 2 h2', cursor=8",
     "SPEECH OUTPUT: 'Line 1",
     "'",
     "SPEECH OUTPUT: 'Line 2'",
     "SPEECH OUTPUT: 'heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'Line 3'",
     "     VISIBLE:  'Line 3', cursor=1",
     "SPEECH OUTPUT: 'Line 3",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'The Orca logo image'",
     "     VISIBLE:  'The Orca logo image', cursor=1",
     "SPEECH OUTPUT: 'The Orca logo'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'Hey, look, it's our logo!'",
     "SPEECH OUTPUT: '",
     "'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down",
    ["BRAILLE LINE:  'Can an Orca really'",
     "     VISIBLE:  'Can an Orca really', cursor=1",
     "SPEECH OUTPUT: 'Can an Orca really '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["BRAILLE LINE:  'hold a white cane?'",
     "     VISIBLE:  'hold a white cane?', cursor=1",
     "SPEECH OUTPUT: 'hold a white cane? '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Down",
    ["BRAILLE LINE:  '(And why aren't we'",
     "     VISIBLE:  '(And why aren't we', cursor=1",
     "SPEECH OUTPUT: '(And why aren't we '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Down",
    ["BRAILLE LINE:  'speaking this text?'",
     "     VISIBLE:  'speaking this text?', cursor=1",
     "SPEECH OUTPUT: 'speaking this text?'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Down",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: 'The Orca logo'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'Hey, look, it's our logo!'",
     "SPEECH OUTPUT: '",
     "'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: '",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Down",
    ["BRAILLE LINE:  'This text comes before the box section'",
     "     VISIBLE:  'This text comes before the box s', cursor=1",
     "SPEECH OUTPUT: 'This text comes before the box section",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Down",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Down",
    ["BRAILLE LINE:  'image'",
     "     VISIBLE:  'image', cursor=1",
     "SPEECH OUTPUT: 'image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "14. Line Down",
    ["BRAILLE LINE:  'Here's a box'",
     "     VISIBLE:  'Here's a box', cursor=1",
     "SPEECH OUTPUT: 'Here's a box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "15. Line Down",
    ["BRAILLE LINE:  'Here's some box text.'",
     "     VISIBLE:  'Here's some box text.', cursor=1",
     "SPEECH OUTPUT: 'Here's some box text.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "16. Line Down",
    ["BRAILLE LINE:  'The end of the box'",
     "     VISIBLE:  'The end of the box', cursor=1",
     "SPEECH OUTPUT: 'The end of the box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "17. Line Down",
    ["BRAILLE LINE:  'image This text comes after'",
     "     VISIBLE:  'image This text comes after', cursor=7",\
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'This text comes after '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "18. Line Down",
    ["BRAILLE LINE:  'the box section.'",
     "     VISIBLE:  'the box section.', cursor=1",
     "SPEECH OUTPUT: 'the box section.",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "19. Line Up",
    ["BRAILLE LINE:  'image'",
     "     VISIBLE:  'image', cursor=1",
     "SPEECH OUTPUT: 'image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "20. Line Up",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "21. Line Up",
    ["BRAILLE LINE:  'This text comes before the box section'",
     "     VISIBLE:  'This text comes before the box s', cursor=1",
     "SPEECH OUTPUT: 'This text comes before the box section",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "22. Line Up",
    ["BRAILLE LINE:  'The Orca logo image'",
     "     VISIBLE:  'The Orca logo image', cursor=1",
     "SPEECH OUTPUT: 'The Orca logo'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'Hey, look, it's our logo!'",
     "SPEECH OUTPUT: '",
     "'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "23. Line Up",
    ["BRAILLE LINE:  'Line 3'",
     "     VISIBLE:  'Line 3', cursor=1",
     "SPEECH OUTPUT: 'Line 3",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "24. Line Up",
    ["KNOWN ISSUE: On the way up, we skip the 'Line 2' text.",
     "BRAILLE LINE:  'Line 1'",
     "     VISIBLE:  'Line 1', cursor=1",
     "SPEECH OUTPUT: 'Line 1",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "25. Line Up",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
