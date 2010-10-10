"""Define a browser view for the CinemaFolder content type. In the FTI 
configured in profiles/default/types/*.xml, this is being set as the default
view of that content type.
"""

from zope.publisher.browser import BrowserView

from Products.CMFCore.utils import getToolByName

from optilux.cinemacontent.interfaces import ICinemaFolder
from optilux.cinemacontent.interfaces import ICinema

from plone.memoize.instance import memoize 

class CinemaFolderView(BrowserView):
    """Default view of a cinema folder
    """
    
    # Methods called from the associated template
    
    def haveCinemaFolders(self):
        return len(self.cinemaFolders()) > 0
    
    # The memoize decorator means that the function will be executed only
    # once (for a given set of arguments, but in this case there are no
    # arguments). On subsequent calls, the return value is looked up from a
    # cache, meaning we can call this function several times without a 
    # performance hit.
    
    @memoize
    def cinemaFolders(self):
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
    
    def haveCinemas(self):
        return len(self.cinemas()) > 0
    
    @memoize
    def cinemas(self):
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
