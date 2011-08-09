from five import grok
from zope import schema
from plone.directives import form

from plone.app.textfield import RichText

from optilux.cinemacontent import CinemaMessageFactory as _

# View
from plone.memoize.instance import memoize
from optilux.cinemacontent.cinema import ICinema
from Products.CMFCore.utils import getToolByName

# Subscriber
from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.container.interfaces import INameChooser

from zope.lifecycleevent.interfaces import IObjectAddedEvent

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping

from optilux.cinemacontent.interfaces import PROMOTIONS_PORTLET_COLUMN
from optilux.cinemacontent.portlets import promotions

from Acquisition import aq_parent

class ICinemaFolder(form.Schema):
    """A folder that can contain cinemas
    """
    
    text = RichText(
            title=_(u"Body text"),
            description=_(u"Introductory text for this cinema folder"),
            required=False
        )

class View(grok.View):
    """Default view (called "@@view"") for a cinema folder.
    
    The associated template is found in cinemafolder_templates/view.pt.
    """
    
    grok.context(ICinemaFolder)
    grok.require('zope2.View')
    grok.name('view')
    
    def update(self):
        """Called before rendering the template for this view
        """
        
        self.haveCinemaFolders = len(self.cinemaFolders()) > 0
        self.haveCinemas       = len(self.cinemas()) > 0
    
    @memoize
    def cinemaFolders(self):
        """Get all child cinema folders in this cinema folder.
        
        We memoize this using @plone.memoize.instance.memoize so that even
        if it is called more than once in a request, the calculations are only
        performed once.
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        return [ dict(url=cinemaFolder.getURL(),
                      title=cinemaFolder.Title,
                      description=cinemaFolder.Description,)
                 for cinemaFolder in 
                    catalog({'object_provides': ICinemaFolder.__identifier__,
                             'path': dict(query='/'.join(self.context.getPhysicalPath()),
                                          depth=1),
                             'sort_on': 'sortable_title'})
               ]
    
    @memoize
    def cinemas(self):
        """Get all child cinemas in this cinema.
        """
        catalog = getToolByName(self.context, 'portal_catalog')

        return [ dict(url=cinema.getURL(),
                      title=cinema.Title,
                      address=cinema.Description,)
                 for cinema in 
                    catalog({'object_provides': ICinema.__identifier__,
                             'path': dict(query='/'.join(self.context.getPhysicalPath()),
                                      depth=1),
                             'sort_on': 'sortable_title'})
               ]

@grok.subscribe(ICinemaFolder, IObjectAddedEvent)
def addPromotionsPortlet(obj, event):
    """Event handler triggered when adding a cinema folder. This will add
    the promotions portlet automatically.
    """
    
    # Only do this if the parent is not a cinema folder, i.e. only do it on
    # top-level cinema folders. Of course, site managers can move things 
    # around once the site structure is created
    
    parent = aq_parent(obj)
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
