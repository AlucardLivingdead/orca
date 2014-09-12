#!/usr/bin/python

"""Test of label guess functionality."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "1. Next form field",
    ["BRAILLE LINE:  'Enter your Name:  $l text field using default type=text'",
     "     VISIBLE:  'Enter your Name:  $l text field ', cursor=0",
     "SPEECH OUTPUT: 'Enter your Name:'",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "2. Next form field",
    ["BRAILLE LINE:  '1. Enter your Address:  $l text field using SIZE and'",
     "     VISIBLE:  '1. Enter your Address:  $l text ', cursor=0",
     "SPEECH OUTPUT: '1. Enter your Address:'",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "3. Next form field",
    ["BRAILLE LINE:  '2. Enter your City:  $l 3. Enter your State:  $l 4. Enter your Country: US $l image text field using'",
     "     VISIBLE:  '2. Enter your City:  $l 3. Enter', cursor=0",
     "SPEECH OUTPUT: '2. Enter your City:'",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "4. Next form field",
    ["BRAILLE LINE:  '2. Enter your City:  $l 3. Enter your State:  $l 4. Enter your Country: US $l image text field using'",
     "     VISIBLE:  '2. Enter your City:  $l 3. Enter', cursor=0",
     "SPEECH OUTPUT: '3. Enter your State:'",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "5. Next form field",
    ["BRAILLE LINE:  '2. Enter your City:  $l 3. Enter your State:  $l 4. Enter your Country: US $l image text field using'",
     "     VISIBLE:  'US $l image text field using', cursor=1",
     "SPEECH OUTPUT: '4. Enter your Country:'",
     "SPEECH OUTPUT: 'entry'",
     "SPEECH OUTPUT: 'US'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "6. Next form field",
    ["BRAILLE LINE:  '5. Enter your Zip:  $l'",
     "     VISIBLE:  '5. Enter your Zip:  $l', cursor=0",
     "SPEECH OUTPUT: '5. Enter your Zip:'",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "7. Next form field",
    ["BRAILLE LINE:  'character:  $l'",
     "     VISIBLE:  'character:  $l', cursor=0",
     "SPEECH OUTPUT: 'character:'",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "8. Next form field",
    ["KNOWN ISSUE: This is broken",
     "BRAILLE LINE:  '< > check box bird'",
     "     VISIBLE:  '< > check box bird', cursor=0",
     "SPEECH OUTPUT: 'check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "9. Next form field",
    ["BRAILLE LINE:  '< > check box fish'",
     "     VISIBLE:  '< > check box fish', cursor=0",
     "SPEECH OUTPUT: 'fish'",
     "SPEECH OUTPUT: 'check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "10. Next form field",
    ["BRAILLE LINE:  '< > check box wild animal'",
     "     VISIBLE:  '< > check box wild animal', cursor=0",
     "SPEECH OUTPUT: 'wild animal'",
     "SPEECH OUTPUT: 'check box not checked'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "11. Next form field",
    ["KNOWN ISSUE: This is broken",
     "BRAILLE LINE:  '&=y radio button cabernet sauvignon'",
     "     VISIBLE:  '&=y radio button cabernet sauvig', cursor=0",
     "SPEECH OUTPUT: 'selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "12. Next form field",
    ["BRAILLE LINE:  '& y radio button merlot'",
     "     VISIBLE:  '& y radio button merlot', cursor=0",
     "SPEECH OUTPUT: 'merlot'",
     "SPEECH OUTPUT: 'not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "13. Next form field",
    ["BRAILLE LINE:  '& y radio button nebbiolo'",
     "     VISIBLE:  '& y radio button nebbiolo', cursor=0",
     "SPEECH OUTPUT: 'nebbiolo'",
     "SPEECH OUTPUT: 'not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "14. Next form field",
    ["BRAILLE LINE:  '& y radio button pinot noir'",
     "     VISIBLE:  '& y radio button pinot noir', cursor=0",
     "SPEECH OUTPUT: 'pinot noir'",
     "SPEECH OUTPUT: 'not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "15. Next form field",
    ["BRAILLE LINE:  '& y radio button don't drink wine'",
     "     VISIBLE:  '& y radio button don't drink win', cursor=0",
     "SPEECH OUTPUT: 'don't drink wine'",
     "SPEECH OUTPUT: 'not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "16. Next form field",
    ["BRAILLE LINE:  'Wrapping to top.'",
     "     VISIBLE:  'Wrapping to top.', cursor=0",
     "BRAILLE LINE:  'Enter your Name:  $l text field using default type=text'",
     "     VISIBLE:  'Enter your Name:\xa0 $l text field ', cursor=0",
     "SPEECH OUTPUT: 'Wrapping to top.' voice=system",
     "SPEECH OUTPUT: 'Enter your Name:'",
     "SPEECH OUTPUT: 'entry'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
