#!/usr/bin/python

"""Test of line navigation output of Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'Start'",
     "     VISIBLE:  'Start', cursor=1",
     "SPEECH OUTPUT: 'Start'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'up vote'",
     "     VISIBLE:  'up vote', cursor=1",
     "SPEECH OUTPUT: 'up vote'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["KNOWN ISSUE: It currently takes us several down arrows to move past this link",
     "BRAILLE LINE:  'up vote'",
     "     VISIBLE:  'up vote', cursor=1",
     "SPEECH OUTPUT: 'up vote'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["KNOWN ISSUE: It currently takes us several down arrows to move past this link",
     "BRAILLE LINE:  'up vote'",
     "     VISIBLE:  'up vote', cursor=1",
     "SPEECH OUTPUT: 'up vote'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  '74'",
     "     VISIBLE:  '74', cursor=1",
     "SPEECH OUTPUT: '74'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down",
    ["BRAILLE LINE:  'down vote'",
     "     VISIBLE:  'down vote', cursor=1",
     "SPEECH OUTPUT: 'down vote'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["KNOWN ISSUE: It currently takes us several down arrows to move past this link",
     "BRAILLE LINE:  'down vote'",
     "     VISIBLE:  'down vote', cursor=1",
     "SPEECH OUTPUT: 'down vote'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Down",
    ["KNOWN ISSUE: It currently takes us several down arrows to move past this link",
     "BRAILLE LINE:  'down vote'",
     "     VISIBLE:  'down vote', cursor=1",
     "SPEECH OUTPUT: 'down vote'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Down",
    ["BRAILLE LINE:  'accepted'",
     "     VISIBLE:  'accepted', cursor=1",
     "SPEECH OUTPUT: 'accepted'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Down",
    ["KNOWN ISSUE: It currently takes us several down arrows to move past this object",
     "BRAILLE LINE:  'accepted'",
     "     VISIBLE:  'accepted', cursor=7",
     "SPEECH OUTPUT: 'accepted'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Up",
    ["BRAILLE LINE:  'accepted'",
     "     VISIBLE:  'accepted', cursor=1",
     "SPEECH OUTPUT: 'accepted'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Up",
    ["BRAILLE LINE:  'down vote'",
     "     VISIBLE:  'down vote', cursor=1",
     "SPEECH OUTPUT: 'down vote'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Up",
    ["BRAILLE LINE:  '74'",
     "     VISIBLE:  '74', cursor=1",
     "SPEECH OUTPUT: '74'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "14. Line Up",
    ["BRAILLE LINE:  'up vote'",
     "     VISIBLE:  'up vote', cursor=1",
     "SPEECH OUTPUT: 'up vote'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "15. Line Up",
    ["BRAILLE LINE:  'Start'",
     "     VISIBLE:  'Start', cursor=1",
     "SPEECH OUTPUT: 'Start'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
