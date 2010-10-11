from zope.interface import Interface
from zope import schema

from optilux.cinemacontent import CinemaMessageFactory as _

PROMOTIONS_PORTLET_COLUMN = u"plone.rightcolumn"

# Adapter interfaces

class IRatings(Interface):
    """An object which can be rated
    """
    
    score = schema.Int(
            title=_(u"A score from 1-100"),
            readonly=True,
        )
         
    def available(userToken):
        """Whether or not rating is available for the given user
        """
                       
    def rate(userToken, positive):
        """Give a positive (True) or negative (False) vote.
        """

# Marker interfaces

class IHasDAMCode(Interface):
    """Marker interface for content with the DAM code field, which is enabled
    via a schema extender.
    
    This is applied to relevant types in content/configure.zcml.
    """

# Settings stored in the registry

class IOptiluxSettings(Interface):
    """Describes registry records
    """
    
    damCodes = schema.Tuple(
            title=_(u"Digital Asset Management codes"),
            description=_(u"Allowable values for the DAM code field"),
            value_type=schema.TextLine(),
        )
