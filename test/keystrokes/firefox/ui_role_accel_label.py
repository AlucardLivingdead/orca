#!/usr/bin/python

"""Test of menu accelerator label output of Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Alt>f"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Down Arrow in File menu",
    ["BRAILLE LINE:  'Firefox application Mozilla Firefox frame Menu Bar tool bar Application menu bar New Window(Ctrl+N)'",
     "     VISIBLE:  'New Window(Ctrl+N)', cursor=1",
     "SPEECH OUTPUT: 'New Window Ctrl+N'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down Arrow in File menu",
    ["BRAILLE LINE:  'Firefox application Mozilla Firefox frame Menu Bar tool bar Application menu bar New Private Window(Shift+Ctrl+P)'",
     "     VISIBLE:  'New Private Window(Shift+Ctrl+P)', cursor=1",
     "SPEECH OUTPUT: 'New Private Window Shift+Ctrl+P'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "3. Basic Where Am I",
    ["BRAILLE LINE:  'Firefox application Mozilla Firefox frame Menu Bar tool bar Application menu bar New Private Window(Shift+Ctrl+P)'",
     "     VISIBLE:  'New Private Window(Shift+Ctrl+P)', cursor=1",
     "SPEECH OUTPUT: 'File menu'",
     "SPEECH OUTPUT: 'Menu Bar tool bar New Private Window Shift+Ctrl+P 3 of 12.'",
     "SPEECH OUTPUT: 'W'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
