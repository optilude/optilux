from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from zope.configuration import xmlconfig

class OptiluxTheme(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)
    
    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import optilux.theme
        xmlconfig.file('configure.zcml', optilux.theme, context=configurationContext)
    
    def setUpPloneSite(self, portal):
        applyProfile(portal, 'optilux.theme:default')

OPTILUX_THEME_FIXTURE = OptiluxTheme()
OPTILUX_THEME_INTEGRATION_TESTING = IntegrationTesting(bases=(OPTILUX_THEME_FIXTURE,), name="OptiluxTheme:Integration")
OPTILUX_THEME_FUNCTIONAL_TESTING = FunctionalTesting(bases=(OPTILUX_THEME_FIXTURE,), name="OptiluxTheme:Functional")
