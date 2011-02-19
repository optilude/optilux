from zope.interface import Interface
from zope import schema

from optilux.cinemacontent import CinemaMessageFactory as _

PROMOTIONS_PORTLET_COLUMN = u"plone.rightcolumn"
MAKE_RESERVATION_PERMISSION = "Optilux: Make reservation"

# Database services

class IScreeningLocator(Interface):
    """A utility used to locate appropriate screenings based on
    search criteria
    """
    
    def filmsAtCinema(cinemaCode, fromDate, toDate):
        """Return a list of all films screening at the particular
        cinema between the specified dates.
        
        Returns a list of dictionaries with keys 'filmCode',
        'url', 'title' and 'summary'.
        """
        
    def cinemasForFilm(filmCode, fromDate, toDate):
        """Return a list of all cinemas screening the given film
        between the specified dates.
        
        Returns a list of dictionaries with keys 'cinemaCode',
        'url', 'name'  and 'address'.
        """
        
    def screenings(filmCode, cinemaCode, fromDate, toDate):
        """Return all screenings of the given film, at the given
        cinema, between the given dates
        
        Returns a list of IScreening objects.
        """
        
    def screeningById(screeningId):
        """Get an IScreening from a screening id
        """
        
class ITicketReserver(Interface):
    """A utility capable of making reservations
    """
    
    def __call__(reservation):
        """Make a reservation
        """

# Exceptions

class ReservationError(Exception):
    """Exception raised if there is an error making a reservation
    """

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
