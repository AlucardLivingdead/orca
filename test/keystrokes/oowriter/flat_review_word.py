#!/usr/bin/python

"""Test flat review by word."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(TypeAction("Line 1"))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("Line 2"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "1. Review current word.",
    ["BRAILLE LINE:  'ruler Line 1 $l'",
     "     VISIBLE:  'ruler Line 1 $l', cursor=7",
     "SPEECH OUTPUT: 'Line'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "2. Spell current word.",
    ["BRAILLE LINE:  'ruler Line 1 $l'",
     "     VISIBLE:  'ruler Line 1 $l', cursor=7",
     "BRAILLE LINE:  'ruler Line 1 $l'",
     "     VISIBLE:  'ruler Line 1 $l', cursor=7",
     "SPEECH OUTPUT: 'Line'",
     "SPEECH OUTPUT: 'L'",
     "SPEECH OUTPUT: 'i'",
     "SPEECH OUTPUT: 'n'",
     "SPEECH OUTPUT: 'e'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(KeyComboAction("KP_5"))
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "3. Phonetic spell current word.",
    ["BRAILLE LINE:  'ruler Line 1 $l'",
     "     VISIBLE:  'ruler Line 1 $l', cursor=7",
     "BRAILLE LINE:  'ruler Line 1 $l'",
     "     VISIBLE:  'ruler Line 1 $l', cursor=7",
     "BRAILLE LINE:  'ruler Line 1 $l'",
     "     VISIBLE:  'ruler Line 1 $l', cursor=7",
     "SPEECH OUTPUT: 'Line'",
     "SPEECH OUTPUT: 'L'",
     "SPEECH OUTPUT: 'i'",
     "SPEECH OUTPUT: 'n'",
     "SPEECH OUTPUT: 'e'",
     "SPEECH OUTPUT: 'lima' voice=uppercase",
     "SPEECH OUTPUT: 'india'",
     "SPEECH OUTPUT: 'november'",
     "SPEECH OUTPUT: 'echo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "4. Review next word.",
    ["BRAILLE LINE:  'ruler Line 1 $l'",
     "     VISIBLE:  'ruler Line 1 $l', cursor=12",
     "SPEECH OUTPUT: '1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "5. Review next word.",
    ["BRAILLE LINE:  'Line 2 $l'",
     "     VISIBLE:  'Line 2 $l', cursor=1",
     "SPEECH OUTPUT: 'Line'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "6. Review next word.",
    ["BRAILLE LINE:  'Line 2 $l'",
     "     VISIBLE:  'Line 2 $l', cursor=6",
     "SPEECH OUTPUT: '2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_4"))
sequence.append(utils.AssertPresentationAction(
    "7. Review previous word.",
    ["BRAILLE LINE:  'Line 2 $l'",
     "     VISIBLE:  'Line 2 $l', cursor=1",
     "SPEECH OUTPUT: 'Line'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_4"))
sequence.append(utils.AssertPresentationAction(
    "8. Review previous word.",
    ["BRAILLE LINE:  'ruler Line 1 $l'",
     "     VISIBLE:  'ruler Line 1 $l', cursor=12",
     "SPEECH OUTPUT: '1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_4"))
sequence.append(utils.AssertPresentationAction(
    "9. Review previous word.",
    ["BRAILLE LINE:  'ruler Line 1 $l'",
     "     VISIBLE:  'ruler Line 1 $l', cursor=7",
     "SPEECH OUTPUT: 'Line'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
