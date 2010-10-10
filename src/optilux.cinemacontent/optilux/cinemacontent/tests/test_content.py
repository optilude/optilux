import unittest2 as unittest

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from optilux.cinemacontent.testing import OPTILUX_CINEMACONTENT_INTEGRATION_TESTING

from zope.interface import Invalid
from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.event import notify

from zope.schema.interfaces import IVocabularyFactory

from zope.intid.interfaces import IIntIds
from z3c.relationfield import RelationValue

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping

from plone.registry.interfaces import IRegistry

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.event import ObjectInitializedEvent

class TestContent(unittest.TestCase):

    layer = OPTILUX_CINEMACONTENT_INTEGRATION_TESTING

    def test_hierarchy(self):
        portal = self.layer['portal']
        
        # Ensure that we can create the various content types without error
        
        setRoles(portal, TEST_USER_ID, ('Manager',))
        
        portal.invokeFactory('optilux.CinemaFolder', 'cf1', title=u"Cinema folder")
        portal.invokeFactory('optilux.FilmFolder', 'ff1', title=u"Film folder")
        
        setRoles(portal, TEST_USER_ID, ('Member',))
        
        portal['cf1'].invokeFactory('optilux.Cinema', 'c1', title=u"Cinema")
        portal['cf1']['c1'].invokeFactory('optilux.Promotion', 'p1', title=u"Promotion")
        
        portal['ff1'].invokeFactory('optilux.Film', 'f1', title=u"Film")
    
    def test_cinema_code_validator(self):
        from optilux.cinemacontent.cinema import cinemaCodeIsValid
        
        self.assertTrue(cinemaCodeIsValid('C123'))
        self.assertTrue(cinemaCodeIsValid('C1234'))
        self.assertTrue(cinemaCodeIsValid('C1235'))
        
        self.assertRaises(Invalid, cinemaCodeIsValid, 'B123')
        self.assertRaises(Invalid, cinemaCodeIsValid, 'C123456')
        self.assertRaises(Invalid, cinemaCodeIsValid, 'C12')
    
    def test_cinema_uniqueness_validator(self):
        from optilux.cinemacontent.cinema import ICinema
        from optilux.cinemacontent.cinema import ValidateCinemaCodeUniqueness
        
        portal = self.layer['portal']
        request = self.layer['request']
        
        setRoles(portal, TEST_USER_ID, ('Manager',))
        portal.invokeFactory('optilux.CinemaFolder', 'cf1', title=u"Cinema folder")
        setRoles(portal, TEST_USER_ID, ('Member',))
        
        # Create two cinemas
        
        portal['cf1'].invokeFactory('optilux.Cinema', 'c1', cinemaCode=u"C123")
        portal['cf1'].invokeFactory('optilux.Cinema', 'c2', cinemaCode=u"C321")
        
        # Create an instance of the validator and attemp to validate
        
        validator = ValidateCinemaCodeUniqueness(
                portal['cf1']['c2'],
                request,
                None, # view - not used, so we skip mocking it
                ICinema['cinemaCode'],
                None, # widget - also not used
            )
        
        validator.validate('C999')
        validator.validate('C321')
        
        self.assertRaises(Invalid, validator.validate, 'A1')
        self.assertRaises(Invalid, validator.validate, 'C123')
    
    def test_cinema_code_indexer(self):
        portal = self.layer['portal']
        
        setRoles(portal, TEST_USER_ID, ('Manager',))
        portal.invokeFactory('optilux.CinemaFolder', 'cf1', title=u"Cinema folder")
        setRoles(portal, TEST_USER_ID, ('Member',))
        
        # Create two cinemas
        
        portal['cf1'].invokeFactory('optilux.Cinema', 'c1', cinemaCode=u"123")
        portal['cf1'].invokeFactory('optilux.Cinema', 'c2', cinemaCode=u"321")
        
        # Make sure we can search for the cinema code and access it as
        # metadata
        
        catalog = getToolByName(portal, 'portal_catalog')
        results = list(catalog({'cinemaCode': u"123"}))
        
        self.assertEqual(1, len(results))
        self.assertEqual(u"123", results[0].cinemaCode)
    
    def test_film_code_validator(self):
        from optilux.cinemacontent.film import filmCodeIsValid
        
        self.assertTrue(filmCodeIsValid('F123'))
        self.assertTrue(filmCodeIsValid('F1234'))
        self.assertTrue(filmCodeIsValid('F1235'))
        
        self.assertRaises(Invalid, filmCodeIsValid, 'C123')
        self.assertRaises(Invalid, filmCodeIsValid, 'F123456')
        self.assertRaises(Invalid, filmCodeIsValid, 'F12')
    
    def test_film_uniquenes_validator(self):
        from optilux.cinemacontent.film import IFilm
        from optilux.cinemacontent.film import ValidateFilmCodeUniqueness
        
        
        portal = self.layer['portal']
        request = self.layer['request']
        
        setRoles(portal, TEST_USER_ID, ('Manager',))
        portal.invokeFactory('optilux.FilmFolder', 'ff1', title=u"Film folder")
        setRoles(portal, TEST_USER_ID, ('Member',))
        
        # Create two films
        
        portal['ff1'].invokeFactory('optilux.Film', 'f1', filmCode=u"F123")
        portal['ff1'].invokeFactory('optilux.Film', 'f2', filmCode=u"F321")
        
        # Create an instance of the validator and attemp to validate
        
        validator = ValidateFilmCodeUniqueness(
                portal['ff1']['f2'],
                request,
                None, # view - not used, so we skip mocking it
                IFilm['filmCode'],
                None, # widget - also not used
            )
        
        validator.validate('F999')
        validator.validate('F321')
        
        self.assertRaises(Invalid, validator.validate, 'A1')
        self.assertRaises(Invalid, validator.validate, 'F123')
    
    def test_film_code_indexer(self):
        portal = self.layer['portal']
        
        setRoles(portal, TEST_USER_ID, ('Manager',))
        portal.invokeFactory('optilux.FilmFolder', 'ff1', title=u"Film folder")
        setRoles(portal, TEST_USER_ID, ('Member',))
        
        # Create two films
        
        portal['ff1'].invokeFactory('optilux.Film', 'f1', filmCode=u"123")
        portal['ff1'].invokeFactory('optilux.Film', 'f2', filmCode=u"321")
        
        # Make sure we can search for the cinema code and access it as
        # metadata
        
        catalog = getToolByName(portal, 'portal_catalog')
        results = list(catalog({'filmCode': u"123"}))
        
        self.assertEqual(1, len(results))
        self.assertEqual(u"123", results[0].filmCode)
    
    def test_highlighted_films(self):
        portal = self.layer['portal']
        
        setRoles(portal, TEST_USER_ID, ('Manager',))
        portal.invokeFactory('optilux.CinemaFolder', 'cf1', title=u"Cinema folder")
        portal.invokeFactory('optilux.FilmFolder', 'ff1', title=u"Film folder")
        setRoles(portal, TEST_USER_ID, ('Member',))
        
        # Create two films and one cinema
        
        portal['ff1'].invokeFactory('optilux.Film', 'f1', title=u"Film 1",
                description=u"Description 1", filmCode=u"123")
        portal['ff1'].invokeFactory('optilux.Film', 'f2', title=u"Film 2",
                description=u"Description 2", filmCode=u"321")
        
        portal['cf1'].invokeFactory('optilux.Cinema', 'c1', cinemaCode=u"abc")
        
        c1 = portal['cf1']['c1']
        f1 = portal['ff1']['f1']
        f2 = portal['ff1']['f2']
        
        # Set the highlighted films
        
        intids = getUtility(IIntIds)
        c1.highlightedFilms = [
                RelationValue(intids.getId(f1)),
                RelationValue(intids.getId(f2)),
            ]
        
        # Find the cinema view and look for the highlighted films
        view = c1.restrictedTraverse('@@view')
        highlightedFilms = view.highlightedFilms()
        
        self.assertEqual(highlightedFilms,
            [{'imageTag': None,
              'summary': 'Description 1',
              'title': 'Film 1',
              'url': f1.absolute_url()},
             {'imageTag': None,
              'summary': 'Description 2',
              'title': 'Film 2',
              'url': f2.absolute_url()}])
    
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
        
        from optilux.cinemacontent.interfaces import PROMOTIONS_PORTLET_COLUMN
        from optilux.cinemacontent.portlets.promotions import IPromotionsPortlet
        
        portal = self.layer['portal']
        
        setRoles(portal, TEST_USER_ID, ('Manager',))
        portal.invokeFactory('optilux.CinemaFolder', 'cf1', title=u"Cinema folder")
        setRoles(portal, TEST_USER_ID, ('Member',))
        
        cf = portal['cf1']
        notify(ObjectInitializedEvent(cf))
        
        # Look for the portlet
        column = getUtility(IPortletManager, name=PROMOTIONS_PORTLET_COLUMN)
        manager = getMultiAdapter((cf, column,), IPortletAssignmentMapping)
        
        promotionsPortlets = [p for p in manager.values() \
                                if IPromotionsPortlet.providedBy(p)]
        
        self.assertEqual(1, len(promotionsPortlets))
