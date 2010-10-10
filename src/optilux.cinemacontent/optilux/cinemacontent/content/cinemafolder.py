"""Definition of the CinemaFolder content type and associated schemata and
other logic.

This file contains a number of comments explaining the various lines of
code. Other files in this sub-package contain analogous code, but will 
not be commented as heavily.

Please see README.txt for more information on how the content types in
this package are used.
"""

from zope.interface import implements
from zope.component import adapter, getMultiAdapter, getUtility

from zope.app.container.interfaces import INameChooser

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping

from Acquisition import aq_inner, aq_parent

from Products.Archetypes import atapi
from Products.Archetypes.interfaces import IObjectInitializedEvent

from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from optilux.cinemacontent.interfaces import ICinemaFolder

from optilux.cinemacontent.config import PROJECTNAME
from optilux.cinemacontent.config import PROMOTIONS_PORTLET_COLUMN

from optilux.cinemacontent import CinemaMessageFactory as _
from optilux.cinemacontent.portlets import promotions

# This is the Archetypes schema, defining fields and widgets. We extend
# the one from ATContentType's ATFolder with our additional fields.
CinemaFolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((
    atapi.TextField('text',
        required=False,
        searchable=True,
        validators=('isTidyHtmlWithCleanup',),
        default_output_type='text/x-html-safe',
        widget=atapi.RichWidget(label=_(u"Descriptive text"),
                                description=_(u""),
                                rows=25,
                                allow_file_upload=False),
        ),
    ))

# Calling this re-orders a few fields to comply with Plone conventions.
finalizeATCTSchema(CinemaFolderSchema, folderish=True, moveDiscussion=False)

class CinemaFolder(folder.ATFolder):
    """Contains multiple cinemas
    
    Can also contain promotions, which will then apply to all cinemas in
    this folder, and other cinema folders to allow cinemas to be grouped
    into sub-groups.
    """
    implements(ICinemaFolder)
    
    # Associate the schema with our content type
    schema = CinemaFolderSchema
    
# This line tells Archetypes about the content type
atapi.registerType(CinemaFolder, PROJECTNAME)

# We will register this function as an event handler, adding a "promotions"
# portlet whenever a cinema folder is first created. 
@adapter(ICinemaFolder, IObjectInitializedEvent)
def addPromotionsPortlet(obj, event):
    
    # Only do this if the parent is not a cinema folder, i.e. only do it on
    # top-level cinema folders. Of course, site managers can move things 
    # around once the site structure is created
    
    parent = aq_parent(aq_inner(obj))
    if ICinemaFolder.providedBy(parent):
        return
    
    # A portlet manager is akin to a column
    column = getUtility(IPortletManager, name=PROMOTIONS_PORTLET_COLUMN)
    
    # We multi-adapt the object and the column to an assignment mapping,
    # which acts like a dict where we can put portlet assignments
    manager = getMultiAdapter((obj, column,), IPortletAssignmentMapping)
    
    # We then create the assignment and put it in the assignment manager,
    # using the default name-chooser to pick a suitable name for us.
    assignment = promotions.Assignment()
    chooser = INameChooser(manager)
    manager[chooser.chooseName(None, assignment)] = assignment
