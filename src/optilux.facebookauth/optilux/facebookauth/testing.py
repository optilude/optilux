from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting

from zope.configuration import xmlconfig

class OptiluxFacebookAuth(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)
    
    def setUpZope(self, app, configurationContext):
        import optilux.facebookauth
        xmlconfig.file('configure.zcml', optilux.facebookauth, context=configurationContext)
    
    def setUpPloneSite(self, portal):
        applyProfile(portal, 'optilux.facebookauth:default')

OPTILUX_FACEBOOKAUTH_FIXTURE = OptiluxFacebookAuth()
OPTILUX_FACEBOOKAUTH_INTEGRATION_TESTING = IntegrationTesting(
        bases=(OPTILUX_FACEBOOKAUTH_FIXTURE,),
        name="OptiluxFacebookAuth:Integration",
    )
