#!/usr/bin/python

"""Test of line navigation output of Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'This is a test.'",
     "     VISIBLE:  'This is a test.', cursor=1",
     "SPEECH OUTPUT: 'This is a test.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'Solution'",
     "     VISIBLE:  'Solution', cursor=1",
     "SPEECH OUTPUT: 'Solution'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["KNOWN ISSUE: We seem to be combining list items",
     "BRAILLE LINE:  'Here is a step-by-step tutorial: •Do this thing'",
     "     VISIBLE:  'Here is a step-by-step tutorial:', cursor=1",
     "SPEECH OUTPUT: 'Here is a step-by-step tutorial: ",
     "'",
     "SPEECH OUTPUT: 'panel'",
     "SPEECH OUTPUT: '•Do this thing'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["KNOWN ISSUE: Are we getting stuck here?",
     "BRAILLE LINE:  'Here is a step-by-step tutorial: •Do this thing'",
     "     VISIBLE:  '•Do this thing', cursor=2",
     "SPEECH OUTPUT: 'Here is a step-by-step tutorial: ",
     "'",
     "SPEECH OUTPUT: 'panel'",
     "SPEECH OUTPUT: '•Do this thing'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  '•Do this other thing'",
     "     VISIBLE:  '•Do this other thing', cursor=2",
     "SPEECH OUTPUT: '•Do this other thing'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Up",
    ["BRAILLE LINE:  '•Do this thing'",
     "     VISIBLE:  '•Do this thing', cursor=2",
     "SPEECH OUTPUT: '•Do this thing'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Up",
    ["BRAILLE LINE:  'Here is a step-by-step tutorial: •Do this thing'",
     "     VISIBLE:  'Here is a step-by-step tutorial:', cursor=1",
     "SPEECH OUTPUT: 'Here is a step-by-step tutorial: ",
     "'",
     "SPEECH OUTPUT: 'panel'",
     "SPEECH OUTPUT: '•Do this thing'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Up",
    ["BRAILLE LINE:  'Solution'",
     "     VISIBLE:  'Solution', cursor=1",
     "SPEECH OUTPUT: 'Solution'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Up",
    ["BRAILLE LINE:  'This is a test.'",
     "     VISIBLE:  'This is a test.', cursor=1",
     "SPEECH OUTPUT: 'This is a test.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
