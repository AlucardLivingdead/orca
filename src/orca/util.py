# Orca
#
# Copyright 2005-2007 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

"""Provides various utility functions for Orca."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2007 Sun Microsystems Inc."
__license__   = "LGPL"

import string

import atspi
import chnames
import debug
import input_event
import orca_prefs
import orca_state
import phonnames
import punctuation_settings
import pronunciation_dict
import rolenames
import settings
import speech
import speechserver

from orca_i18n import _ # for gettext support

# Unicode currency symbols (populated by the getUnicodeCurrencySymbols()
# routine).
#
_unicodeCurrencySymbols = []

def isSameObject(obj1, obj2):
    if (obj1 == obj2):
        return True
    elif (not obj1) or (not obj2):
        return False

    try:
        if obj1.name != obj2.name:
            return False

        # When we're looking at children of objects that manage
        # their descendants, we will often get different objects
        # that point to the same logical child.  We want to be able
        # to determine if two objects are in fact pointing to the same child.
        # If we cannot do so easily (i.e., object equivalence), we examine
        # the hierarchy and the object index at each level.
        #
        parent1 = obj1
        parent2 = obj2
        while (parent1 and parent2 and \
                parent1.state.count(atspi.Accessibility.STATE_TRANSIENT) and \
                parent2.state.count(atspi.Accessibility.STATE_TRANSIENT)):
            if parent1.index != parent2.index:
                return False
            parent1 = parent1.parent
            parent2 = parent2.parent
        if parent1 and parent2 and parent1 == parent2:
            return True
    except:
        pass

    # In java applications, TRANSIENT state is missing for tree items
    # (fix for bug #352250)
    #
    try:
        parent1 = obj1
        parent2 = obj2
        while parent1 and parent2 and \
                parent1.role == rolenames.ROLE_LABEL and \
                parent2.role == rolenames.ROLE_LABEL:
            if parent1.index != parent2.index:
                return False
            parent1 = parent1.parent
            parent2 = parent2.parent
        if parent1 and parent2 and parent1 == parent2:
            return True
    except:
        pass

    return False

def appendString(text, newText, delimiter=" "):
    """Appends the newText to the given text with the delimiter in between
    and returns the new string.  Edge cases, such as no initial text or
    no newText, are handled gracefully."""

    if (not newText) or (len(newText) == 0):
        return text
    elif text and len(text):
        return text + delimiter + newText
    else:
        return newText

def getUnicodeCurrencySymbols():
    """Return a list of the unicode currency symbols, populating the list
    if this is the first time that this routine has been called.

    Returns a list of unicode currency symbols.
    """

    global _unicodeCurrencySymbols

    if not _unicodeCurrencySymbols:
        _unicodeCurrencySymbols = [ \
            u'\u0024',     # dollar sign
            u'\u00A2',     # cent sign
            u'\u00A3',     # pound sign
            u'\u00A4',     # currency sign
            u'\u00A5',     # yen sign
            u'\u0192',     # latin small letter f with hook
            u'\u060B',     # afghani sign
            u'\u09F2',     # bengali rupee mark
            u'\u09F3',     # bengali rupee sign
            u'\u0AF1',     # gujarati rupee sign
            u'\u0BF9',     # tamil rupee sign
            u'\u0E3F',     # thai currency symbol baht
            u'\u17DB',     # khmer currency symbol riel
            u'\u2133',     # script capital m
            u'\u5143',     # cjk unified ideograph-5143
            u'\u5186',     # cjk unified ideograph-5186
            u'\u5706',     # cjk unified ideograph-5706
            u'\u5713',     # cjk unified ideograph-5713
            u'\uFDFC',     # rial sign
        ]

        # Add 20A0 (EURO-CURRENCY SIGN) to 20B5 (CEDI SIGN)
        #
        for ordChar in range(ord(u'\u20A0'), ord(u'\u20B5') + 1):
            _unicodeCurrencySymbols.append(unichr(ordChar))

    return _unicodeCurrencySymbols

def getRealActiveDescendant(obj):
    """Given an object that should be a child of an object that
    manages its descendants, return the child that is the real
    active descendant carrying useful information.

    Arguments:
    - obj: an object that should be a child of an object that
    manages its descendants.
    """

    # If obj is a table cell and all of it's children are table cells
    # (probably cell renderers), then return the first child which has
    # a non zero length text string. If no such object is found, just
    # fall through and use the default approach below. See bug #376791
    # for more details.
    #
    if obj.role == rolenames.ROLE_TABLE_CELL and obj.childCount:
        nonTableCellFound = False
        for i in range (0, obj.childCount):
            if obj.child(i).role != rolenames.ROLE_TABLE_CELL:
                nonTableCellFound = True
        if not nonTableCellFound:
            for i in range (0, obj.childCount):
                if obj.child(i).text:
                    text = obj.child(i).text.getText(0, -1)
                    if len(text) != 0:
                        return obj.child(i)

    # [[[TODO: WDW - this is an odd hacky thing I've somewhat drawn
    # from Gnopernicus.  The notion here is that we get an active
    # descendant changed event, but that object tends to have children
    # itself and we need to decide what to do.  Well...the idea here
    # is that the last child (Gnopernicus chooses child(1)), tends to
    # be the child with information.  The previous children tend to
    # be non-text or just there for spacing or something.  You will
    # see this in the various table demos of gtk-demo and you will
    # also see this in the Contact Source Selector in Evolution.
    #
    # Just note that this is most likely not a really good solution
    # for the general case.  That needs more thought.  But, this
    # comment is here to remind us this is being done in poor taste
    # and we need to eventually clean up our act.]]]
    #
    if obj and obj.childCount:
        return obj.child(obj.childCount - 1)
    else:
        return obj
