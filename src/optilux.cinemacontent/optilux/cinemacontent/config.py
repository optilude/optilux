PROJECTNAME = "optilux.cinemacontent"
PROMOTIONS_PORTLET_COLUMN = u"plone.rightcolumn"

# This maps portal types to their corresponding add permissions.
# These are referenced in the root product __init__.py, during
# Archetypes/CMF type initialisation.

# We prefix the permission names with our product name to group
# them sensibly. This is good practice, because it makes it
# easier to find permissions in the Security tab in the ZMI.

ADD_PERMISSIONS = {
    "CinemaFolder" : "Optilux: Add Cinema Folder",
    "Cinema"       : "Optilux: Add Cinema",
    "FilmFolder"   : "Optilux: Add Film Folder",
    "Film"         : "Optilux: Add Film",
    "Promotion"    : "Optilux: Add Promotion",
}
