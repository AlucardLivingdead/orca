#!/usr/bin/python

"""Test of Dojo spinner presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "Dojo Spinner Widget Test" frame.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the dojo spinner demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction(utils.DojoURLPrefix + "form/test_Spinner.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Dojo Spinner Widget Test", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Give the widget a moment to construct itself.  Move to the top of
# the file because that seems to give us more consistent results for
# the first test.
#
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Control>Home"))

########################################################################
# Tab to the first spinner.  
# 
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to the first spinner",
    ["BUG? - The spinbox is followed by some text - 'onChange:' followed by a grayed out entry containing the text 'not fired yet!'. Either the 'on change' text should be present or, in my opinion, this 'not fired yet!' removed",
     "BRAILLE LINE:  'Spinbox #1: 900 $l not fired yet! $l'",
     "     VISIBLE:  'Spinbox #1: 900 $l not fired yet', cursor=16",
     "BRAILLE LINE:  'Spinbox #1: 900 $l not fired yet! $l'",
     "     VISIBLE:  'Spinbox #1: 900 $l not fired yet', cursor=16",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Spinbox #1: 900 selected spin button'"]))

########################################################################
# Use down arrow to decrement spinner value.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "first spinner decrement 1", 
    ["BRAILLE LINE:  'Spinbox #1: 900 $l'",
     "     VISIBLE:  'Spinbox #1: 900 $l', cursor=0",
     "BRAILLE LINE:  'Spinbox #1: 899 $l'",
     "     VISIBLE:  'Spinbox #1: 899 $l', cursor=0",
     "SPEECH OUTPUT: '899'"]))

########################################################################
# Use down arrow to decrement spinner value.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "first spinner decrement 2", 
    ["BRAILLE LINE:  'Spinbox #1: 899 $l'",
     "     VISIBLE:  'Spinbox #1: 899 $l', cursor=0",
     "BRAILLE LINE:  'Spinbox #1: 898 $l'",
     "     VISIBLE:  'Spinbox #1: 898 $l', cursor=0",
     "SPEECH OUTPUT: '898'"]))

########################################################################
# Use down arrow to decrement spinner value.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "first spinner decrement 3", 
    ["BRAILLE LINE:  'Spinbox #1: 898 $l'",
     "     VISIBLE:  'Spinbox #1: 898 $l', cursor=0",
     "BRAILLE LINE:  'Spinbox #1: 897 $l'",
     "     VISIBLE:  'Spinbox #1: 897 $l', cursor=0",
     "SPEECH OUTPUT: '897'"]))

########################################################################
# Use down arrow to decrement spinner value. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "first spinner decrement 4", 
    ["BRAILLE LINE:  'Spinbox #1: 897 $l'",
     "     VISIBLE:  'Spinbox #1: 897 $l', cursor=0",
     "BRAILLE LINE:  'Spinbox #1: 896 $l'",
     "     VISIBLE:  'Spinbox #1: 896 $l', cursor=0",
     "SPEECH OUTPUT: '896'"]))

########################################################################
# Use down arrow to decrement spinner value.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "first spinner decrement 5", 
    ["BRAILLE LINE:  'Spinbox #1: 896 $l'",
     "     VISIBLE:  'Spinbox #1: 896 $l', cursor=0",
     "BRAILLE LINE:  'Spinbox #1: 895 $l'",
     "     VISIBLE:  'Spinbox #1: 895 $l', cursor=0",
     "SPEECH OUTPUT: '895'"]))

########################################################################
# Use up arrow to increment spinner value. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "first spinner increment 1", 
    ["BRAILLE LINE:  'Spinbox #1: 895 $l'",
     "     VISIBLE:  'Spinbox #1: 895 $l', cursor=0",
     "BRAILLE LINE:  'Spinbox #1: 896 $l'",
     "     VISIBLE:  'Spinbox #1: 896 $l', cursor=0",
     "SPEECH OUTPUT: '896'"]))

########################################################################
# Use up arrow to increment spinner value.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "first spinner increment 2", 
    ["BRAILLE LINE:  'Spinbox #1: 896 $l'",
     "     VISIBLE:  'Spinbox #1: 896 $l', cursor=0",
     "BRAILLE LINE:  'Spinbox #1: 897 $l'",
     "     VISIBLE:  'Spinbox #1: 897 $l', cursor=0",
     "SPEECH OUTPUT: '897'"]))

########################################################################
# Use up arrow to increment spinner value.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "first spinner increment 3", 
    ["BRAILLE LINE:  'Spinbox #1: 897 $l'",
     "     VISIBLE:  'Spinbox #1: 897 $l', cursor=0",
     "BRAILLE LINE:  'Spinbox #1: 898 $l'",
     "     VISIBLE:  'Spinbox #1: 898 $l', cursor=0",
     "SPEECH OUTPUT: '898'"]))

########################################################################
# Use up arrow to increment spinner value.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "first spinner increment 4", 
    ["BRAILLE LINE:  'Spinbox #1: 898 $l'",
     "     VISIBLE:  'Spinbox #1: 898 $l', cursor=0",
     "BRAILLE LINE:  'Spinbox #1: 899 $l'",
     "     VISIBLE:  'Spinbox #1: 899 $l', cursor=0",
     "SPEECH OUTPUT: '899'"]))

########################################################################
# Use up arrow to increment spinner value.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "first spinner increment 5", 
    ["BRAILLE LINE:  'Spinbox #1: 899 $l'",
     "     VISIBLE:  'Spinbox #1: 899 $l', cursor=0",
     "BRAILLE LINE:  'Spinbox #1: 900 $l'",
     "     VISIBLE:  'Spinbox #1: 900 $l', cursor=0",
     "SPEECH OUTPUT: '900'"]))

########################################################################
# Use up arrow to increment spinner value.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "first spinner increment 6", 
    ["BRAILLE LINE:  'Spinbox #1: 900 $l'",
     "     VISIBLE:  'Spinbox #1: 900 $l', cursor=0",
     "BRAILLE LINE:  'Spinbox #1: 901 $l'",
     "     VISIBLE:  'Spinbox #1: 901 $l', cursor=0",
     "SPEECH OUTPUT: '901'"]))

########################################################################
# Use up arrow to increment spinner value.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "first spinner increment 7", 
    ["BRAILLE LINE:  'Spinbox #1: 901 $l'",
     "     VISIBLE:  'Spinbox #1: 901 $l', cursor=0",
     "BRAILLE LINE:  'Spinbox #1: 902 $l'",
     "     VISIBLE:  'Spinbox #1: 902 $l', cursor=0",
     "SPEECH OUTPUT: '902'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "basic whereAmI", 
    ["BRAILLE LINE:  'Spinbox #1: 902 $l'",
     "     VISIBLE:  'Spinbox #1: 902 $l', cursor=0",
     "SPEECH OUTPUT: 'Spinbox #1:'",
     "SPEECH OUTPUT: 'spin button'",
     "SPEECH OUTPUT: '902'",
     "SPEECH OUTPUT: ''"]))

########################################################################
# Close the demo
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
