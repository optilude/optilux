import json

from five import grok

from zExceptions import Forbidden
from zope.component import getMultiAdapter

from plone.app.layout.globals.interfaces import IViewView
from plone.app.layout.viewlets.interfaces import IBelowContentBody

from optilux.cinemacontent.cinema import ICinema

class MyCinema(grok.Viewlet):
    """Viewlet for allowing users to set a "home" cinema
    """
    
    grok.context(ICinema)
    grok.name('optilux.cinemacontent.mycinema')
    grok.view(IViewView)
    grok.viewletmanager(IBelowContentBody)
    grok.require('zope2.View')
    
    def update(self):
        
        self.portal_state = getMultiAdapter(
                (self.context, self.request),
                name=u"plone_portal_state",
            )
        
        if not self.available():
            self.isHome = False
        else:
            member = self.portal_state.member()
    
            cinemaCode = self.context.cinemaCode
            homeCinemas = list(member.getProperty('homeCinemas', []))
        
            if 'optilux.cinemacontent.mycinema.Toggle' in self.request.form:
                authenticator = getMultiAdapter(
                        (self.context, self.request),
                        name=u"authenticator",
                    )
                if not authenticator.verify():
                    raise Forbidden()
                
                if cinemaCode in homeCinemas:
                    homeCinemas.remove(cinemaCode)
                else:
                    homeCinemas.append(cinemaCode)
                member.setProperties(homeCinemas=homeCinemas)
        
            self.isHome = (cinemaCode in homeCinemas)
        
    def available(self):
        return not self.portal_state.anonymous()
