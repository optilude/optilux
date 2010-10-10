"""Define a browser view for the Cinema content type. In the FTI 
configured in profiles/default/types/*.xml, this is being set as the default
view of that content type.
"""

from zope.publisher.browser import BrowserView

from plone.memoize.instance import memoize
from optilux.cinemacontent.interfaces import IBannerProvider

class CinemaView(BrowserView):
    """Default view of a cinema
    """
    
    def haveHighlightedFilms(self):
        return len(self.highlightedFilms()) > 0
        
    @memoize
    def highlightedFilms(self):
        return [dict(url=film.absolute_url(),
                     title=film.Title(),
                     summary=film.Description(),
                     bannerTag=IBannerProvider(film).tag,)
                for film in self.context.getHighlightedFilms()]
