# Metacity script

import orca
from orca_i18n import _
import speech

# The status bar in metacity tells us what toplevel window will be
# activated when tab is released

def onNameChanged (e):

    # If it's not the statusbar's name changing, ignore it

    if e.source.role != "statusbar":
        return

    # We have to stop speech, as Metacity has a key grab and we're not
    # getting keys

    speech.stop ("default")

    name = e.source.name

    # Do we know about this window?  Traverse through our list of apps
    # and go through the toplevel windows in each to see if we know
    # about this one

    found = False
    for app in orca.apps:
        i = 0
        while i < app.childCount:
            win = app.child(i)
            if win is None:
                print "app error " + app.name
            elif win.name == name:
                found = True
            i = i + 1
    speech.say ("status", name)
    if found == False:
        speech.say ("status", _("inaccessible"))
        


