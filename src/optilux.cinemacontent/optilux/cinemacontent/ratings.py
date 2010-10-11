from five import grok

from BTrees.OOBTree import OOSet

from zope.annotation.interfaces import IAnnotations

from optilux.cinemacontent.film import IFilm
from optilux.cinemacontent.interfaces import IRatings

# Viewlet
from zope.component import getMultiAdapter
from plone.app.layout.globals.interfaces import IViewView
from plone.app.layout.viewlets.interfaces import IBelowContentTitle
from zExceptions import Forbidden

POSITIVE_KEY = 'optilux.cinemacontent.ratings.positive'
NEGATIVE_KEY = 'optilux.cinemacontent.ratings.negative'

class FilmRatings(grok.Adapter):
    """Rate a film
    
    The userToken is a username or IP address or other string identifying
    users. We use this to try to avoid people voting more than once.
    
    Here is how it works. First, we create a dummy film. We need to make sure 
    it's annotatable. The standard Film content type is attribute annotatable 
    because all content in Plone is.
        
        >>> from zope.interface import implements
        >>> from zope.annotation.interfaces import IAttributeAnnotatable
        
        >>> from optilux.cinemacontent.film import IFilm
        
        >>> class DummyFilm(object):
        ...     implements(IFilm, IAttributeAnnotatable)
        ...     film_code = u""
        ...     title = u""
        ...     summary = u""
        ...     teaser = u""
        ...     shown_from = None
        ...     shown_until = None
        
    We need to make sure the rating adapter is configured. Normally, this 
    would happen during ZCML processing. We also need the standard annotation
    adapter.
    
        >>> from zope.component import provideAdapter
        >>> from zope.annotation.attribute import AttributeAnnotations
        >>> provideAdapter(AttributeAnnotations)
    
        >>> from optilux.cinemacontent.ratings import FilmRatings
        >>> provideAdapter(FilmRatings, provides=IRatings, adapts=(IFilm,))
    
    Now we can adapt a film to a IRatings and rate it.
    
        >>> test_film = DummyFilm()
        >>> ratings = IRatings(test_film)
        
        >>> ratings.score is None
        True
        
    Let's rate as different users. The score is calculated as the percentage
    of positive votes, returned as an integer. Once a user has voted once, he 
    cannot vote again.
        
        >>> ratings.available('user1')
        True
        
        >>> ratings.rate('user1', True)
        >>> ratings.available('user1')
        False
        >>> ratings.score
        100
        
        >>> ratings.rate('user1', True) # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        KeyError: 'Ratings not available for user1'
        
        >>> ratings.rate('user2', False)
        >>> ratings.score
        50
        
        >>> ratings.rate('user3', True)
        >>> ratings.score
        66
    """
    grok.provides(IRatings)
    grok.context(IFilm)
    
    def __init__(self, context):
        self.context = context
        
        # We assume IFilm is annotatable, in which case we can adapt to
        # IAnnotations and get a mapping-like object back. We manage all
        # ratings under a particular key. We store all the positive votes
        # in one key and all the negative votes in another. We can then
        # just count the number of items in each set to work out the score.
        
        annotations = IAnnotations(context)
        self.positive = annotations.setdefault(POSITIVE_KEY, OOSet())
        self.negative = annotations.setdefault(NEGATIVE_KEY, OOSet())
    
    @property
    def score(self):
        positives = len(self.positive)
        negatives = len(self.negative)
        total = positives + negatives
        
        if total == 0:
            return None
        else:
            return int((float(positives) / total) * 100)
        
    def available(self, userToken):
        return not (self.positive.has_key(userToken) or 
                    self.negative.has_key(userToken))
                    
    def rate(self, userToken, positive):
        if not self.available(userToken):
            raise KeyError("Ratings not available for %s" % userToken)
        if positive:
            self.positive.insert(userToken)
        else:
            self.negative.insert(userToken)

class RatingsViewlet(grok.Viewlet):
    """Viewlet for allowing users to rate a film
    """
    
    grok.context(IFilm)
    grok.view(IViewView)
    grok.viewletmanager(IBelowContentTitle)
    grok.name('optilux.cinemacontent.ratings')
    grok.require('zope2.View')
    
    def update(self):
        self.ratings = IRatings(self.context)
        self.portal_state = getMultiAdapter((self.context, self.request), name=u"plone_portal_state")
        
        form = self.request.form
        
        vote = None
        if 'optilux.cinemacontent.ratings.VotePositive' in form:
            vote = True
        elif 'optilux.cinemacontent.ratings.VoteNegative' in form:
            vote = False
        
        if vote is None or self.portal_state.anonymous():
            return
        
        # Perform CSRF check (see plone.protect)
        authenticator = getMultiAdapter((self.context, self.request), name=u"authenticator")
        if not authenticator.verify():
            raise Forbidden()
        
        userToken = self.portal_state.member().getId()    
        if userToken is not None and self.ratings.available(userToken):
            self.ratings.rate(userToken, vote)
    
    def haveScore(self):
        return self.score() is not None
    
    def available(self):
        if self.portal_state.anonymous():
            return False
        return self.ratings.available(self.portal_state.member().getId())
    
    def score(self):
        return self.ratings.score
