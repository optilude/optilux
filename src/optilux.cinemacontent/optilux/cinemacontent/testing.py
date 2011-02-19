import os
import tempfile

import sqlalchemy

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from zope.configuration import xmlconfig

from zope.component import provideUtility

from z3c.saconfig.utility import EngineFactory
from z3c.saconfig.utility import GloballyScopedSession

class OptiluxCinemaContent(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)
    
    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import optilux.cinemacontent
        xmlconfig.file('configure.zcml', optilux.cinemacontent, context=configurationContext)

        # Create database in a temporary file
        fileno, self.dbFileName = tempfile.mkstemp(suffix='.db')
        dbURI = 'sqlite:///%s' % self.dbFileName
        dbEngine = sqlalchemy.create_engine(dbURI)
        optilux.cinemacontent.ORMBase.metadata.create_all(dbEngine)
        
        # Register z3c.saconfig utilities for testing
        engine = EngineFactory(dbURI, echo=False, convert_unicode=False)
        provideUtility(engine, name=u"ftesting")
        
        session = GloballyScopedSession(engine=u"ftesting", twophase=False)
        provideUtility(session)
    
    def tearDownZope(self, app):
        # Clean up the database
        os.unlink(self.dbFileName)
        
    def setUpPloneSite(self, portal):
        applyProfile(portal, 'optilux.cinemacontent:default')

OPTILUX_CINEMACONTENT_FIXTURE = OptiluxCinemaContent()
OPTILUX_CINEMACONTENT_INTEGRATION_TESTING = IntegrationTesting(bases=(OPTILUX_CINEMACONTENT_FIXTURE,), name="OptiluxCinemaContent:Integration")
OPTILUX_CINEMACONTENT_FUNCTIONAL_TESTING = FunctionalTesting(bases=(OPTILUX_CINEMACONTENT_FIXTURE,), name="OptiluxCinemaContent:Functional")
