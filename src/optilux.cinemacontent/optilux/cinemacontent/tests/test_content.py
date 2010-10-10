import unittest2 as unittest

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from optilux.cinemacontent.testing import OPTILUX_CINEMACONTENT_INTEGRATION_TESTING

from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.event import notify

from zope.schema.interfaces import IVocabularyFactory

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.event import ObjectInitializedEvent

class TestContent(unittest.TestCase):

    layer = OPTILUX_CINEMACONTENT_INTEGRATION_TESTING

    def test_hierarchy(self):
        portal = self.layer['portal']
        
        # Ensure that we can create the various content types without error
        
        setRoles(portal, TEST_USER_ID, ('Manager',))
        
        portal.invokeFactory('Cinema Folder', 'cf1', title=u"Cinema folder")
        portal.invokeFactory('Film Folder', 'ff1', title=u"Film folder")
        
        setRoles(portal, TEST_USER_ID, ('Member',))
        
        portal['cf1'].invokeFactory('Cinema', 'c1', title=u"Cinema")
        portal['cf1']['c1'].invokeFactory('Promotion', 'p1', title=u"Promotion")
        
        portal['ff1'].invokeFactory('Film', 'f1', title=u"Film")
    
    def test_cinema_uniqueness_validator(self):
        portal = self.layer['portal']
        request = self.layer['request']
        
        setRoles(portal, TEST_USER_ID, ('Manager',))
        portal.invokeFactory('Cinema Folder', 'cf1', title=u"Cinema folder")
        setRoles(portal, TEST_USER_ID, ('Member',))
        
        # Create two cinemas
        
        portal['cf1'].invokeFactory('Cinema', 'c1', cinemaCode=u"123")
        portal['cf1'].invokeFactory('Cinema', 'c2', cinemaCode=u"321")
        
        # Find out what would happen if we tried to validate an edit form
        # putting the cinema code for c2 to "123"
        
        request.form['cinemaCode'] = u"123"
        errors = portal['cf1']['c2'].validate(request)
        self.assertTrue('cinemaCode' in errors)
        
        # Ensure we don't get an error if we pick a unique code
        request.form['cinemaCode'] = u"321"
        errors = portal['cf1']['c2'].validate(request)
        self.assertFalse('cinemaCode' in errors)
    
    def test_cinema_code_indexer(self):
        portal = self.layer['portal']
        
        setRoles(portal, TEST_USER_ID, ('Manager',))
        portal.invokeFactory('Cinema Folder', 'cf1', title=u"Cinema folder")
        setRoles(portal, TEST_USER_ID, ('Member',))
        
        # Create two cinemas
        
        portal['cf1'].invokeFactory('Cinema', 'c1', cinemaCode=u"123")
        portal['cf1'].invokeFactory('Cinema', 'c2', cinemaCode=u"321")
        
        # Make sure we can search for the cinema code and access it as
        # metadata
        
        catalog = getToolByName(portal, 'portal_catalog')
        results = list(catalog({'cinemaCode': u"123"}))
        
        self.assertEqual(1, len(results))
        self.assertEqual(u"123", results[0].cinemaCode)
    
    def test_film_uniquenes_validator(self):
        portal = self.layer['portal']
        request = self.layer['request']
        
        setRoles(portal, TEST_USER_ID, ('Manager',))
        portal.invokeFactory('Film Folder', 'ff1', title=u"Film folder")
        setRoles(portal, TEST_USER_ID, ('Member',))
        
        # Create two films
        
        portal['ff1'].invokeFactory('Film', 'f1', filmCode=u"123")
        portal['ff1'].invokeFactory('Film', 'f2', filmCode=u"321")
        
        # Find out what would happen if we tried to validate an edit form
        # putting the film code for f2 to "123"
        
        request.form['filmCode'] = u"123"
        errors = portal['ff1']['f2'].validate(request)
        self.assertTrue('filmCode' in errors)
        
        # Ensure we don't get an error if we pick a unique code
        request.form['filmCode'] = u"321"
        errors = portal['ff1']['f2'].validate(request)
        self.assertFalse('filmCode' in errors)
    
    def test_film_code_indexer(self):
        portal = self.layer['portal']
        
        setRoles(portal, TEST_USER_ID, ('Manager',))
        portal.invokeFactory('Film Folder', 'ff1', title=u"Film folder")
        setRoles(portal, TEST_USER_ID, ('Member',))
        
        # Create two films
        
        portal['ff1'].invokeFactory('Film', 'f1', filmCode=u"123")
        portal['ff1'].invokeFactory('Film', 'f2', filmCode=u"321")
        
        # Make sure we can search for the cinema code and access it as
        # metadata
        
        catalog = getToolByName(portal, 'portal_catalog')
        results = list(catalog({'filmCode': u"123"}))
        
        self.assertEqual(1, len(results))
        self.assertEqual(u"123", results[0].filmCode)
    
    def test_films_vocabulary(self):
        portal = self.layer['portal']
        
        setRoles(portal, TEST_USER_ID, ('Manager',))
        portal.invokeFactory('Film Folder', 'ff1', title=u"Film folder")
        setRoles(portal, TEST_USER_ID, ('Member',))
        
        # Create two films
        
        portal['ff1'].invokeFactory('Film', 'f1', title=u"Film 1", filmCode=u"123")
        portal['ff1'].invokeFactory('Film', 'f2', title=u"Film 2", filmCode=u"321")
        
        # Look for them in the vocabulary
        vocabularyFactory = getUtility(IVocabularyFactory,
                name=u"optilux.cinemacontent.CurrentFilms"
            )
        
        vocabulary = vocabularyFactory(portal)
        terms = list(vocabulary)
        
        self.assertEqual(2, len(terms))
        titles = [term.token for term in terms]
        
        self.assertTrue('Film 1' in titles)
        self.assertTrue('Film 2' in titles)
    
    def test_highlighted_films(self):
        portal = self.layer['portal']
        
        setRoles(portal, TEST_USER_ID, ('Manager',))
        portal.invokeFactory('Cinema Folder', 'cf1', title=u"Cinema folder")
        portal.invokeFactory('Film Folder', 'ff1', title=u"Film folder")
        setRoles(portal, TEST_USER_ID, ('Member',))
        
        # Create two films and one cinema
        
        portal['ff1'].invokeFactory('Film', 'f1', title=u"Film 1",
                description=u"Description 1", filmCode=u"123")
        portal['ff1'].invokeFactory('Film', 'f2', title=u"Film 2",
                description=u"Description 2", filmCode=u"321")
        
        portal['cf1'].invokeFactory('Cinema', 'c1', cinemaCode=u"abc")
        
        c1 = portal['cf1']['c1']
        f1 = portal['ff1']['f1']
        f2 = portal['ff1']['f2']
        
        # Set the highlighted films
        c1.setHighlightedFilms([f1, f2])
        
        # Find the cinema view and look for the highlighted films
        view = c1.restrictedTraverse('@@view')
        highlightedFilms = view.highlightedFilms()
        
        self.assertEqual(highlightedFilms,
            [{'bannerTag': '<img src="%s/image_thumb" alt="Film 1" title="Film 1" height="0" width="0" />' % f1.absolute_url(),
              'summary': 'Description 1',
              'title': 'Film 1',
              'url': f1.absolute_url()},
             {'bannerTag': '<img src="%s/image_thumb" alt="Film 2" title="Film 2" height="0" width="0" />' % f2.absolute_url(),
              'summary': 'Description 2',
              'title': 'Film 2',
              'url': f2.absolute_url()}])
    
    def test_film_banner_tag(self):
        from optilux.cinemacontent.interfaces import IBannerProvider
        
        portal = self.layer['portal']
        
        setRoles(portal, TEST_USER_ID, ('Manager',))
        portal.invokeFactory('Film Folder', 'ff1', title=u"Film folder")
        setRoles(portal, TEST_USER_ID, ('Member',))
        
        # Create two films and one cinema
        
        portal['ff1'].invokeFactory('Film', 'f1', title=u"Film 1",
                description=u"Description 1", filmCode=u"123")
        
        f1 = portal['ff1']['f1']
        
        provider = IBannerProvider(f1)
        self.assertEqual(provider.tag,
                '<img src="%s/image_thumb" alt="Film 1" title="Film 1" height="0" width="0" />' % f1.absolute_url()
            )
    
    def test_promotion_banner_tag(self):
        from optilux.cinemacontent.interfaces import IBannerProvider
        
        portal = self.layer['portal']
        
        setRoles(portal, TEST_USER_ID, ('Manager',))
        portal.invokeFactory('Cinema Folder', 'cf1', title=u"Cinema folder")
        setRoles(portal, TEST_USER_ID, ('Member',))
        
        portal['cf1'].invokeFactory('Cinema', 'c1', title=u"Cinema")
        portal['cf1']['c1'].invokeFactory('Promotion', 'p1', title=u"Promotion")
        
        p1 = portal['cf1']['c1']['p1']
        
        provider = IBannerProvider(p1)
        self.assertEqual(provider.tag,
                '<img src="%s/image_thumb" alt="Promotion" title="Promotion" height="0" width="0" />' % p1.absolute_url()
            )
    
    def test_dam_field(self):
        portal = self.layer['portal']
        
        setRoles(portal, TEST_USER_ID, ('Manager',))
        portal.invokeFactory('Image', 'i1', title=u"Image 1")
        setRoles(portal, TEST_USER_ID, ('Member',))
        
        i1 = portal['i1']
        
        self.assertTrue('damCode' in i1.Schema())
    
    def test_dam_field_indexer(self):
        portal = self.layer['portal']
        
        setRoles(portal, TEST_USER_ID, ('Manager',))
        portal.invokeFactory('Image', 'i1', title=u"Image 1")
        portal.invokeFactory('Image', 'i2', title=u"Image 2")
        setRoles(portal, TEST_USER_ID, ('Member',))
        
        i1 = portal['i1']
        i1.getField('damCode').set(i1, u'One')
        i1.reindexObject()
        
        i2 = portal['i2']
        i2.getField('damCode').set(i2, u'Two')
        i2.reindexObject()
        
        catalog = getToolByName(portal, 'portal_catalog')
        results = catalog({'damCode': u"Two"})
        
        self.assertEqual(1, len(results))
        self.assertEqual(results[0].getURL(), i2.absolute_url())
    
    def test_dam_vocabulary(self):
        from zope.component import getUtility
        from plone.registry.interfaces import IRegistry
        from optilux.cinemacontent.interfaces import IOptiluxSettings
        
        portal = self.layer['portal']
        
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IOptiluxSettings)
        settings.damCodes = (u"One", u"Two", u"Three",)
        
        # Look for them in the vocabulary
        vocabularyFactory = getUtility(IVocabularyFactory,
                name=u"optilux.cinemacontent.DAMCodes"
            )
        
        vocabulary = vocabularyFactory(portal)
        terms = list(vocabulary)
        
        self.assertEqual(3, len(terms))
        titles = [term.token for term in terms]
        
        self.assertTrue('One' in titles)
        self.assertTrue('Two' in titles)
        self.assertTrue('Three' in titles)

    def test_promotions_portlet_added(self):
        
        from optilux.cinemacontent.config import PROMOTIONS_PORTLET_COLUMN
        from optilux.cinemacontent.portlets.promotions import IPromotionsPortlet
        
        portal = self.layer['portal']
        
        setRoles(portal, TEST_USER_ID, ('Manager',))
        portal.invokeFactory('Cinema Folder', 'cf1', title=u"Cinema folder")
        setRoles(portal, TEST_USER_ID, ('Member',))
        
        cf = portal['cf1']
        notify(ObjectInitializedEvent(cf))
        
        # Look for the portlet
        column = getUtility(IPortletManager, name=PROMOTIONS_PORTLET_COLUMN)
        manager = getMultiAdapter((cf, column,), IPortletAssignmentMapping)
        
        promotionsPortlets = [p for p in manager.values() \
                                if IPromotionsPortlet.providedBy(p)]
        
        self.assertEqual(1, len(promotionsPortlets))