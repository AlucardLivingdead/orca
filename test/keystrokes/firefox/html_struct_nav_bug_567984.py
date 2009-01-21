# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of table cell navigation output of Firefox. 
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the local "simple form" test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "bug-567984.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

sequence.append(WaitForFocus("",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'Index Vakbarát Hírportál h1'",
     "     VISIBLE:  'Index Vakbarát Hírportál h1', cursor=1",
     "SPEECH OUTPUT: 'Index Vakbarát Hírportál heading level 1'"]))

########################################################################
# H to move amongst headings
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "2. h",
    ["BRAILLE LINE:  'Legfrissebb hírek h2'",
     "     VISIBLE:  'Legfrissebb hírek h2', cursor=1",
     "SPEECH OUTPUT: 'Legfrissebb hírek heading level 2'"]))

########################################################################
# H to move amongst headings
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "3. h",
    ["BRAILLE LINE:  'Izrael bejelentette az  h3'",
     "     VISIBLE:  'Izrael bejelentette az  h3', cursor=1",
     "SPEECH OUTPUT: 'Izrael bejelentette az ",
     "egyoldalú tûzszünetet link heading level 3'"]))

########################################################################
# H to move amongst headings
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "4. h",
    ["BRAILLE LINE:  'Videók a Hudsonba zuhanó repülõrõl h3'",
     "     VISIBLE:  'Videók a Hudsonba zuhanó repülõr', cursor=1",
     "SPEECH OUTPUT: 'Videók a Hudsonba zuhanó repülõrõl link heading level 3'"]))

########################################################################
# H to move amongst headings
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "5. h",
    ["BRAILLE LINE:  'Újabb pénzügyi guru tûnt el, pénzzel együtt h3'",
     "     VISIBLE:  'Újabb pénzügyi guru tûnt el, pén', cursor=1",
     "SPEECH OUTPUT: 'Újabb pénzügyi guru tûnt el, pénzzel együtt link heading level 3'"]))

########################################################################
# Down Arrow to move to some text in the document frame
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Down",
    ["BRAILLE LINE:  'A 75 éves Arthur Nadeltõl több százmillió dollár követelnének az ügyfelei, de még a férfit sem találják.'",
     "     VISIBLE:  'A 75 éves Arthur Nadeltõl több s', cursor=1",
     "SPEECH OUTPUT: 'A 75 éves Arthur Nadeltõl több százmillió dollár követelnének az ügyfelei, de még a férfit sem találják.'"]))

########################################################################
# Down Arrow to move to some text in the document frame
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Down",
    ["BRAILLE LINE:  '1150 embert utcára tesz a pécsi Elcoteq h3'",
     "     VISIBLE:  '1150 embert utcára tesz a pécsi ', cursor=1",
     "SPEECH OUTPUT: '1150 embert utcára tesz a pécsi Elcoteq link heading level 3'"]))

########################################################################
# H to move to the next heading. It should NOT be the first heading.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("h"))
sequence.append(utils.AssertPresentationAction(
    "8. h",
    ["BRAILLE LINE:  'Hamarosan újraindul a gázszállítás h3'",
     "     VISIBLE:  'Hamarosan újraindul a gázszállít', cursor=1",
     "SPEECH OUTPUT: 'Hamarosan újraindul a gázszállítás link heading level 3'"]))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
