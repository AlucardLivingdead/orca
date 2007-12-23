# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of line navigation output of Firefox on GNOME bugzilla's form
for entering bugs. Note that this is based on the following Firefox 3
build: Gecko/2007122122 Minefield/3.0b3pre.  In addition, it is using
the current patch to bug 505102 to handle a significant change
made in the current Firefox.  The assertions in the test will
fail if your configuration is different.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the local "simple form" test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "enter-bug-form.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

sequence.append(WaitForFocus("Enter Bug: orca",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file",
    ["BRAILLE LINE:  'Enter Bug: orca – This page lets you enter a new bug into Bugzilla. h1'",
     "     VISIBLE:  'Enter Bug: orca – This page le', cursor=1",
     "SPEECH OUTPUT: 'Enter Bug: orca – This page lets you enter a new bug into Bugzilla. heading  '",
     "SPEECH OUTPUT: 'level 1'"]))

########################################################################
# Down Arrow.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Before reporting a bug, please read the bug writing guidelines Link , please look at the list of most frequently Link'",
     "     VISIBLE:  'Before reporting a bug, please r', cursor=1",
     "SPEECH OUTPUT: 'Before reporting a bug, please read the bug writing guidelines link , please look at the list of most frequently link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'reported bugs Link , and please search Link  or browse Link  for the bug.'",
     "     VISIBLE:  'reported bugs Link , and please ', cursor=1",
     "SPEECH OUTPUT: 'reported bugs link , and please search link  or browse link  for the bug.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'reported bugs Link , and please search Link  or browse Link  for the bug.'",
     "     VISIBLE:  'reported bugs Link , and please ', cursor=1",
     "SPEECH OUTPUT: 'reported bugs link , and please search link  or browse link  for the bug.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Reporter: joanmarie.diggs@gmail.com Product: orca'",
     "     VISIBLE:  'Reporter: joanmarie.diggs@gmail.', cursor=1",
     "SPEECH OUTPUT: 'Reporter: joanmarie.diggs@gmail.com Product: orca'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Version: List Component Link : List'",
     "     VISIBLE:  'Version: List Component Link : L', cursor=1",
     "SPEECH OUTPUT: 'Version: List with 9 items Component link : List with 5 items'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  ' '",
     "     VISIBLE:  ' ', cursor=1",
     "SPEECH OUTPUT: ' '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'GNOME Link Unspecified Combo'",
     "     VISIBLE:  'GNOME Link Unspecified Combo', cursor=1",
     "SPEECH OUTPUT: 'GNOME link Unspecified combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'version Link :'",
     "     VISIBLE:  'version Link :', cursor=1",
     "SPEECH OUTPUT: 'version link :'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Unspecified Combo'",
     "     VISIBLE:  'Unspecified Combo', cursor=1",
     "SPEECH OUTPUT: 'Unspecified combo box'"]))

########################################################################
# Tab to move off of the combo box.  Then continue with Down Arrow.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab", 
    ["BRAILLE LINE:  'OS Link : Linux Combo'",
     "     VISIBLE:  'OS Link : Linux Combo', cursor=0",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'OS link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Severity Link : normal Combo'",
     "     VISIBLE:  'Severity Link : normal Combo', cursor=1",
     "SPEECH OUTPUT: 'Severity link : normal combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  ' '",
     "     VISIBLE:  ' ', cursor=1",
     "SPEECH OUTPUT: ' '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Summary:  $l'",
     "     VISIBLE:  'Summary:  $l', cursor=1",
     "SPEECH OUTPUT: 'Summary: text '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Description:  $l'",
     "     VISIBLE:  'Description:  $l', cursor=1",
     "SPEECH OUTPUT: 'Description: text '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BUG? - We seem to be landing in a space after the entry.",
     "BRAILLE LINE:  ' '",
     "     VISIBLE:  ' ', cursor=1",
     "SPEECH OUTPUT: ' '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  ' '",
     "     VISIBLE:  ' ', cursor=1",
     "SPEECH OUTPUT: ' '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Optional Fields'",
     "     VISIBLE:  'Optional Fields', cursor=1",
     "SPEECH OUTPUT: 'Optional Fields'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Cc:  $l'",
     "     VISIBLE:  'Cc:  $l', cursor=1",
     "SPEECH OUTPUT: 'Cc: text '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Keywords Link :  $l'",
     "     VISIBLE:  'Keywords Link :  $l', cursor=1",
     "SPEECH OUTPUT: 'Keywords link : text '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Depends on:  $l'",
     "     VISIBLE:  'Depends on:  $l', cursor=1",
     "SPEECH OUTPUT: 'Depends on: text '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Blocks:  $l'",
     "     VISIBLE:  'Blocks:  $l', cursor=1",
     "SPEECH OUTPUT: 'Blocks: text '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Commit Button       Remember values as bookmarkable template Button'",
     "     VISIBLE:  'Commit Button       Remember', cursor=1",
     "SPEECH OUTPUT: 'Commit button       Remember values as bookmarkable template button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'We've made a guess at your operating system. Please check it and, if we got it wrong, email'",
     "     VISIBLE:  'We've made a guess at your opera', cursor=1",
     "SPEECH OUTPUT: 'We've made a guess at your operating system. Please check it and, if we got it wrong, email'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'bugmaster@gnome.org.'",
     "     VISIBLE:  'bugmaster@gnome.org.', cursor=1",
     "SPEECH OUTPUT: 'bugmaster@gnome.org.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Saved Searches: All Orca Link  | Firefox Link  | open orca Link  | Open RFEs Link'",
     "     VISIBLE:  'Saved Searches: All Orca Link ', cursor=1",
     "SPEECH OUTPUT: 'Saved Searches: All Orca link  | Firefox link  | open orca link  | Open RFEs link'"]))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
