import unittest2 as unittest

from plone.testing.zca import UNIT_TESTING
from optilux.facebookauth.testing import OPTILUX_FACEBOOKAUTH_INTEGRATION_TESTING

from zope.publisher.browser import TestRequest
from zope.component import provideAdapter
from zope.globalrequest import setRequest

from collective.beaker.interfaces import ISession
from collective.beaker.testing import testingSession

from Products.PlonePAS.plugins.ufactory import PloneUser
from Products.CMFCore.utils import getToolByName

class TestSetup(unittest.TestCase):
    
    layer = OPTILUX_FACEBOOKAUTH_INTEGRATION_TESTING
    
    def test_login_action_installed(self):
        portal = self.layer['portal']
        portal_actions = getToolByName(portal, 'portal_actions')
        
        self.assertTrue('facebook-login' in portal_actions['user'])
        self.assertFalse(portal_actions['user']['login'].visible)
    
    def test_pas_plugin_installed(self):
        portal = self.layer['portal']
        acl_users = portal['acl_users']
        
        self.assertTrue('optilux-facebook-users' in acl_users)

class TestPlugin(unittest.TestCase):
    
    layer = UNIT_TESTING
    
    def test_extractCredentials_no_session_adapter(self):
        from optilux.facebookauth.plugin import OptiluxFacebookUsers
        
        request = TestRequest()
        plugin = OptiluxFacebookUsers('optilux')
        creds = plugin.extractCredentials(request)
        self.assertEqual(None, creds)
    
    def test_extractCredentials_username_in_session(self):
        from optilux.facebookauth.plugin import OptiluxFacebookUsers
        from optilux.facebookauth.plugin import SessionKeys
        
        provideAdapter(testingSession)
        
        request = TestRequest()
        session = ISession(request)
        
        session[SessionKeys.userName] = 'john@smith.com'
        session[SessionKeys.userId] = '123'
        
        plugin = OptiluxFacebookUsers('optilux')
        
        creds = plugin.extractCredentials(request)
        self.assertEqual(creds, {
                'username': 'john@smith.com',
                'src': 'optilux',
                'userid': '123',
            })
    
    def test_extractCredentials_username_not_in_session(self):
        from optilux.facebookauth.plugin import OptiluxFacebookUsers
        from optilux.facebookauth.plugin import SessionKeys
        
        provideAdapter(testingSession)
        
        request = TestRequest()
        session = ISession(request)
        
        session[SessionKeys.userName] = 'john@smith.com'
        session[SessionKeys.userId] = '123'
        
        plugin = OptiluxFacebookUsers('optilux')
        
        creds = plugin.extractCredentials(request)
        self.assertEqual(creds, {
                'username': 'john@smith.com',
                'src': 'optilux',
                'userid': '123',
            })
    
    def test_extractCredentials_username_in_session_userid_not_in_session(self):
        from optilux.facebookauth.plugin import OptiluxFacebookUsers
        from optilux.facebookauth.plugin import SessionKeys
        
        provideAdapter(testingSession)
        
        request = TestRequest()
        session = ISession(request)
        
        session[SessionKeys.userName] = 'john@smith.com'
        
        plugin = OptiluxFacebookUsers('optilux')
        
        creds = plugin.extractCredentials(request)

        self.assertEqual(creds, None)
    
    def test_authenticateCredentials_optilux_is_not_src(self):
        from optilux.facebookauth.plugin import OptiluxFacebookUsers
        
        creds = {'greeting' : "hello"}
        request = TestRequest()
        plugin = OptiluxFacebookUsers('optilux')
        
        creds = plugin.authenticateCredentials(request)
        self.assertEqual(creds, None)
    
    def test_authenticateCredentials_user_id_not_in_creds_username_in_creds(self):
        from optilux.facebookauth.plugin import OptiluxFacebookUsers
        
        creds = {'username' : "foo", 'src' : "optilux"}
        request = TestRequest()
        plugin = OptiluxFacebookUsers('optilux')
        
        creds = plugin.authenticateCredentials(request)
        self.assertEqual(creds, None) 
    
    def test_authenticateCredentials_user_id_in_creds_username_not_in_creds(self):
        from optilux.facebookauth.plugin import OptiluxFacebookUsers
        
        creds = {'userid' : "bar", 'src' : "optilux"}
        request = TestRequest()
        plugin = OptiluxFacebookUsers('optilux')
        
        creds = plugin.authenticateCredentials(request)
        self.assertEqual(creds, None)
        
    def test_authenticateCredentials_user_id_and_username_in_creds(self):
        from optilux.facebookauth.plugin import OptiluxFacebookUsers
        
        creds = {'username' : "foo", 'userid' : "bar"}
        request = TestRequest()
        plugin = OptiluxFacebookUsers('optilux')
        
        creds = plugin.authenticateCredentials(request)
        self.assertEqual(creds, None)  

    def test_resetCredentials_no_session(self):
        from optilux.facebookauth.plugin import OptiluxFacebookUsers
        
        request = TestRequest()
        plugin = OptiluxFacebookUsers('optilux')
        response = request.response

        plugin.resetCredentials(request, response)
    
    def test_resetCredentials_have_session(self):
        from optilux.facebookauth.plugin import OptiluxFacebookUsers

        provideAdapter(testingSession)

        request = TestRequest()
        session = ISession(request)
        
        plugin = OptiluxFacebookUsers('optilux')
        response = request.response

        plugin.resetCredentials(request, response)
        
        self.assertTrue(session._deleted)
    
    def test_get_properties_for_user_no_session(self):
        from optilux.facebookauth.plugin import OptiluxFacebookUsers
        
        request = TestRequest()
        plugin = OptiluxFacebookUsers('optilux')
        user = PloneUser('1234', 'test@test.com')
        self.assertEqual(plugin.getPropertiesForUser(user, request), {})
    
    def test_get_properties_for_user_not_optilux_user(self):
        from optilux.facebookauth.plugin import OptiluxFacebookUsers
        
        provideAdapter(testingSession)
        request = TestRequest()
        plugin = OptiluxFacebookUsers('optilux')
        user = PloneUser('1234', 'test@test.com')
        self.assertEqual(plugin.getPropertiesForUser(user, request), {})
    
    def test_get_properties_for_user(self):
        from optilux.facebookauth.plugin import OptiluxFacebookUsers
        from optilux.facebookauth.plugin import SessionKeys
        
        provideAdapter(testingSession)
        
        request = TestRequest()
        session = ISession(request)
        session[SessionKeys.userId] = '1234'
        session[SessionKeys.userName] = 'test@test.com'
        session[SessionKeys.fullname] = u'John Smith'
        
        plugin = OptiluxFacebookUsers('optilux')
        user = PloneUser('1234', 'test@test.com')
        self.assertEqual(plugin.getPropertiesForUser(user, request), {'fullname': u'John Smith'})
    
    def test_get_roles_for_principal_no_session(self):
        from optilux.facebookauth.plugin import OptiluxFacebookUsers
        
        request = TestRequest()
        plugin = OptiluxFacebookUsers('optilux')
        user = PloneUser('1234', 'test@test.com')
        
        self.assertEqual(plugin.getRolesForPrincipal(user, request), ())
    
    def test_get_roles_for_principal_not_optilux_user(self):
        from optilux.facebookauth.plugin import OptiluxFacebookUsers
        
        provideAdapter(testingSession)
        request = TestRequest()
        plugin = OptiluxFacebookUsers('optilux')
        user = PloneUser('1234', 'test@test.com')
        self.assertEqual(plugin.getRolesForPrincipal(user, request), ())
    
    def test_get_roles_for_principal(self):
        from optilux.facebookauth.plugin import OptiluxFacebookUsers
        from optilux.facebookauth.plugin import SessionKeys
        
        provideAdapter(testingSession)
        
        request = TestRequest()
        
        session = ISession(request)
        session[SessionKeys.userId] = '1234'
        session[SessionKeys.userName] = 'test@test.com'
        
        plugin = OptiluxFacebookUsers('optilux')
        user = PloneUser('1234', 'test@test.com')
        
        self.assertEqual(plugin.getRolesForPrincipal(user, request), ('Member',))
    
    def test_enumerate_users_no_global_request(self):
        from optilux.facebookauth.plugin import OptiluxFacebookUsers
        
        plugin = OptiluxFacebookUsers('optilux')
        self.assertEqual(plugin.enumerateUsers(id='54321', exact_match=True), ())
    
    def test_enumerate_users_no_session(self):
        from optilux.facebookauth.plugin import OptiluxFacebookUsers
        
        request = TestRequest()
        setRequest(request)
        
        plugin = OptiluxFacebookUsers('optilux')
        self.assertEqual(plugin.enumerateUsers(id='54321', exact_match=True), ())
        
        setRequest(None)
    
    def test_enumerate_exact_match_not_optilux_user(self):
        from optilux.facebookauth.plugin import OptiluxFacebookUsers
        
        provideAdapter(testingSession)
        
        request = TestRequest()
        setRequest(request)
        
        plugin = OptiluxFacebookUsers('optilux')
        self.assertEqual(plugin.enumerateUsers(id='54321', exact_match=True), ())
        
        setRequest(None)
    
    def test_enumerate_exact_match_not_current_user(self):
        from optilux.facebookauth.plugin import OptiluxFacebookUsers
        from optilux.facebookauth.plugin import SessionKeys
        
        provideAdapter(testingSession)
        
        request = TestRequest()
        setRequest(request)
        
        session = ISession(request)
        session[SessionKeys.userId] = u'123'
        session[SessionKeys.userName] = u'foo@bar.com'
        
        plugin = OptiluxFacebookUsers('optilux')
        self.assertEqual(plugin.enumerateUsers(id='54321', exact_match=True), ())
        
        setRequest(None)
    
    def test_enumerate_exact_match_current_user(self):
        from optilux.facebookauth.plugin import OptiluxFacebookUsers
        from optilux.facebookauth.plugin import SessionKeys
        
        provideAdapter(testingSession)
        
        request = TestRequest()
        setRequest(request)
        
        session = ISession(request)
        session[SessionKeys.userId] = u'54321'
        session[SessionKeys.userName] = u'test@test.com'
        
        plugin = OptiluxFacebookUsers('optilux')
        self.assertEqual(plugin.enumerateUsers(id='54321', exact_match=True), 
                ({'login': u'test@test.com', 'pluginid': 'optilux', 'id': u'54321'},),
            )
        
        setRequest(None)
    
    def test_enumerate_not_exact_match_current_user(self):
        from optilux.facebookauth.plugin import OptiluxFacebookUsers
        from optilux.facebookauth.plugin import SessionKeys
        
        provideAdapter(testingSession)
        
        request = TestRequest()
        setRequest(request)
        
        session = ISession(request)
        session[SessionKeys.userId] = u'54321'
        session[SessionKeys.userName] = u'test@test.com'
        
        plugin = OptiluxFacebookUsers('optilux')
        self.assertEqual(plugin.enumerateUsers(id='54321', exact_match=False), ())
        self.assertEqual(plugin.enumerateUsers(login='test@test.com', exact_match=False), ())
        
        setRequest(None)
