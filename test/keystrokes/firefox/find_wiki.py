#!/usr/bin/python

"""Test of find result presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>Home"))
sequence.append(KeyComboAction("<Control>F"))
sequence.append(TypeAction("orca"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "1. Return to next result",
    ["KNOWN ISSUE: We're double-presenting this",
     "BRAILLE LINE:  'Welcome to Orca! h1'",
     "     VISIBLE:  'Welcome to Orca! h1', cursor=12",
     "BRAILLE LINE:  'Welcome to Orca! h1'",
     "     VISIBLE:  'Welcome to Orca! h1', cursor=16",
     "SPEECH OUTPUT: 'Welcome to Orca! heading level 1'",
     "SPEECH OUTPUT: 'Welcome to Orca! heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "2. Return to next result",
    ["KNOWN ISSUE: We're double-presenting this",
     "BRAILLE LINE:  'Welcome to Orca!'",
     "     VISIBLE:  'Welcome to Orca!', cursor=1",
     "BRAILLE LINE:  'Welcome to Orca!'",
     "     VISIBLE:  'Welcome to Orca!', cursor=1",
     "SPEECH OUTPUT: '1.'",
     "SPEECH OUTPUT: 'Welcome to Orca!'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '1.'",
     "SPEECH OUTPUT: 'Welcome to Orca!'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "3. Return to next result",
    ["KNOWN ISSUE: We're double-presenting this",
     "BRAILLE LINE:  'Orca is a free, open source, flexible, extensible, and  $l'",
     "     VISIBLE:  'Orca is a free, open source, fle', cursor=1",
     "BRAILLE LINE:  'Orca is a free, open source, flexible, extensible, and  $l'",
     "     VISIBLE:  'Orca is a free, open source, fle', cursor=5",
     "SPEECH OUTPUT: 'Orca is a free, open source, flexible, extensible, and'",
     "SPEECH OUTPUT: 'Orca is a free, open source, flexible, extensible, and'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "4. Return to next result",
    ["KNOWN ISSUE: We're double-presenting this",
     "BRAILLE LINE:  'synthesis, braille, and magnification, Orca helps provide  $l'",
     "     VISIBLE:  's, braille, and magnification, O', cursor=32",
     "BRAILLE LINE:  'synthesis, braille, and magnification, Orca helps provide  $l'",
     "     VISIBLE:  'raille, and magnification, Orca ', cursor=32",
     "SPEECH OUTPUT: 'synthesis, braille, and magnification, Orca helps provide'",
     "SPEECH OUTPUT: 'synthesis, braille, and magnification, Orca helps provide'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Escape"))
sequence.append(utils.AssertPresentationAction(
    "5. Escape to return to page content",
    ["BRAILLE LINE:  'synthesis, braille, and magnification, Orca helps provide'",
     "     VISIBLE:  'raille, and magnification, Orca ', cursor=32",
     "SPEECH OUTPUT: 'synthesis, braille, and magnification, Orca helps provide  selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Down arrow to be sure we've updated our position",
    ["BRAILLE LINE:  'access to applications and toolkits that support the AT-SPI'",
     "     VISIBLE:  'access to applications and toolk', cursor=1",
     "SPEECH OUTPUT: 'access to applications and toolkits that support the AT-SPI'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
