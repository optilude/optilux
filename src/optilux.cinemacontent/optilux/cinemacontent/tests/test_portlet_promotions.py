import unittest2 as unittest

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from optilux.cinemacontent.testing import OPTILUX_CINEMACONTENT_INTEGRATION_TESTING

from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.storage import PortletAssignmentMapping

from optilux.cinemacontent.portlets import promotions

class TestPortlet(unittest.TestCase):

    layer = OPTILUX_CINEMACONTENT_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Manager',))

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='optilux.Promotions')
        self.assertEqual(portlet.addview, 'optilux.Promotions')

    def testInterfaces(self):
        portlet = promotions.Assignment()
        self.assertTrue(IPortletAssignment.providedBy(portlet))
        self.assertTrue(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portal = self.layer['portal']
        
        portlet = getUtility(IPortletType, name='optilux.Promotions')
        mapping = portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={})

        self.assertEqual(len(mapping), 1)
        self.assertTrue(isinstance(mapping.values()[0], promotions.Assignment))

    def testInvokeEditView(self):
        
        request = self.layer['request']
        
        mapping = PortletAssignmentMapping()

        mapping['foo'] = promotions.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.assertTrue(isinstance(editview, promotions.EditForm))

    def testRenderer(self):
        
        context = self.layer['portal']
        request = self.layer['request']
        
        view = context.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn', context=context)
        assignment = promotions.Assignment()

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.assertTrue(isinstance(renderer, promotions.Renderer))

class TestRenderer(unittest.TestCase):
    
    layer = OPTILUX_CINEMACONTENT_INTEGRATION_TESTING
    
    def setUp(self):
        portal = self.layer['portal']
        
        setRoles(portal, TEST_USER_ID, ('Manager',))
        
        portal.invokeFactory('optilux.CinemaFolder', 'cf1')
        portal.invokeFactory('optilux.CinemaFolder', 'cf2')
        
        portal['cf1'].invokeFactory('optilux.Promotion', 'p1')
        portal['cf1'].invokeFactory('optilux.Promotion', 'p2')
        portal['cf1'].invokeFactory('optilux.Promotion', 'p3')
        portal['cf1'].invokeFactory('optilux.Promotion', 'p4')
        portal['cf1'].invokeFactory('optilux.Promotion', 'p5')
        portal['cf2'].invokeFactory('optilux.Promotion', 'p6')
        portal['cf2'].invokeFactory('optilux.Promotion', 'p7')

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        
        portal = self.layer['portal']
        
        context = context or portal
        request = request or self.layer['request']
        
        view = view or portal.restrictedTraverse('@@plone')
        
        manager = manager or getUtility(IPortletManager, name='plone.rightcolumn', context=portal)
        assignment = assignment or promotions.Assignment()

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def test_count(self):
        
        portal = self.layer['portal']
        
        r = self.renderer(context=portal['cf1'], assignment=promotions.Assignment(count=5))
        self.assertEqual(5, len([p for p in r.promotions()]))

    def test_randomize(self):
        
        portal = self.layer['portal']
        
        r = self.renderer(context=portal['cf1'], assignment=promotions.Assignment(count=5, randomize=True))
        self.assertEqual(5, len([p for p in r.promotions()]))
        # Mmmm, hard to test for random things :)
        
    def test_sitewide(self):
        
        portal = self.layer['portal']
        
        r = self.renderer(context=portal['cf1'], assignment=promotions.Assignment(count=10, sitewide=True))
        p6_url = portal['cf2']['p6'].absolute_url()
        self.assertTrue(p6_url in [p['url'] for p in r.promotions()])
