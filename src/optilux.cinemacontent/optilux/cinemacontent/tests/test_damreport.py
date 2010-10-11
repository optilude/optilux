import unittest2 as unittest

from plone.testing.z2 import Browser
from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD

from optilux.cinemacontent.testing import OPTILUX_CINEMACONTENT_FUNCTIONAL_TESTING

from zExceptions import Unauthorized

class TestDAMReport(unittest.TestCase):

    layer = OPTILUX_CINEMACONTENT_FUNCTIONAL_TESTING

    def test_render_report_non_admin(self):
        app = self.layer['app']
        portal = self.layer['portal']
        
        browser = Browser(app)
        browser.handleErrors = False
        
        # Open page
        try:
            browser.open("%s/@@dam-report" % portal.absolute_url())
            self.fail(u"Unauthorized not raised")
        except Unauthorized:
            pass

    def test_render_report_admin(self):
        app = self.layer['app']
        portal = self.layer['portal']
        
        browser = Browser(app)
        browser.handleErrors = False
        
        # Simulate HTTP Basic authentication
        browser.addHeader('Authorization',
                'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
            )
        
        # Open page
        browser.open("%s/@@dam-report" % portal.absolute_url())
        
        self.assertTrue(u"DAM report" in browser.contents)
