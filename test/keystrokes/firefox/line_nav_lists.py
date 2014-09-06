#!/usr/bin/python

"""Test of HTML list presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'Welcome to a List of Lists h1'",
     "     VISIBLE:  'Welcome to a List of Lists h1', cursor=1",
     "SPEECH OUTPUT: 'Welcome to a List of Lists",
     "SPEECH OUTPUT: 'heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'Lists are not only fun to make, they are fun to use. They help us:'",
     "     VISIBLE:  'Lists are not only fun to make, ', cursor=1",
     "SPEECH OUTPUT: 'Lists are not only fun to make, they are fun to use. They help us: '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  '1.remember what the heck we are doing each day'",
     "     VISIBLE:  '1.remember what the heck we are ', cursor=1",
     "SPEECH OUTPUT: '1.remember what the heck we are doing each day'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  '2.arrange long and arbitrary lines of text into ordered lists that are pleasing to the eye and suggest some'",
     "     VISIBLE:  '2.arrange long and arbitrary lin', cursor=1",
     "SPEECH OUTPUT: '2.arrange long and arbitrary lines of text into ordered lists that are pleasing to the eye and suggest some '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'sense of priority, even if it is artificial'",
     "     VISIBLE:  'sense of priority, even if it is', cursor=1",
     "SPEECH OUTPUT: 'sense of priority, even if it is artificial'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down",
    ["BRAILLE LINE:  '3.look really cool when we carry them around on yellow Post-Itstm.'",
     "     VISIBLE:  '3.look really cool when we carry', cursor=1",
     "SPEECH OUTPUT: '3.look really cool when we carry them around on yellow Post-Itstm.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["BRAILLE LINE:  '4.and that other thing I keep forgetting.'",
     "     VISIBLE:  '4.and that other thing I keep fo', cursor=1",
     "SPEECH OUTPUT: '4.and that other thing I keep forgetting.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Down",
    ["BRAILLE LINE:  'Your ordered lists can start at a strange number, like:'",
     "     VISIBLE:  'Your ordered lists can start at ', cursor=1",
     "SPEECH OUTPUT: 'Your ordered lists can start at a strange number, like: '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Down",
    ["BRAILLE LINE:  'VI.And use roman numerals,'",
     "     VISIBLE:  'VI.And use roman numerals,', cursor=1",
     "SPEECH OUTPUT: 'VI.And use roman numerals,'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Down",
    ["BRAILLE LINE:  'g.You might try using letters as well,'",
     "     VISIBLE:  'g.You might try using letters as', cursor=1",
     "SPEECH OUTPUT: 'g.You might try using letters as well,'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Down",
    ["BRAILLE LINE:  'H.Maybe you prefer Big Letters,'",
     "     VISIBLE:  'H.Maybe you prefer Big Letters,', cursor=1",
     "SPEECH OUTPUT: 'H.Maybe you prefer Big Letters,'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Down",
    ["BRAILLE LINE:  'ix.or small roman numerals'",
     "     VISIBLE:  'ix.or small roman numerals', cursor=1",
     "SPEECH OUTPUT: 'ix.or small roman numerals'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Up",
    ["BRAILLE LINE:  'H.Maybe you prefer Big Letters,'",
     "     VISIBLE:  'H.Maybe you prefer Big Letters,', cursor=1",
     "SPEECH OUTPUT: 'H.Maybe you prefer Big Letters,'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "14. Line Up",
    ["BRAILLE LINE:  'g.You might try using letters as well,'",
     "     VISIBLE:  'g.You might try using letters as', cursor=1",
     "SPEECH OUTPUT: 'g.You might try using letters as well,'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "15. Line Up",
    ["BRAILLE LINE:  'VI.And use roman numerals,'",
     "     VISIBLE:  'VI.And use roman numerals,', cursor=1",
     "SPEECH OUTPUT: 'VI.And use roman numerals,'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "16. Line Up",
    ["BRAILLE LINE:  'Your ordered lists can start at a strange number, like:'",
     "     VISIBLE:  'Your ordered lists can start at ', cursor=1",
     "SPEECH OUTPUT: 'Your ordered lists can start at a strange number, like: '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "17. Line Up",
    ["BRAILLE LINE:  '4.and that other thing I keep forgetting.'",
     "     VISIBLE:  '4.and that other thing I keep fo', cursor=1",
     "SPEECH OUTPUT: '4.and that other thing I keep forgetting.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "18. Line Up",
    ["BRAILLE LINE:  '3.look really cool when we carry them around on yellow Post-Itstm.'",
     "     VISIBLE:  '3.look really cool when we carry', cursor=1",
     "SPEECH OUTPUT: '3.look really cool when we carry them around on yellow Post-Itstm.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "19. Line Up",
    ["BRAILLE LINE:  'sense of priority, even if it is artificial'",
     "     VISIBLE:  'sense of priority, even if it is', cursor=1",
     "SPEECH OUTPUT: 'sense of priority, even if it is artificial'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "20. Line Up",
    ["BRAILLE LINE:  '2.arrange long and arbitrary lines of text into ordered lists that are pleasing to the eye and suggest some'",
     "     VISIBLE:  '2.arrange long and arbitrary lin', cursor=1",
     "SPEECH OUTPUT: '2.arrange long and arbitrary lines of text into ordered lists that are pleasing to the eye and suggest some '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "21. Line Up",
    ["BRAILLE LINE:  '1.remember what the heck we are doing each day'",
     "     VISIBLE:  '1.remember what the heck we are ', cursor=1",
     "SPEECH OUTPUT: '1.remember what the heck we are doing each day'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "22. Line Up",
    ["BRAILLE LINE:  'Lists are not only fun to make, they are fun to use. They help us:'",
     "     VISIBLE:  'Lists are not only fun to make, ', cursor=1",
     "SPEECH OUTPUT: 'Lists are not only fun to make, they are fun to use. They help us: '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "23. Line Up",
    ["BRAILLE LINE:  'Welcome to a List of Lists h1'",
     "     VISIBLE:  'Welcome to a List of Lists h1', cursor=1",
     "SPEECH OUTPUT: 'Welcome to a List of Lists",
     "SPEECH OUTPUT: 'heading level 1'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
