import unittest2 as unittest

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.app.testing import logout

from optilux.cinemacontent.testing import OPTILUX_CINEMACONTENT_INTEGRATION_TESTING

from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from Products.CMFCore.utils import getToolByName

from optilux.cinemacontent.portlets import mycinemas

class TestPortlet(unittest.TestCase):

    layer = OPTILUX_CINEMACONTENT_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Manager',))

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='optilux.MyCinemas')
        self.assertEquals(portlet.addview, 'optilux.MyCinemas')

    def testInterfaces(self):
        portlet = mycinemas.Assignment()
        self.assertTrue(IPortletAssignment.providedBy(portlet))
        self.assertTrue(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portal = self.layer['portal']
        
        portlet = getUtility(IPortletType, name='optilux.MyCinemas')
        mapping = portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview()

        self.assertEquals(len(mapping), 1)
        self.assertTrue(isinstance(mapping.values()[0], mycinemas.Assignment))

    def testRenderer(self):
        context = self.layer['portal']
        request = self.layer['request']
        
        view = context.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn', context=context)
        assignment = mycinemas.Assignment()

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.assertTrue(isinstance(renderer, mycinemas.Renderer))

class TestRenderer(unittest.TestCase):
    
    layer = OPTILUX_CINEMACONTENT_INTEGRATION_TESTING
    
    def setUp(self):
        portal = self.layer['portal']
        
        setRoles(portal, TEST_USER_ID, ('Manager',))
        
        portal.invokeFactory('optilux.CinemaFolder', 'cinemas')
        portal['cinemas'].invokeFactory('optilux.Cinema', 'c1', cinemaCode=u"C1")
        portal['cinemas'].invokeFactory('optilux.Cinema', 'c2', cinemaCode=u"C2")
        
        self.membership = getToolByName(portal, 'portal_membership')
        
        setRoles(portal, TEST_USER_ID, ('Member',))
    
    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        portal = self.layer['portal']
        
        context = context or portal
        request = request or self.layer['request']
        
        view = view or portal.restrictedTraverse('@@plone')
        
        manager = manager or getUtility(IPortletManager, name='plone.rightcolumn', context=portal)
        assignment = assignment or mycinemas.Assignment()

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
    
    def test_anonymous(self):
        portal = self.layer['portal']
        
        member = self.membership.getAuthenticatedMember()
        member.setProperties(homeCinemas=['C1'])
        
        logout()
        
        r = self.renderer(context=portal, assignment=mycinemas.Assignment())
        self.assertFalse(r.available)

    def test_no_cinemas(self):
        portal = self.layer['portal']
        
        member = self.membership.getAuthenticatedMember()
        member.setProperties(homeCinemas=[])
        r = self.renderer(context=portal, assignment=mycinemas.Assignment())
        self.assertFalse(r.available)
        self.assertEqual(len(list(r.cinemas())), 0)
        
    def test_single(self):
        portal = self.layer['portal']
        
        member = self.membership.getAuthenticatedMember()
        member.setProperties(homeCinemas=['C1'])
        r = self.renderer(context=portal, assignment=mycinemas.Assignment())
        self.assertTrue(r.available)
        cinemaUrls = [c['url'] for c in r.cinemas()]
        self.assertEqual(len(cinemaUrls), 1)
        self.assertEqual(cinemaUrls[0], portal.cinemas.c1.absolute_url())

    def test_multiple(self):
        portal = self.layer['portal']
        
        member = self.membership.getAuthenticatedMember()
        member.setProperties(homeCinemas=['C1', 'C2'])
        r = self.renderer(context=portal, assignment=mycinemas.Assignment())
        self.assertTrue(r.available)
        cinemaUrls = [c['url'] for c in r.cinemas()]
        self.assertEqual(len(cinemaUrls), 2)
        self.assertEqual(cinemaUrls[0], portal.cinemas.c1.absolute_url())
        self.assertEqual(cinemaUrls[1], portal.cinemas.c2.absolute_url())
