from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting

from plone.testing import z2

from zope.configuration import xmlconfig

class OptiluxCinemaContent(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)
    
    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import optilux.cinemacontent
        xmlconfig.file('configure.zcml', optilux.cinemacontent, context=configurationContext)
        
        # Make sure initialize() is called
        z2.installProduct(app, 'optilux.cinemacontent')
    
    def tearDownZope(self, app):
        # Uninstall products installed above
        z2.uninstallProduct(app, 'optilux.cinemacontent')
        
    def setUpPloneSite(self, portal):
        applyProfile(portal, 'optilux.cinemacontent:default')

OPTILUX_CINEMACONTENT_FIXTURE = OptiluxCinemaContent()
OPTILUX_CINEMACONTENT_INTEGRATION_TESTING = IntegrationTesting(bases=(OPTILUX_CINEMACONTENT_FIXTURE,), name="OptiluxCinemaContent:Integration")
