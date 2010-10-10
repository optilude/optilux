from zope.interface import Interface
from zope import schema

from optilux.cinemacontent import CinemaMessageFactory as _

class IFilmFolder(Interface):
    """A folder containing films
    """
    
class IFilm(Interface):
    """A film
    """

class ICinemaFolder(Interface):
    """A folder containing cinemas
    """

class ICinema(Interface):
    """A cinema
    """

class IPromotion(Interface):
    """A promotion running for one or more cinemas
    """
    
# Adapters providing additional functionality for content types

class IBannerProvider(Interface):
    """A component which can provide an HTML tag for a banner image
    """
    
    tag = schema.TextLine(
            title=_(u"A HTML tag to render to show the banner image"),
            readonly=True,
        )

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
