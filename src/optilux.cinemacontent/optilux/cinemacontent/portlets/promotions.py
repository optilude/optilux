"""Define a portlet used to show promotions. This follows the patterns from
plone.app.portlets.portlets. Note that we also need a portlet.xml in the
GenericSetup extension profile to tell Plone about our new portlet.
"""

import random

from zope import schema
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider

from DateTime import DateTime
from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from optilux.cinemacontent.interfaces import IPromotion
from optilux.cinemacontent.interfaces import IBannerProvider
from optilux.cinemacontent import CinemaMessageFactory as _

# This interface defines the configurable options (if any) for the portlet.
# It will be used to generate add and edit forms.

class IPromotionsPortlet(IPortletDataProvider):

    count = schema.Int(
            title=_(u"Number of promotions to display"),
            description=_(u"Maximum number of promotions to show"),
            required=True,
            default=5,
        )
                       
    randomize = schema.Bool(
            title=_(u"Randomize promotions"),
            description=_(u"If enabled, promotions to show will"
                            "be picked randomly. If disabled, newer "
                            "promotions will be preferred."),
            default=False,
        )
                            
    sitewide = schema.Bool(
            title=_(u"Sitewide promotions"),
            description=_(u"If enabled, promotions from across the "
                           "site will be found. If disabled, only "
                           "promotions in this folder and its "
                           "subfolders are eligible."),
            default=False,
        )

# The assignment is a persistent object used to store the configuration of
# a particular instantiation of the portlet.

class Assignment(base.Assignment):
    implements(IPromotionsPortlet)

    def __init__(self, count=5, randomize=False, sitewide=False):
        self.count = count
        self.randomize = randomize
        self.sitewide = sitewide

    title = _(u"Promotions")

# The renderer is like a view (in fact, like a content provider/viewlet). The
# item self.data will typically be the assignment (although it is possible
# that the assignment chooses to return a different object - see 
# base.Assignment).

class Renderer(base.Renderer):

    # render() will be called to render the portlet
    
    render = ViewPageTemplateFile('promotions.pt')
       
    # The 'available' property is used to determine if the portlet should
    # be shown.
        
    @property
    def available(self):
        return len(self._data()) > 0

    # To make the view template as simple as possible, we return dicts with
    # only the necessary information.

    def promotions(self):
        for brain in self._data():
            promotion = brain.getObject()
            bannerProvider = IBannerProvider(promotion)
            yield dict(title=promotion.Title(),
                       summary=promotion.Description(),
                       url=brain.getURL(),
                       image_tag=bannerProvider.tag)

    # By using the @memoize decorator, the return value of the function will
    # be cached. Thus, calling it again does not result in another query.
    # See the plone.memoize package for more.
        
    @memoize
    def _data(self):
        context = aq_inner(self.context)
        limit = self.data.count
        
        query = dict(object_provides = IPromotion.__identifier__)
        
        if not self.data.sitewide:
            query['path'] = '/'.join(context.getPhysicalPath())
        if not self.data.randomize:
            query['sort_on'] = 'modified'
            query['sort_order'] = 'reverse'
            query['sort_limit'] = limit
        
        # Ensure that we only get active objects, even if the user would
        # normally have the rights to view inactive objects (as an
        # administrator would)
        query['effectiveRange'] = DateTime()
        
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(query)
        
        promotions = []
        if self.data.randomize:
            promotions = list(results)
            promotions.sort(lambda x,y: cmp(random.randint(0,200),100))
            promotions = promotions[:limit]
        else:
            promotions = results[:limit]
        
        return promotions

# Define the add forms and edit forms, based on zope.formlib. These use
# the interface to determine which fields to render.

class AddForm(base.AddForm):
    form_fields = form.Fields(IPromotionsPortlet)
    label = _(u"Add Promotions portlet")
    description = _(u"This portlet displays cinema promotions.")

    # This method must be implemented to actually construct the object.
    # The 'data' parameter is a dictionary, containing the values entered
    # by the user.

    def create(self, data):
        assignment = Assignment()
        form.applyChanges(assignment, self.form_fields, data)
        return assignment

class EditForm(base.EditForm):
    form_fields = form.Fields(IPromotionsPortlet)
    label = _(u"Edit Promotions portlet")
    description = _(u"This portlet displays cinema promotions.")
