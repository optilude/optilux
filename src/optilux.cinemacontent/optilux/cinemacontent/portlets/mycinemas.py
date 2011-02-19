"""Define a portlet used to show the current user's cinemas. This follows the 
patterns from plone.app.portlets.portlets. Note that we also need a 
portlet.xml in the GenericSetup extension profile to tell Plone about our 
new portlet.
"""

from zope.component import getMultiAdapter
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName

from optilux.cinemacontent.cinema import ICinema

from optilux.cinemacontent import CinemaMessageFactory as _

# This interface defines the configurable options (if any) for the portlet.
# It will be used to generate add and edit forms. In this case, we don't
# have an edit form, since there are no editable options.

class IMyCinemasPortlet(IPortletDataProvider):
    pass

# The assignment is a persistent object used to store the configuration of
# a particular instantiation of the portlet.

class Assignment(base.Assignment):
    implements(IMyCinemasPortlet)

    title = _(u"My cinema")

# The renderer is like a view (in fact, like a content provider/viewlet). The
# item self.data will typically be the assignment (although it is possible
# that the assignment chooses to return a different object - see 
# base.Assignment).

class Renderer(base.Renderer):

    # render() will be called to render the portlet
    
    render = ViewPageTemplateFile('mycinemas.pt')
       
    # The 'available' property is used to determine if the portlet should
    # be shown.
        
    @property
    def available(self):
        return len(self._cinemaCodes()) > 0

    
    def cinemas(self):
        context = aq_inner(self.context)
        cinemaCodes = self._cinemaCodes()
        
        if cinemaCodes:
            catalog = getToolByName(context, 'portal_catalog')
            for brain in catalog({'cinemaCode': cinemaCodes,
                                  'object_provides': ICinema.__identifier__}):
                yield dict(title=brain.Title,
                           address=brain.Description,
                           url=brain.getURL())
        
    # By using the @memoize decorator, the return value of the function will
    # be cached. Thus, calling it again does not result in another query.
    # See the plone.memoize package for more.
        
    @memoize
    def _cinemaCodes(self):
        context = aq_inner(self.context)
        portal_state = getMultiAdapter(
                (context, self.request),
                name="plone_portal_state",
            )
        if portal_state.anonymous():
            return []
        return portal_state.member().getProperty('homeCinemas', [])

# Define an add view - by using NullAddForm, we signal that we don't want
# a visible form, since there are no options to set anyway.

class AddForm(base.NullAddForm):
    
    # This method must be implemented to actually construct the object.

    def create(self):
        return Assignment()
