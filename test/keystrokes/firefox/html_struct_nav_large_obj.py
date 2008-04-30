#!/usr/bin/python

"""Test of navigation to 'large objects'
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the frame.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the textattributes.html test page.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction(utils.htmlURLPrefix + "textattributes.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Text Attributes and Alignment Test Page", 
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file", 
    ["BRAILLE LINE:  'Text Attributes h1'",
     "     VISIBLE:  'Text Attributes h1', cursor=1",
     "SPEECH OUTPUT: 'Text Attributes heading  '",
     "SPEECH OUTPUT: 'level 1'"]))

########################################################################
# Navigate to the first 'large chunk'.  It is the 1st paragraph under 'From 
# Shakespeare's Hamlet'  The following will be presented.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("o"))
sequence.append(utils.AssertPresentationAction(
    "First large chunk", 
    ["BRAILLE LINE:  'I have of late but'",
     "     VISIBLE:  'I have of late but', cursor=1",
     "BRAILLE LINE:  'I have of late but'",
     "     VISIBLE:  'I have of late but', cursor=1",
     "SPEECH OUTPUT: 'I have of late but",
     "wherefore I know not lost all my mirth,",
     "forgone all custom of exercises;",
     "and indeed, it goes so heavily with",
     "my disposition that this goodly frame,",
     "the earth, seems to me a sterile promontory;",
     "this most excellent canopy, the air, look you,",
     "this brave o'erhanging firmament,",
     "this majestical roof fretted with golden fire",
     "why, it appeareth no other thing to me than a foul",
     "and pestilent congregation of vapours.",
     "What a piece of work is a man!",
     "how noble in reason! how infinite in faculties!",
     "in form and moving how express and admirable!",
     "in action how like an angel!",
     "in apprehension how like a god!",
     "the beauty of the world, the paragon of animals!'"]))

########################################################################
# Navigate to the next 'large chunk'.  It is the 2nd paragraph under 'From 
# Shakespeare's Hamlet' 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("o"))
sequence.append(utils.AssertPresentationAction(
    "Second large chunk", 
    ["BRAILLE LINE:  'I have of late but'",
     "     VISIBLE:  'I have of late but', cursor=1",
     "SPEECH OUTPUT: 'I have of late but",
     "wherefore I know not lost all my mirth,",
     "forgone all custom of exercises;",
     "and indeed, it goes so heavily with",
     "my disposition that this goodly frame,",
     "the earth, seems to me a sterile promontory;",
     "this most excellent canopy, the air, look you,",
     "this brave o'erhanging firmament,",
     "this majestical roof fretted with golden fire",
     "why, it appeareth no other thing to me than a foul",
     "and pestilent congregation of vapours.",
     "What a piece of work is a man!",
     "how noble in reason! how infinite in faculties!",
     "in form and moving how express and admirable!",
     "in action how like an angel!",
     "in apprehension how like a god!",
     "the beauty of the world, the paragon of animals!'"]))

########################################################################
# Navigate to the next 'large chunk'.  It is the 3nd paragraph under 'From 
# Shakespeare's Hamlet'  The following will be presented.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("o"))
sequence.append(utils.AssertPresentationAction(
    "Third large chunk", 
    ["BRAILLE LINE:  'I have of late but'",
     "     VISIBLE:  'I have of late but', cursor=1",
     "SPEECH OUTPUT: 'I have of late but",
     "wherefore I know not lost all my mirth,",
     "forgone all custom of exercises;",
     "and indeed, it goes so heavily with",
     "my disposition that this goodly frame,",
     "the earth, seems to me a sterile promontory;",
     "this most excellent canopy, the air, look you,",
     "this brave o'erhanging firmament,",
     "this majestical roof fretted with golden fire",
     "why, it appeareth no other thing to me than a foul",
     "and pestilent congregation of vapours.",
     "What a piece of work is a man!",
     "how noble in reason! how infinite in faculties!",
     "in form and moving how express and admirable!",
     "in action how like an angel!",
     "in apprehension how like a god!",
     "the beauty of the world, the paragon of animals!'"]))

########################################################################
# Navigate to the next 'large chunk'.  It is the 2nd paragraph under 'From 
# Wislawa Szymborska - 1972'  The following will be presented.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("o"))
sequence.append(utils.AssertPresentationAction(
    "Fourth large chunk", 
    ["BRAILLE LINE:  'I know how to cope with misfortune,'",
     "     VISIBLE:  'I know how to cope with misfortu', cursor=1",
     "SPEECH OUTPUT: 'I know how to cope with misfortune, ",
     "how to endure bad news, ",
     "take the edge of injustice, ",
     "make up for the absence of God, ",
     "help pick out your widow's weeds. ",
     "What are you waiting for - ",
     "have faith in chemistry's compassion.'"]))

########################################################################
# Navigate to the previous 'large chunk'.  It is the 3rd paragraph under 'From 
# Shakespeare's Hamlet'  The following will be presented.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>o"))
sequence.append(utils.AssertPresentationAction(
    "Shift + o to third large chunk", 
    ["BRAILLE LINE:  'I have of late but'",
     "     VISIBLE:  'I have of late but', cursor=1",
     "SPEECH OUTPUT: 'I have of late but",
     "wherefore I know not lost all my mirth,",
     "forgone all custom of exercises;",
     "and indeed, it goes so heavily with",
     "my disposition that this goodly frame,",
     "the earth, seems to me a sterile promontory;",
     "this most excellent canopy, the air, look you,",
     "this brave o'erhanging firmament,",
     "this majestical roof fretted with golden fire",
     "why, it appeareth no other thing to me than a foul",
     "and pestilent congregation of vapours.",
     "What a piece of work is a man!",
     "how noble in reason! how infinite in faculties!",
     "in form and moving how express and admirable!",
     "in action how like an angel!",
     "in apprehension how like a god!",
     "the beauty of the world, the paragon of animals!'"]))

########################################################################
# Close the demo
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_name="Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
