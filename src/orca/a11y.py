# Orca
#
# Copyright 2004-2005 Sun Microsystems Inc.
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
#
#

"""Manages the Accessible class.

Also provides a number of convenience functions for working with
Accessible objects.
"""


import os
import sys
import core     # The Orca core module - written in C


# The Accessible that currently has keyboard focus
#
focusedObject = None

# The Accessible application whose window currently has focus
#
focusedApp = None


class Accessible:
    """Wraps at-spi Accessible objects and caches properties such as
    name, description, and parent.

    It also adds some properties to the at-spi Accessible including
    the Application to which the object belongs.

    For efficiency purposes, this class also maintains a cache of all
    Accessible objects obtained so far, and will return an element
    from that cache instead of creating a duplicate object.
    """


    # The cache of the currently active accessible objects.  The key is
    # the at-spi Accessible, and the value is the Python Accessible.
    #
    cache = {} 

    def __init__ (self, acc):
        """Obtains, and creates if necessary, a Python Accessible from
        an at-spi Accessibility_Accessible.  Applications should not
        call this method, but should instead call makeAccessible.
        
        Arguments:
        - acc: the at-spi Accessibility_Accessible
        
        Returns the associated Python Accessible.
        """
        
        try:
            existing = Accessible.cache[acc]
            return
        except:
            pass

        # The acc reference might be an Accessibility_Accessible or an
        # Accessibility_Application, so try both
        #
        try:
            self.acc = acc._narrow (core.Accessibility.Accessible)
        except:
            self.acc = acc._narrow (core.Accessibility.Application)

        # Save a reference to the at-spi object, and also save this
        # new object away in the cache.
        #
        self.acc.ref ()
        Accessible.cache[acc] = self


    def __del__ (self):
        """Unrefs the at-spi Accessible associated with this object.
        [[[TODO: WDW - shouldn't this also remove the element from the
        cache?]]]
        """
        
        self.acc.unref ()


    def __get_name (self):
        """Returns the object's accessible name as a string.
        """

        self.name = self.acc.name
        return self.name


    def __get_description (self):
        """Returns the object's accessible description as a string.
        """

        self.description = self.acc.description
        return self.description


    def __get_parent (self):
        """Returns the object's parent as a Python Accessible.  If
        this object has no parent, None will be returned.
        """

        # [[[TODO: WDW - we might try looking to see if the
        # self.parent attribute has already been set.]]]
        #
        obj = self.acc.parent
        if obj is None:
            self.parent = None
            return self.parent

        self.parent = makeAccessible(obj);
        return self.parent;


    def __get_child_count (self):
        """Returns the number of children for this object.
        """

        self.childCount = self.acc.childCount
        return self.childCount


    def __get_index (self):
        """Returns the index of this object in its parent's child list.
        """

        self.index = self.acc.getIndexInParent ()
        return self.index


    def __get_role (self):
        """Returns the Accessible role name of this object as a string.
        This string is not localized and can be used for comparison.
        """
        
        self.role = self.acc.getRoleName ()
        return self.role


    def __get_state (self):
        """Returns the Accessible StateSeq of this object, which is a
        sequence of Accessible StateTypes.
        """

        set = self.acc.getState ()
        set = set._narrow (core.Accessibility.StateSet)
        self.state = set.getStates ()
        return self.state


    def __get_relations (self):
        """Returns the Accessible RelationSet of this object as a list.
        """

        relations = self.acc.getRelationSet ()
        self.relations = []
        for relation in relations:
            self.relations.append (relation._narrow (
                core.Accessibility.Relation))
                                   
        return self.relations


    def __get_app (self):
        """Returns the at-spi Accessibility_Application associated with this
        object.  Returns None if the application cannot be found (usually
        the indication of an at-spi bug).
        """
        
        # Traverse up the tree until we find the app.
        # [[[TODO: WDW - this code seems like it might break if this
        # object is an application to begin with.]]]
        #
        obj = self
        while (obj.parent != None) and (obj != obj.parent):
            obj = obj.parent
            
        if (obj == obj.parent) or (obj.role != "application"):
            self.app = None
        else:
            self.app = obj
            
        return self.app


    def __getattr__ (self, attr):
        """Created virtual attributes for the Accessible object to make
        the syntax a bit nicer (e.g., acc.name rather than acc.name()).

        Arguments:
        - attr: a string indicating the attribute name to retrieve

        Returns the value of the given attribute.
        """
        
        if attr == "name":
            return self.__get_name ()
        elif attr == "description":
            return self.__get_description ()
        elif attr == "parent":
            return self.__get_parent ()
        elif attr == "childCount":
            return self.__get_child_count ()
        elif attr == "index":
            return self.__get_index ()
        elif attr == "role":
            return self.__get_role ()
        elif attr == "state":
            return self.__get_state ()
        elif attr == "relations":
            return self.__get_relations ()
        elif attr == "app":
            return self.__get_app ()

        # If we can't find the attribute, defer to the base object
        #
        return super (object, self).__getattr__ (name)
    

    def child (self, index):
        """Returns the specified child of this object.

        Arguments:
        - index: an integer specifying which child to obtain

        Returns the child at the given index.  [[[TODO: WDW - what to do
        when an index out of bounds occurs?]]]
        """
        
        acc = self.acc.getChildAtIndex (index)
        newChild = makeAccessible(acc)

        # Save away details we now know about this child
        #
        newChild.index = index
        newChild.parent = self
        try:
            newChild.app = self.app
        except:
            pass
        
        return newChild


def makeAccessible (acc):
    """Make an Accessible.  This is used instead of a simple calls to
    Accessible's constructor because the object may already be in the
    cache.

    Arguments:
    - acc: the at-spi Accessibility_Accessible

    Returns a Python Accessible.
    """

    if acc is None:
        return None
    
    try:
        obj = Accessible.cache[acc]
    except:
        obj = Accessible (acc)
    return obj



########################################################################
#                                                                      #
# Methods for handling at-spi events.                                  #
#                                                                      #
########################################################################

# This dictionary maps at-spi event names to Python function names
# which are to be used in scripts.  For example, it maps "focus:"
# events to call a script function called onFocus and
# "window:activate" to onWindowActivated.  [[[TODO: WDW - might
# consider moving this to the script module at some point.]]]
#
dispatcher = {}
dispatcher["onWindowActivated"] = "window:activate"
dispatcher["onWindowDestroyed"] = "window:destroy"
dispatcher["onFocus"] = "focus:"
dispatcher["onStateChanged"] = "object:state-changed:"
dispatcher["onSelectionChanged"] = "object:selection-changed"
dispatcher["onCaretMoved"] = "object:text-caret-moved"
dispatcher["onTextInserted"] = "object:text-changed:insert"
dispatcher["onTextDeleted"] = "object:text-changed:delete"
dispatcher["onLinkSelected"] = "object:link-selected"
dispatcher["onNameChanged"] = "object:property-change:accessible-name"


def onWindowActivated (e):
    """Core module event listener called when a window is activated.
    Saves away the associated application in the focusedApp attribute.

    Arguments:
    - e: the Python Event object
    """
    
    global focusedApp

    source = e.source._narrow (core.Accessibility.Accessible)
    focusedApp = makeAccessible (source.parent)


def onFocus (e):
    """Core module event listener called when focus changes.  Saves
    away the associated application in the focusedApp attribute and the
    associated object in the focusedObject attribute.

    Arguments:
    - e: the Python Event object
    """
    
    global focusedObject
    global focusedApp

    focusedObject = makeAccessible (e.source)

    # We need this hack fo the time being due to a bug in Nautilus,
    # which makes it impossible to traverse to the application from
    # some objects within Nautilus.  [[[TODO: WDW - verify and
    # possibly remove this hack at some point.]]]
    #
    focusedObject.app = focusedApp


def onNameChanged (e):
    """Core module event listener called when an object's name
    changes.  Updates the cache accordingly.

    Arguments:
    - e: the Python Event object
    """
    
    try:
        obj = Accessible.cache[e.source]
        obj.name = e.any_data
    except:
        pass


def onDescriptionChanged (e):
    """Core module event listener called when an object's description
    changes.  Updates the cache accordingly.

    Arguments:
    - e: the Python Event object
    """

    try:
        obj = Accessible.cache[e.source]
        obj.description = e.any_data
    except:
        pass


def onParentChanged (e):
    """Core module event listener called when an object's parent
    changes.  Updates the cache accordingly.

    Arguments:
    - e: the Python Event object
    """

    try:
        # [[[TODO: WDW - might want to see what this del is doing - we
        # might need to del the parent and app from the cache so we
        # don't run into a memory leak.]]]
        #
        obj = Accessible.cache[e.source]
        del obj.parent
        del obj.app
    except:
        pass


def onStateChanged (e):
    """Core module event listener called when an object's state
    changes.  Updates the cache accordingly.

    Arguments:
    - e: the Python Event object
    """

    try:
        obj = Accessible.cache[e.source]
        del obj.state
    except:
        pass

def onChildrenChanged (e):
    """Core module event listener called when an object's child count
    changes.  Updates the cache accordingly.

    Arguments:
    - e: the Python Event object
    """
    try:
        obj = Accessible.cache[e.source]
        del obj.childCount
    except:
        pass


def onDefunct (e):
    """Core module event listener called when an object becomes
    defunct.  Removes the object from the cache accordingly.

    Arguments:
    - e: the Python Event object
    """
    try:
        del Accessible.cache[e.source]
    except:
        pass



########################################################################
#                                                                      #
# Utility methods.                                                     #
#                                                                      #
########################################################################

initialized = False

def init ():
    """Initialize the a11y module.  This also intializes the core
    module and registers the various core module event listeners in
    this module with the core module.

    Returns True if the module has been successfully initialized.
    """
    
    global initialized
    if initialized:
        return True

    # Register our various listeners.
    #
    core.init ()
    core.registerEventListener (
        onWindowActivated, "window:activate")
    core.registerEventListener (
        onFocus, "focus:")
    core.registerEventListener (
        onDefunct, "object:state-changed:defunct")
    core.registerEventListener (
        onNameChanged, "object:property-change:accessible-name")
    core.registerEventListener (
        onDescriptionChanged, "object:property-change:accessible-description")
    core.registerEventListener (
        onParentChanged, "object:property-change:accessible-parent")
    core.registerEventListener (
        onStateChanged, "object:state-changed:")
    core.registerEventListener (
        onChildrenChanged, "object:children-changed:")

    initialized = True
    return True


def shutdown ():
    """Shuts down this module as well as the core module.
    [[[TODO: WDW - should this free the cache as well?]]]
    """
    
    global initialized

    if not initialized:
        return False

    core.shutdown ()

    initialized = False
    return True


def getObjects (root):
    """Returns a list of all objects under the given root.  Objects
    are returned in no particular order - this function does a simple
    tree traversal, ignoring the children of objects which report the
    MANAGES_DESCENDANTS state is active.

    Arguments:
    - root: the Accessible object to traverse

    Returns: a list of all objects under the specified object
    """


    # All the objects we've found
    #
    objvisitted = {}

    # The list of object we'll return
    #
    objlist = []

    # Start at the first child of the given object
    #
    if root.childCount <= 0:
        return objlist

    tmp = root.child (0)
    while tmp != root:

        # Traverse to the bottom of the tre
        #
        while tmp.childCount > 0:

            # If tmp is None, we hit the bottom of the tree
            #
            if tmp is None:
                break
            tmp = tmp.child (0)

            # Avoid traversing into objects which manage their
            # descendants (tables, etc)
            #
            state = tmp.state
            if state.count (core.Accessibility.STATE_MANAGES_DESCENDANTS):
                break

        # Move up the tree until the current object has siblings
        #
        i = tmp.index
        while tmp != root and i >= tmp.parent.childCount-1:
            try:
                t = objvisitted[tmp]
            except:
                objlist.append (tmp)
                objvisitted[tmp] = True
            tmp = tmp.parent
            i = tmp.index

        # If we're at the top, we're done
        #
        if tmp == root:
            break
        try:
            t = objvisitted[tmp]
        except:
            objlist.append (tmp)
            objvisitted[tmp] = True

        # Move to the next sibling
        #
        tmp = tmp.parent.child (i+1)
        
    return objlist


def findByRole (root, role):
    """Returns a list of all objects of a specific role beneath the
    given root.  [[[TODO: MM - This is very inefficient - this should
    do it's own traversal and not add objects to the list that aren't
    of the specified role.  Instead it uses the traversal from
    getObjects and then deletes objects from the list that aren't of
    the specified role.]]]

    Arguments:
    - root the Accessible object to traverse
    - role the string describing the Accessible role of the object
    
    Returns a list of descendants of the root that are of the given role.
    """
    
    objlist = []
    allobjs = getObjects (root)
    for o in allobjs:
        if o.role == role:
            objlist.append (o)
    return objlist


def findByName (root, name):
    """Returns a list of all objects beneath the specified object with
    the specified name.  [[[TODO: MM - This is very inefficient - this
    should do it's own traversal and not add objects to the list that
    don't have the specified name.  Instead it uses the traversal from
    getObjects and then deletes objects from the list that don't have
    the specified name.]]]

    Arguments:
    - root the Accessible object to traverse
    - name the string containing the Accessible name of the object
    
    Returns a list of descendants of the root that are of the given role.
    """

    objlist = []
    list = getObjects (root)

    # Create a new list containing only those objects with the
    # specified name
    #
    for o in list:
        if o.name == name:
            objlist.append (o)
    return objlist


def getLabel (obj):
    """Returns an object's label as a string.  The label is determined
    using the following logic:

        1. If the object has a LABELLED_BY relation, return the text of
           the targets of this relation

        2. Else if the object has no LABELLED_BY relation, return the name

        3. Else if the object has no name, return the description

        4. Else return an empty string
       
    Arguments:
    - obj: the Accessible object

    Returns the object's label as a string.
    """

    label = ""

    # Does the object have a relation set?
    #
    relations = obj.relations
    for relation in relations:
        if relation.getRelationType () \
               == core.Accessibility.RELATION_LABELLED_BY:
            target = makeAccessible(relation.getTarget (0))
            label = target.name
            break

    # If the object doesn't have a relation, but has a name, return
    # that
    #
    if (len (label) == 0) and (obj.name is not None) and (len (obj.name) > 0):
        label = obj.name

    # If the object has no name, but has a description, return that
    #
    elif (len (label) == 0) and (obj.description is not None) \
             and (len (obj.description) > 0):
        label = obj.description

    return label


def getGroup (obj):
    """Returns an object's group.  [[[TODO: MM - This is busted for
    now.  It currently just returns the object's parent.]]]

    Arguments:
    - obj: the Accessible object

    Returns the objects group.
    """
    
    return obj.parent


def getAccessible (obj):
    """Returns an object that implements the Accessibility_Accessible
    interface for this object, or None if this object doesn't implement
    the Accessibility_Accessible interface.

    Arguments:
    - obj: [[[TODO: WDW - need to determine object type.]]]

    Returns an object that implements the Accessibility_Accessible
    interface for this object or None if this object doesn't implement
    the Accessibility_Accessible interface.
    """
    
    acc = obj.queryInterface ("IDL:Accessibility/Accessible:1.0")
    if acc is not None:
        acc = acc._narrow (core.Accessibility.Accessible)
    return acc

def getAction (obj):
    """Returns an object that implements the Accessibility_Action
    interface for this object, or None if this object doesn't implement
    the Accessibility_Action interface.

    Arguments:
    - obj: [[[TODO: WDW - need to determine object type.]]]

    Returns an object that implements the Accessibility_Action
    interface for this object or None if this object doesn't implement
    the Accessibility_Action interface.
    """

    bobj = obj.acc._narrow (core.Accessibility.Accessible)
    action = bobj.queryInterface ("IDL:Accessibility/Action:1.0")
    if action is not None:
        action = action._narrow (core.Accessibility.Action)
    return action

def getComponent (obj):
    """Returns an object that implements the Accessibility_Component
    interface for this object, or None if this object doesn't implement
    the Accessibility_Component interface.

    Arguments:
    - obj: [[[TODO: WDW - need to determine object type.]]]

    Returns an object that implements the Accessibility_Component
    interface for this object or None if this object doesn't implement
    the Accessibility_Component interface.
    """

    bobj = obj.acc._narrow (core.Accessibility.Accessible)
    component = bobj.queryInterface ("IDL:Accessibility/Component:1.0")
    if component is not None:
        component = component._narrow (core.Accessibility.Component)
    return component

def getHypertext (obj):
    """Returns an object that implements the Accessibility_Hypertext
    interface for this object, or None if this object doesn't implement
    the Accessibility_Hypertext interface.

    Arguments:
    - obj: [[[TODO: WDW - need to determine object type.]]]

    Returns an object that implements the Accessibility_Hypertext
    interface for this object or None if this object doesn't implement
    the Accessibility_Hypertext interface.
    """

    bobj = obj.acc._narrow (core.Accessibility.Accessible)
    hypertext = bobj.queryInterface ("IDL:Accessibility/Hypertext:1.0")
    if hypertext is not None:
        hypertext = hypertext._narrow (core.Accessibility.Hypertext)
    return hypertext

def getSelection (obj):
    """Returns an object that implements the Accessibility_Selection
    interface for this object, or None if this object doesn't implement
    the Accessibility_Selection interface.

    Arguments:
    - obj: [[[TODO: WDW - need to determine object type.]]]

    Returns an object that implements the Accessibility_Selection
    interface for this object or None if this object doesn't implement
    the Accessibility_Selection interface.
    """

    bobj = obj.acc._narrow (core.Accessibility.Accessible)
    sel = bobj.queryInterface ("IDL:Accessibility/Selection:1.0")
    if sel is not None:
        sel = sel._narrow (core.Accessibility.Selection)
    return sel

def getTable (obj):
    """Returns an object that implements the Accessibility_Table
    interface for this object, or None if this object doesn't implement
    the Accessibility_Table interface.

    Arguments:
    - obj: [[[TODO: WDW - need to determine object type.]]]

    Returns an object that implements the Accessibility_Table
    interface for this object or None if this object doesn't implement
    the Accessibility_Table interface.
    """

    bobj = obj.acc._narrow (core.Accessibility.Accessible)
    table = bobj.queryInterface ("IDL:Accessibility/Table:1.0")
    if table is not None:
        table = table._narrow (core.Accessibility.Table)
    return table

def getText (obj):
    """Returns an object that implements the Accessibility_Text
    interface for this object, or None if this object doesn't implement
    the Accessibility_Text interface.

    Arguments:
    - obj: [[[TODO: WDW - need to determine object type.]]]

    Returns an object that implements the Accessibility_Text
    interface for this object or None if this object doesn't implement
    the Accessibility_Text interface.
    """

    bobj = obj.acc._narrow (core.Accessibility.Accessible)
    text = bobj.queryInterface ("IDL:Accessibility/Text:1.0")
    if text is not None:
        text = text._narrow (core.Accessibility.Text)
    return text

def getValue (obj):
    """Returns an object that implements the Accessibility_Value
    interface for this object, or None if this object doesn't implement
    the Accessibility_Value interface.

    Arguments:
    - obj: [[[TODO: WDW - need to determine object type.]]]

    Returns an object that implements the Accessibility_Value
    interface for this object or None if this object doesn't implement
    the Accessibility_Value interface.
    """

    bobj = obj.acc._narrow (core.Accessibility.Accessible)
    value = bobj.queryInterface ("IDL:Accessibility/Value:1.0")
    if value is not None:
        value = value._narrow (core.Accessibility.Value)
    return value
