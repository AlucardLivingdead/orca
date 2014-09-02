#!/usr/bin/python

"""Test of Dojo toolbar presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Down Arrow",
    ["BRAILLE LINE:  'Toolbar from markup h2'",
     "     VISIBLE:  'Toolbar from markup h2', cursor=1",
     "SPEECH OUTPUT: 'Toolbar from markup'",
     "SPEECH OUTPUT: 'heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down Arrow",
    ["BRAILLE LINE:  'input before toolbar1 $l'",
     "     VISIBLE:  'input before toolbar1 $l', cursor=1",
     "SPEECH OUTPUT: 'entry'",
     "SPEECH OUTPUT: 'input before toolbar1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Down Arrow",
    ["KNOWN ISSUE: Whether or not this is the ideal presentation is questionable. But it is more correct that what we were doing.",
     "BRAILLE LINE:  'Buttons: Copy Toggles: Italic Dropdowns: TooltipDialogColorPalette Combos: Menusave options push button Menu2 push button save options2 push button'",
     "     VISIBLE:  'Buttons: Copy Toggles: Italic Dr', cursor=1",
     "SPEECH OUTPUT: 'Buttons: '",
     "SPEECH OUTPUT: 'Copy'",
     "SPEECH OUTPUT: ' Toggles: '",
     "SPEECH OUTPUT: 'Italic'",
     "SPEECH OUTPUT: 'push button'",
     "SPEECH OUTPUT: 'Italic'",
     "SPEECH OUTPUT: 'push button'",
     "SPEECH OUTPUT: 'push button'",
     "SPEECH OUTPUT: 'Dropdowns: '",
     "SPEECH OUTPUT: ' Combos: '",
     "SPEECH OUTPUT: 'Menu'",
     "SPEECH OUTPUT: 'save options'",
     "SPEECH OUTPUT: 'push button'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'clickable'",
     "SPEECH OUTPUT: 'save options2'",
     "SPEECH OUTPUT: 'push button'",
     "SPEECH OUTPUT: 'Ordered list'",
     "SPEECH OUTPUT: 'push button'",
     "SPEECH OUTPUT: 'push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Down Arrow",
    ["BRAILLE LINE:  'input after toolbar1 $l'",
     "     VISIBLE:  'input after toolbar1 $l', cursor=1",
     "SPEECH OUTPUT: 'entry'",
     "SPEECH OUTPUT: 'input after toolbar1'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
