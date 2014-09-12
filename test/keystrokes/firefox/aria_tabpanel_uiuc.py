#!/usr/bin/python

"""Test of UIUC tab panel presentation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Give focus to a widget in the first Tab",
    ["BRAILLE LINE:  '&=y Thick and cheesy radio button'",
     "     VISIBLE:  '&=y Thick and cheesy radio butto', cursor=0",
     "SPEECH OUTPUT: 'Thick and cheesy'",
     "SPEECH OUTPUT: 'selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Page_Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Ctrl Page Down to second tab",
    ["BRAILLE LINE:  'Crust page tab Veggies page tab Carnivore Delivery'",
     "     VISIBLE:  'Veggies page tab Carnivore Deliv', cursor=1",
     "BRAILLE LINE:  'Focus mode'",
     "     VISIBLE:  'Focus mode', cursor=0",
     "BRAILLE LINE:  'Veggies page tab'",
     "     VISIBLE:  'Veggies page tab', cursor=1",
     "SPEECH OUTPUT: 'Veggies'",
     "SPEECH OUTPUT: 'page tab'",
     "SPEECH OUTPUT: 'Focus mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Right arrow to third tab",
    ["BRAILLE LINE:  'Carnivore page tab'",
     "     VISIBLE:  'Carnivore page tab', cursor=1",
     "BRAILLE LINE:  'Carnivore page tab'",
     "     VISIBLE:  'Carnivore page tab', cursor=1",
     "SPEECH OUTPUT: 'Carnivore'",
     "SPEECH OUTPUT: 'page tab'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(utils.AssertPresentationAction(
    "4. basic whereAmI",
    ["BRAILLE LINE:  'Carnivore page tab'",
     "     VISIBLE:  'Carnivore page tab', cursor=1",
     "SPEECH OUTPUT: 'page tab list'",
     "SPEECH OUTPUT: 'Carnivore'",
     "SPEECH OUTPUT: 'page tab 3 of 4'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "5. Right arrow to fourth tab",
    ["BRAILLE LINE:  'Delivery page tab'",
     "     VISIBLE:  'Delivery page tab', cursor=1",
     "BRAILLE LINE:  'Delivery page tab'",
     "     VISIBLE:  'Delivery page tab', cursor=1",
     "SPEECH OUTPUT: 'Delivery'",
     "SPEECH OUTPUT: 'page tab'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "6. Left arrow back to third tab",
    ["BRAILLE LINE:  'Carnivore page tab'",
     "     VISIBLE:  'Carnivore page tab', cursor=1",
     "BRAILLE LINE:  'Carnivore page tab'",
     "     VISIBLE:  'Carnivore page tab', cursor=1",
     "SPEECH OUTPUT: 'Carnivore'",
     "SPEECH OUTPUT: 'page tab'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "7. Press Tab to move into the third page",
    ["BRAILLE LINE:  '< > Pepperoni check box'",
     "     VISIBLE:  '< > Pepperoni check box', cursor=1",
     "BRAILLE LINE:  'Browse mode'",
     "     VISIBLE:  'Browse mode', cursor=0",
     "SPEECH OUTPUT: 'Pepperoni'",
     "SPEECH OUTPUT: 'check box not checked'",
     "SPEECH OUTPUT: 'Browse mode' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(utils.AssertPresentationAction(
    "8. Toggle the focused checkbox",
    ["BRAILLE LINE:  '< > Pepperoni check box'",
     "     VISIBLE:  '< > Pepperoni check box', cursor=1",
     "BRAILLE LINE:  '<x> Pepperoni check box'",
     "     VISIBLE:  '<x> Pepperoni check box', cursor=0",
     "SPEECH OUTPUT: 'checked'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
