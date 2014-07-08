#!/usr/bin/python

"""Test of tooltips."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Printing"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))

sequence.append(KeyComboAction("<Alt>e"))
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>F1"))
sequence.append(utils.AssertPresentationAction(
    "1. Show tooltip",
    ["BRAILLE LINE:  'Specify one or more page ranges,",
     " e.g. 1-3,7,11'",
     "     VISIBLE:  'Specify one or more page ranges,', cursor=0",
     "SPEECH OUTPUT: 'Specify one or more page ranges,",
     " e.g. 1-3,7,11'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>F1"))
sequence.append(utils.AssertPresentationAction(
    "2. Hide tooltip",
    ["KNOWN ISSUE: Too much context",
     "BRAILLE LINE:  'gtk3-demo application Print dialog General page tab Range panel Range &=y Pages: radio button'",
     "     VISIBLE:  '&=y Pages: radio button', cursor=1",
     "SPEECH OUTPUT: 'Print'",
     "SPEECH OUTPUT: 'General'",
     "SPEECH OUTPUT: 'page tab'",
     "SPEECH OUTPUT: 'Range'",
     "SPEECH OUTPUT: 'panel'",
     "SPEECH OUTPUT: 'Pages:'",
     "SPEECH OUTPUT: 'selected radio button'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
