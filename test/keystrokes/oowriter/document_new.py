#!/usr/bin/python

"""Test to verify what is announced when you create a new document."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>N"))
sequence.append(utils.AssertPresentationAction(
    "New text document",
    ["BRAILLE LINE:  'soffice application Untitled 2 - LibreOffice Writer frame'",
     "     VISIBLE:  'Untitled 2 - LibreOffice Writer ', cursor=1",
     "BRAILLE LINE:  'soffice application Untitled 2 - LibreOffice Writer frame Untitled 2 - LibreOffice Writer root pane Document view  $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'Untitled 2 - LibreOffice Writer frame'",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
