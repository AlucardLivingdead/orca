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
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the dojo spinner demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction(utils.DojoURLPrefix + "form/test_CheckBox.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("CheckBox Widget Demo", 
                              acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Give the widget a moment to construct itself
#
sequence.append(PauseAction(3000))

########################################################################
# Tab to the cb0 checkbox.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to the cb0 checkbox", 
    [ "BRAILLE LINE:  '< > CheckBox cb0: Vanilla (non-dojo) checkbox (for comparison purposes)'",
     "     VISIBLE:  '< > CheckBox cb0: Vanilla (non-d', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'cb0: Vanilla (non-dojo) checkbox (for comparison purposes) check box not checked'"]))

########################################################################
# Now, change its state.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "change state on cb0 checkbox", 
    ["BRAILLE LINE:  '<x> CheckBox cb0: Vanilla (non-dojo) checkbox (for comparison purposes)'",
     "     VISIBLE:  '<x> CheckBox cb0: Vanilla (non-d', cursor=1",
     "SPEECH OUTPUT: 'checked'"]))

########################################################################
# Tab to the cb1 checkbox.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to the cb1 checkbox", 
    ["BRAILLE LINE:  '< > CheckBox cb1: normal checkbox, with value=foo, clicking generates console log messages'",
     "     VISIBLE:  '< > CheckBox cb1: normal checkbo', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'cb1: normal checkbox, with value=foo, clicking generates console log messages check box not checked'"]))

########################################################################
# Now, change its state.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "change state on cb1 checkbox", 
    ["BRAILLE LINE:  '<x> CheckBox cb1: normal checkbox, with value=foo, clicking generates console log messages'",
     "     VISIBLE:  '<x> CheckBox cb1: normal checkbo', cursor=1",
     "SPEECH OUTPUT: 'checked'"]))

########################################################################
# Tab to the cb2 checkbox.  
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to the cb2 checkbox", 
    ["BRAILLE LINE:  '<x> CheckBox cb2: normal checkbox, initially turned on.  \"onChange\" handler updates: [] '",
     "     VISIBLE:  '<x> CheckBox cb2: normal checkbo', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'cb2: normal checkbox, initially turned on. check box checked'"]))

########################################################################
# Tab to the cb5 checkbox.  Note: cb3 and cb4 are disabled.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to the cb5 checkbox", 
    ["BRAILLE LINE:  '< > CheckBox cb5: Vanilla (non-dojo) checkbox (for comparison purposes)  '",
     "     VISIBLE:  '< > CheckBox cb5: Vanilla (non-d', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'cb5: Vanilla (non-dojo) checkbox (for comparison purposes) check box not checked'"]))

########################################################################
# Tab to the cb6 checkbox.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to the cb6 checkbox", 
    ["BRAILLE LINE:  '<x> CheckBox cb6: instantiated from script  '",
     "     VISIBLE:  '<x> CheckBox cb6: instantiated f', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'cb6: instantiated from script check box checked'"]))

########################################################################
# Tab to the cb7 checkbox.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "Tab to the cb7 checkbox", 
    ["BRAILLE LINE:  '< > CheckBox cb7: normal checkbox. disable Button enable Button set value to \"fish\" Button Reset value+checked Button  \"onChange\" handler updates: [] '",
     "     VISIBLE:  '< > CheckBox cb7: normal checkbo', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'cb7: normal checkbox. check box not checked'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
# BRAILLE LINE:  '< > CheckBox cb7: normal checkbox. disable Button enable Button set value to "fish" Button "onChange" handler updates: [false]'
#     VISIBLE:  '< > CheckBox cb7: normal checkbo', cursor=1
# SPEECH OUTPUT: 'cb7: normal checkbox. check box'
# SPEECH OUTPUT: 'not checked'
# SPEECH OUTPUT: ''
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I", 
    ["BRAILLE LINE:  '< > CheckBox cb7: normal checkbox. disable Button enable Button set value to \"fish\" Button Reset value+checked Button  \"onChange\" handler updates: [] '",
     "     VISIBLE:  '< > CheckBox cb7: normal checkbo', cursor=1",
     "SPEECH OUTPUT: 'cb7: normal checkbox. check box not checked'",
     "SPEECH OUTPUT: ''"]))

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
