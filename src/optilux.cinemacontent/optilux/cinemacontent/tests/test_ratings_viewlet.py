import datetime
import unittest2 as unittest

from plone.testing.z2 import Browser
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, TEST_USER_PASSWORD
from plone.app.testing import setRoles

from optilux.cinemacontent.testing import OPTILUX_CINEMACONTENT_FUNCTIONAL_TESTING

class TestRatingsViewlet(unittest.TestCase):

    layer = OPTILUX_CINEMACONTENT_FUNCTIONAL_TESTING

    def test_vote_negative(self):
        app = self.layer['app']
        portal = self.layer['portal']
        
        # Create a film that can be rated
        
        setRoles(portal, TEST_USER_ID, ('Manager',))
        portal.invokeFactory('optilux.FilmFolder', 'ff1', title=u"Film folder")
        setRoles(portal, TEST_USER_ID, ('Member',))
        
        portal['ff1'].invokeFactory('optilux.Film', 'f1',
                title=u"Film",
                startDate=datetime.date.today(),
                endDate=datetime.date.today()
            )
        
        f1 = portal['ff1']['f1']
        
        # Commit so that the test browser knows about this
        import transaction; transaction.commit()
        
        browser = Browser(app)
        browser.handleErrors = False
        
        # Render the film
        browser.open(f1.absolute_url())
        
        self.assertTrue("Ratings" in browser.contents)
        self.assertTrue("No-one has voted yet" in browser.contents)
        self.assertFalse("optilux.cinemacontent.ratings.VotePositive" in browser.contents)
        
        # Log in as a user that could rate the film
        browser.addHeader('Authorization',
                'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,)
            )
        
        browser.open(f1.absolute_url())
        
        self.assertTrue("Ratings" in browser.contents)
        self.assertTrue("No-one has voted yet" in browser.contents)
        self.assertTrue("optilux.cinemacontent.ratings.VotePositive" in browser.contents)
        
        # Now vote positive
        browser.getControl(name='optilux.cinemacontent.ratings.VotePositive').click()
        
        # Check outcome
        self.assertTrue("Ratings" in browser.contents)
        self.assertTrue("100% of those who voted liked this film" in browser.contents)
        
    
    def test_vote_positive(self):
        app = self.layer['app']
        portal = self.layer['portal']
        
        # Create a film that can be rated
        
        setRoles(portal, TEST_USER_ID, ('Manager',))
        portal.invokeFactory('optilux.FilmFolder', 'ff1', title=u"Film folder")
        setRoles(portal, TEST_USER_ID, ('Member',))
        
        portal['ff1'].invokeFactory('optilux.Film', 'f1',
                title=u"Film",
                startDate=datetime.date.today(),
                endDate=datetime.date.today()
            )
        
        f1 = portal['ff1']['f1']
        
        # Commit so that the test browser knows about this
        import transaction; transaction.commit()
        
        browser = Browser(app)
        browser.handleErrors = False
        
        # Render the film
        browser.open(f1.absolute_url())
        
        self.assertTrue("Ratings" in browser.contents)
        self.assertTrue("No-one has voted yet" in browser.contents)
        self.assertFalse("optilux.cinemacontent.ratings.VotePositive" in browser.contents)
        
        # Log in as a user that could rate the film
        browser.addHeader('Authorization',
                'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,)
            )
        
        browser.open(f1.absolute_url())
        
        self.assertTrue("Ratings" in browser.contents)
        self.assertTrue("No-one has voted yet" in browser.contents)
        self.assertTrue("optilux.cinemacontent.ratings.VotePositive" in browser.contents)
        
        # Now vote positive
        browser.getControl(name='optilux.cinemacontent.ratings.VotePositive').click()
        
        # Check outcome
        self.assertTrue("Ratings" in browser.contents)
        self.assertTrue("0% of those who voted liked this film" in browser.contents)
