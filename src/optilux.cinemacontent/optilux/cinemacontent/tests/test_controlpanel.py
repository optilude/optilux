import unittest2 as unittest

from plone.testing.z2 import Browser
from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD

from optilux.cinemacontent.testing import OPTILUX_CINEMACONTENT_FUNCTIONAL_TESTING

class TestControlPanel(unittest.TestCase):

    layer = OPTILUX_CINEMACONTENT_FUNCTIONAL_TESTING

    def test_navigate_save(self):
        from zope.component import getUtility
        from plone.registry.interfaces import IRegistry
        from optilux.cinemacontent.interfaces import IOptiluxSettings
        
        app = self.layer['app']
        portal = self.layer['portal']
        
        browser = Browser(app)
        browser.handleErrors = False
        
        # Simulate HTTP Basic authentication
        browser.addHeader('Authorization',
                'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
            )
        
        # Open Plone's site setup
        browser.open("%s/plone_control_panel" % portal.absolute_url())
        
        # Go to the control panel
        browser.getLink('Optilux settings').click()
        
        # Edit the DAM codes field
        browser.getControl(name='form.widgets.damCodes').value = u"one\ntwo\nthree"
        browser.getControl('Save').click()
        
        # Verify that this made it into the registry
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IOptiluxSettings)
        self.assertEqual(settings.damCodes, (u"one", u"two", u"three",))
