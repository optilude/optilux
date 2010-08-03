import unittest2 as unittest
from optilux.policy.testing import OPTILUX_POLICY_INTEGRATION_TESTING

class TestSetup(unittest.TestCase):
    
    layer = OPTILUX_POLICY_INTEGRATION_TESTING
    
    def test_portal_title(self):
        portal = self.layer['portal']
        self.assertEqual("Optilux Cinemas", portal.getProperty('title'))
    
    def test_portal_description(self):
        portal = self.layer['portal']
        self.assertEqual("Welcome to Optilux Cinemas", portal.getProperty('description'))
