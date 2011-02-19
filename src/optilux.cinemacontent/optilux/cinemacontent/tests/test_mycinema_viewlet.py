import unittest2 as unittest

from plone.testing.z2 import Browser
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, TEST_USER_PASSWORD
from plone.app.testing import setRoles

from optilux.cinemacontent.testing import OPTILUX_CINEMACONTENT_FUNCTIONAL_TESTING

class TestMyCinemaViewlet(unittest.TestCase):

    layer = OPTILUX_CINEMACONTENT_FUNCTIONAL_TESTING

    def test_toggle_my_cinema(self):
        app = self.layer['app']
        portal = self.layer['portal']
        
        # Create a cinema
        
        setRoles(portal, TEST_USER_ID, ('Manager',))
        portal.invokeFactory('optilux.CinemaFolder', 'cf1', title=u"Cinema folder")
        setRoles(portal, TEST_USER_ID, ('Member',))
        
        portal['cf1'].invokeFactory('optilux.Cinema', 'c1',
                title=u"Cinema",
                cinemaCode=u"C1",
            )
        
        c1 = portal['cf1']['c1']
        
        # Commit so that the test browser knows about this
        import transaction; transaction.commit()
        
        browser = Browser(app)
        browser.handleErrors = False
        
        # Render the cinema
        browser.open(c1.absolute_url())
        
        # As anonymous we don't see the buttons
        self.assertFalse("This is my home cinema" in browser.contents)
        self.assertFalse("This is not my home cinema" in browser.contents)
        
        # Log in as a user that could record their cinema
        browser.addHeader('Authorization',
                'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,)
            )
        
        browser.open(c1.absolute_url())
        self.assertTrue("This is my home cinema" in browser.contents)
        
        # Toggle once
        browser.getControl(name='optilux.cinemacontent.mycinema.Toggle').click()
        self.assertTrue("This is not my home cinema" in browser.contents)
        
        # Toggle back
        browser.getControl(name='optilux.cinemacontent.mycinema.Toggle').click()
        self.assertTrue("This is my home cinema" in browser.contents)
