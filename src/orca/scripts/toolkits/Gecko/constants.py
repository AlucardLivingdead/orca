import pyatspi

# If True, it tells us to take over caret navigation.  This is something
# that can be set in user-settings.py:
#
# import orca.Gecko
# orca.Gecko.controlCaretNavigation = True
#
controlCaretNavigation = True

# If True, it tells us to position the caret at the beginning of a
# line when arrowing up and down.  If False, we'll try to position the
# caret directly above or below the current caret position.
#
arrowToLineBeginning = True

# If True, it tells Orca to automatically perform a SayAll operation
# when a page is first loaded.
#
sayAllOnLoad = True

# Whether or not to use the structrual navigation commands (e.g. H
# for heading, T for table, and so on).
#
structuralNavigationEnabled = True

# Whether or not to speak the cell's coordinates when navigating
# from cell to cell in HTML tables.
#
speakCellCoordinates = True

# Whether or not to speak the number of cells spanned by a cell
# that occupies more than one row or column of an HTML table.
#
speakCellSpan = True

# Whether or not to announce the header that applies to the current
# when navigating from cell to cell in HTML tables.
#
speakCellHeaders = True

# Whether blank cells should be skipped when navigating in an HTML
# table using table navigation commands
#
skipBlankCells = False

# Whether or not Orca should speak the changing location within the
# document frame *during* a find (i.e. while focus is still in the
# Find toolbar).
#
speakResultsDuringFind = True

# The minimum number of characters that must be matched during
# a find before Orca speaks the changed location, assuming that
# speakResultsDuringFind is True.
#
minimumFindLength = 4

# Whether or not to continue speaking the same line if the match
# has not changed with additional keystrokes.  This setting comes
# in handy for fast typists who might inadvertantly interrupt the
# speaking of the line that matches by continuing to type in the
# Find entry.  This is the equivalent of what we do in autocompletes
# throughout GNOME.  For power-users of the Find toolbar, however,
# that may be too verbose so it's configurable.
#
onlySpeakChangedLinesDuringFind = False

# The minimum number of characters of text that an accessible object must 
# contain to be considered a match in go to next/prev large object
largeObjectTextLength = 75

# Roles that represent a logical chunk of information in a document
#
OBJECT_ROLES = [pyatspi.ROLE_HEADING,
                pyatspi.ROLE_PARAGRAPH,
                pyatspi.ROLE_TABLE,
                pyatspi.ROLE_TABLE_CELL,
                pyatspi.ROLE_TEXT,
                pyatspi.ROLE_SECTION,
                pyatspi.ROLE_DOCUMENT_FRAME,
                pyatspi.ROLE_AUTOCOMPLETE]

ARIA_LANDMARKS = ["banner", "contentinfo", "definition", "main", "navigation",
                  "note", "search", "secondary", "seealso"]
