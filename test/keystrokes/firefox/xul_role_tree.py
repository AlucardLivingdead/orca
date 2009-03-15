# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of tree output using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Open the "Bookmarks" menu, Down Arrow to Show All Bookmarks, then 
# press Return.
#
sequence.append(PauseAction(3000))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>b"))
sequence.append(utils.AssertPresentationAction(
    "Bookmarks menu",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ToolBar Bookmarks Menu'",
     "     VISIBLE:  'Bookmarks Menu', cursor=1",
     "BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ToolBar Application MenuBar Bookmark This Page\(Control D\)'",
     "     VISIBLE:  'Bookmark This Page(Control D)', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Bookmarks menu'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Bookmark This Page Control D'"]))

sequence.append(PauseAction(3000))
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Down Arrow in Bookmarks menu",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application " + utils.firefoxFrameNames + " Frame ToolBar Application MenuBar Organize Bookmarks...'",
     "     VISIBLE:  'Organize Bookmarks...', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Organize Bookmarks…'"]))

sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))

########################################################################
# Press Shift+Tab to move to the tree of bookmarks on the left.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Tab", 1000))
sequence.append(utils.AssertPresentationAction(
    "Shift Tab for tree",
    ["BUG? - We are no longer speaking the Level",
     "BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Library Frame Tree All Bookmarks ListItem'",
     "     VISIBLE:  'All Bookmarks ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'All Bookmarks expanded'"]))

########################################################################
# Press Down Arrow twice to give focus to the Bookmarks Menu list item.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Down Arrow in tree",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Library Frame Tree Bookmarks Toolbar ListItem'",
     "     VISIBLE:  'Bookmarks Toolbar ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Bookmarks Toolbar collapsed'",
     "SPEECH OUTPUT: 'tree level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Down Arrow in tree",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Library Frame Tree Bookmarks Menu ListItem'",
     "     VISIBLE:  'Bookmarks Menu ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Bookmarks Menu collapsed'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Library Frame Tree Bookmarks Menu ListItem'",
     "     VISIBLE:  'Bookmarks Menu ListItem', cursor=1",
     "SPEECH OUTPUT: 'list item'",
     "SPEECH OUTPUT: 'Bookmarks Menu'",
     "SPEECH OUTPUT: 'item 2 of 3'",
     "SPEECH OUTPUT: 'collapsed'",
     "SPEECH OUTPUT: 'tree level 2'"]))

########################################################################
# Press Right Arrow to expand this item.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Right Arrow to expand folder", 
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Library Frame Tree Bookmarks Menu ListItem'",
     "     VISIBLE:  'Bookmarks Menu ListItem', cursor=1",
     "SPEECH OUTPUT: 'expanded'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Library Frame Tree Bookmarks Menu ListItem'",
     "     VISIBLE:  'Bookmarks Menu ListItem', cursor=1",
     "SPEECH OUTPUT: 'list item'",
     "SPEECH OUTPUT: 'Bookmarks Menu'",
     "SPEECH OUTPUT: 'item 2 of 3'",
     "SPEECH OUTPUT: 'expanded'",
     "SPEECH OUTPUT: 'tree level 2'"]))

########################################################################
# Press Down Arrow to give focus to the next item, Recently Bookmarked.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Down Arrow in tree",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Library Frame Tree Recently Bookmarked ListItem'",
     "     VISIBLE:  'Recently Bookmarked ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Recently Bookmarked'",
     "SPEECH OUTPUT: 'tree level 3'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Library Frame Tree Recently Bookmarked ListItem'",
     "     VISIBLE:  'Recently Bookmarked ListItem', cursor=1",
     "SPEECH OUTPUT: 'list item'",
     "SPEECH OUTPUT: 'Recently Bookmarked'",
     "SPEECH OUTPUT: 'item 1 of 4'",
     "SPEECH OUTPUT: 'tree level 3'"]))

########################################################################
# Press Up Arrow to work back to the Bookmarks Toolbar list item.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Up Arrow in tree",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Library Frame Tree Bookmarks Menu ListItem'",
     "     VISIBLE:  'Bookmarks Menu ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Bookmarks Menu expanded'",
     "SPEECH OUTPUT: 'tree level 2'"]))

########################################################################
# Press Left Arrow to collapse this item.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left Arrow to collapse folder", 
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Library Frame Tree Bookmarks Menu ListItem'",
     "     VISIBLE:  'Bookmarks Menu ListItem', cursor=1",
     "SPEECH OUTPUT: 'collapsed'"]))

########################################################################
# Press Up Arrow to work back to the Bookmarks Toolbar list item.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Up Arrow in tree",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Library Frame Tree Bookmarks Toolbar ListItem'",
     "     VISIBLE:  'Bookmarks Toolbar ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Bookmarks Toolbar collapsed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Up Arrow in tree",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Library Frame Tree All Bookmarks ListItem'",
     "     VISIBLE:  'All Bookmarks ListItem', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'All Bookmarks expanded'",
     "SPEECH OUTPUT: 'tree level 1'"]))

########################################################################
# Press Tab to return to the tree table that had focus initially.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab back to tree table",
    ["BRAILLE LINE:  '" + utils.firefoxAppNames + " Application Library Frame ScrollPane TreeTable Name ColumnHeader Bookmarks Toolbar   TREE LEVEL 1'",
     "     VISIBLE:  'Bookmarks Toolbar   TREE LEVEL 1', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Name column header'",
     "SPEECH OUTPUT: 'Bookmarks Toolbar  '",
     "SPEECH OUTPUT: ' not selected'"]))

########################################################################
# Now that the Places Manager is back to its pre-explored state,
# press Alt F4 to close it.
#
sequence.append(KeyComboAction("<Alt>F4"))

########################################################################
# Wait for the focus to be back on the blank Firefox window.
#
sequence.append(WaitForWindowActivate("",None))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
