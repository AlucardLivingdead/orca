#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'Foo'",
     "     VISIBLE:  'Foo', cursor=1",
     "SPEECH OUTPUT: 'Foo'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Tab"))
sequence.append(utils.AssertPresentationAction(
    "2. Shift Tab",
    ["KNOWN ISSUE: Extra 'F' in the braille.",
     "BRAILLE LINE:  'F Foo'",
     "     VISIBLE:  'F Foo', cursor=0",
     "SPEECH OUTPUT: 'document frame'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Tab",
    ["BRAILLE LINE:  'F Foo'",
     "     VISIBLE:  'F Foo', cursor=1",
     "BRAILLE LINE:  'F Foo'",
     "     VISIBLE:  'F Foo', cursor=1",
     "SPEECH OUTPUT: 'Foo link'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
