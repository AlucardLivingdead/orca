# Orca
#
# Copyright 2004 Sun Microsystems Inc.
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

import core
import a11y
import speech
import default

# Orca i18n

from orca_i18n import _


# The Mozilla version of say all reads text from multiple objects

sayAllObjects = []

# The current object being read

sayAllObjectIndex = 0

# The number of objects to speak

sayAllObjectCount = 0

# The object representing the root of the currently active page

activePage = None

# Advance to the next hypertext object in the say all list and speak it

def presentNextHypertext ():
    global sayAllObjectIndex
    global sayAllObjectIndex

    start = 0
    end = 0

    # Find the next object with text

    text = ""
    while text == "" and sayAllObjectIndex < sayAllObjectCount:
        obj = sayAllObjects[sayAllObjectIndex]
        sayAllObjectIndex = sayAllObjectIndex + 1
        txt = a11y.getText (obj)
        if txt is None:

            # If it's an image, read the image's name using the image voice

            text = obj.name
            if obj.role == "image":

                # If we're getting the file name of the image, don't read it

                if text.find (".gif") >= 0 or \
                       text.find (".gif") >= 0 or \
                       text.find (".jpg") >= 0:
                    text = ""
                    sayAllObjectIndex = sayAllObjectIndex + 1
                    continue
                else:
                    speech.say ("image", text)
            elif text is not "":
                speech.say ("default", text)
            if text == "":
                sayAllObjectIndex = sayAllObjectIndex + 1
                continue
            else:

                # Stop looking for more objects, we're speaking one now

                break

        # Get the entire contents of this hypertext object

        text = txt.getText (0, -1)

        # Get the hypertext interface to this object

        ht = a11y.getHypertext (obj)
        if ht is None:
            nLinks = 0
        else:
            nLinks = ht.getNLinks ()
        if nLinks == 0:
            speech.say ("default", text)

        # Speak this hypertext object in chunks

        else:

            # Split up the links

            position = 0
            i = 0
            while i < nLinks:
                hl = ht.getLink (i)

                # We don't get proper start and end offsets, so hack
                # hack hack

                # Get the text of the hyperlink

                anchor = hl.getObject (0)
                name = anchor.name
                start = text[position:].find (name)
                if start == -1:
                    break
                start = start+position
                end = start+len(name)
    
                # If there is text between where we are now and the beginning of the link, read it first

                if start != position:
                    speech.say ("default", text[position:start])

                # Speak the text of the hyperlink using the hyperlink voice

                speech.say ("hyperlink", text[start:end])
                position = end
                i = i + 1

            # We're done speaking the hyperlinks - if there's text
            # left, spaek it

            if end < len(text):
                speech.say ("default", text[end:])

    # If we have no more objects to speak, end say all mode

    if sayAllObjectIndex == sayAllObjectCount:
        return False
    else:
        return True
    

# This function is called by say all mode when another chunk of text
# is needed

def getChunk ():
    global sayAllObjects
    global sayAllObjectIndex
    global sayAllObjectCount

    return presentNextHypertext ()

# This function is called when say all mode is finished - it currently
# does nothing

def sayAllDone (position):
    pass

# this function starts say all for Mozilla

def sayAll ():
    global activePage
    global sayAllObjects
    global sayAllObjectIndex
    global sayAllObjectCount

    # If there is no active page, we can't do say all

    if activePage is None:
        speech.say ("default", _("No page to read."))
        return

    # Get all the objects on the page

    try:
        sayAllObjects = a11y.getObjects (activePage)
    except:
        speech.say ("default", _("Reading web page failed."))
        return

    # Set up say all mode

    sayAllObjectCount = len(sayAllObjects)
    sayAllObjectIndex = 0

    # Speak the name of the page, then start say all mode.  When the
    # name of the page has finished speaking, say all mode will be
    # active and the first chunk of the page will be read

    speech.say ("default", activePage.name)
    speech.startSayAll ("default", getChunk, sayAllDone)

# This function is called whenever an object within Mozilla receives
# focus

def onFocus (event):
    global activePage

    
    if event.source.role != "panel":
        return default.onFocus (event)
    
    # If it's not a panel, do the default

    default.onFocus (event)

    # If the panel has no name, don't touch it

    if len(event.source.name) == 0:
        return

    activePage = event.source


# This function is called when a hyperlink is selected - This happens
# when a link is navigated to using tab/shift-tab

def onLinkSelected (event):
    txt = a11y.getText (event.source)
    if txt is None:
        speech.say ("hyperlink", "link")
    else:
        text = txt.getText (0, -1)
        speech.say ("hyperlink", text)
