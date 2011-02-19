from five import grok
from zope import schema

import sqlalchemy.types
import sqlalchemy.schema

from z3c.saconfig import Session

from zope.interface import Interface
from zope.interface import implements

from zope.site.hooks import getSite

from Products.CMFCore.utils import getToolByName

from optilux.cinemacontent.interfaces import IScreeningLocator

from optilux.cinemacontent import CinemaMessageFactory as _

from optilux.cinemacontent import ORMBase

class IScreening(Interface):
    """A screening of a film at a particular cinema
    """
    
    screeningId = schema.Int(
            title=_(u"Screening identifier"),
        )
    
    cinemaCode = schema.TextLine(
            title=_(u"Cinema code"),
        )
    
    filmCode = schema.TextLine(
            title=_(u"Film code"),
        )
    
    showTime = schema.Datetime(
            title=_(u"Show time"),
        )
    
    remainingTickets = schema.Int(
            title=_(u"Remaining tickets"),
        )

class Screening(ORMBase):
    """Database-backed implementation of IScreening
    """
    
    implements(IScreening)
    
    __tablename__ = 'screening'
    
    screeningId = sqlalchemy.schema.Column(sqlalchemy.types.Integer(),
            primary_key=True,
            autoincrement=True,
        )
        
    cinemaCode = sqlalchemy.schema.Column(sqlalchemy.types.String(4),
            nullable=False,
        )
    
    filmCode = sqlalchemy.schema.Column(sqlalchemy.types.String(4),
            nullable=False,
        )
    
    showTime = sqlalchemy.schema.Column(sqlalchemy.types.DateTime(),
            nullable=False,
        )
    
    remainingTickets = sqlalchemy.schema.Column(sqlalchemy.types.Integer(),
            nullable=False,
        )

class ScreeningLocator(grok.GlobalUtility):
    """Utility used to locate screenings
    """
    
    implements(IScreeningLocator)

    def filmsAtCinema(self, cinemaCode, fromDate, toDate):
        """Return a list of all films showing at the particular cinema
        between the specified dates.
        
        Returns a list of dictionaries with keys 'filmCode', 'url', 'title' 
        and 'summary'.
        """
        
        # Avoid circular import
        from optilux.cinemacontent.film import IFilm
        
        results = Session.query(Screening) \
                         .filter(Screening.cinemaCode==cinemaCode) \
                         .filter(Screening.showTime.between(fromDate, toDate))
        
        filmCodes = [row.filmCode for row in results]
        
        site = getSite()
        catalog = getToolByName(site, 'portal_catalog')
        
        return [ dict(filmCode=film.filmCode,
                      url=film.getURL(),
                      name=film.Title,
                      summary=film.Description,)
                 for film in 
                    catalog({'object_provides': IFilm.__identifier__,
                             'filmCode': filmCodes,
                             'sort_on': 'sortable_title'})
               ]
        
    def cinemasForFilm(self, filmCode, fromDate, toDate):
        """Return a list of all cinemas showing the given film between the
        specified dates.
        
        Returns a list of dictionaries with keys 'cinema_code', 'url', 'name' 
        and 'address'.
        """
        
        # Avoid circular import
        from optilux.cinemacontent.cinema import ICinema
        
        results = Session.query(Screening) \
                         .filter(Screening.filmCode==filmCode) \
                         .filter(Screening.showTime.between(fromDate, toDate))
        
        cinemaCodes = [row.cinemaCode for row in results]
        
        site = getSite()
        catalog = getToolByName(site, 'portal_catalog')
        
        return [ dict(cinemaCode=cinema.cinemaCode,
                      url=cinema.getURL(),
                      name=cinema.Title,
                      address=cinema.Description,)
                 for cinema in 
                    catalog({'object_provides': ICinema.__identifier__,
                             'cinemaCode': cinemaCodes,
                             'sort_on': 'sortable_title'})
               ]
    
    def screenings(self, filmCode, cinemaCode, fromDate, toDate):
        """Return all screenings of the given film, at the given cinema,
        between the given dates.
        
        Returns a list of IScreening objects.
        """
        
        screenings = Session.query(Screening) \
                            .filter(Screening.filmCode==filmCode) \
                            .filter(Screening.cinemaCode==cinemaCode) \
                            .filter(Screening.showTime.between(fromDate, toDate)) \
                            .order_by(Screening.showTime)
        
        return screenings.all()
    
    def screeningById(self, screeningId):
        """Get an IScreening from a screening id
        """
        
        return Session.query(Screening).get(screeningId)
