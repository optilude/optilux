import datetime
import unittest2 as unittest

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from optilux.cinemacontent.testing import OPTILUX_CINEMACONTENT_INTEGRATION_TESTING

class TestReservationsDatabase(unittest.TestCase):

    layer = OPTILUX_CINEMACONTENT_INTEGRATION_TESTING
    
    def test_db_mapping_screening(self):
        from optilux.cinemacontent.screening import Screening
        from z3c.saconfig import Session
        
        screening = Screening()
        screening.cinemaCode = u"ABC1"
        screening.filmCode = u"DEF1"
        screening.showTime = datetime.datetime(2011, 1, 1, 12, 0, 0)
        screening.remainingTickets = 10
        
        Session.add(screening)
        Session.flush()
        
        self.assertTrue(screening.screeningId is not None)
    
    def test_db_mapping_reservation(self):
        from optilux.cinemacontent.screening import Screening
        from optilux.cinemacontent.reservation import Reservation
        from z3c.saconfig import Session
        
        screening = Screening()
        screening.cinemaCode = u"ABC1"
        screening.filmCode = u"DEF1"
        screening.showTime = datetime.datetime(2011, 1, 1, 12, 0, 0)
        screening.remainingTickets = 10
        
        Session.add(screening)
        
        reservation = Reservation()
        reservation.numTickets = 2
        reservation.customerName = u"John Smith"
        reservation.screening = screening
        
        Session.add(reservation)
        
        Session.flush()
        
        self.assertTrue(screening.screeningId is not None)
        self.assertTrue(reservation.reservationId is not None)
        self.assertEqual(reservation.screeningId, screening.screeningId)
    
    def test_screening_locator_film_lookup(self):
        from optilux.cinemacontent.screening import Screening
        from optilux.cinemacontent.interfaces import IScreeningLocator
        from zope.component import getUtility
        from z3c.saconfig import Session
        
        screening = Screening()
        screening.cinemaCode = u"ABC1"
        screening.filmCode = u"DEF1"
        screening.showTime = datetime.datetime(2011, 1, 1, 12, 0, 0)
        screening.remainingTickets = 10
        Session.add(screening)
        
        screening = Screening()
        screening.cinemaCode = u"ABC2"
        screening.filmCode = u"DEF1"
        screening.showTime = datetime.datetime(2011, 1, 1, 12, 0, 0)
        screening.remainingTickets = 10
        Session.add(screening)
        
        Session.flush()
        
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Manager',))
        
        portal.invokeFactory('optilux.FilmFolder', 'films', title=u"Films")
        
        portal['films'].invokeFactory('optilux.Film', 'film1',
                title=u"Film 1", description=u"First film", filmCode=u"DEF1",
            )
        portal['films'].invokeFactory('optilux.Film', 'film2',
                title=u"Film 2", description=u"Second film", filmCode=u"DEF2",
            )
        
        locator = getUtility(IScreeningLocator)
        
        films = locator.filmsAtCinema(u"ABC1", 
                datetime.datetime(2011, 1, 1, 0, 0, 0),
                datetime.datetime(2011, 1, 1, 23, 59, 59),
            )
        
        self.assertEqual(films, [{'filmCode': 'DEF1',
                                  'name': 'Film 1',
                                  'summary': 'First film',
                                  'url': 'http://nohost/plone/films/film1'}])
    
    def test_screening_locator_cinema_lookup(self):
        from optilux.cinemacontent.screening import Screening
        from optilux.cinemacontent.interfaces import IScreeningLocator
        from zope.component import getUtility
        from z3c.saconfig import Session
        
        screening = Screening()
        screening.cinemaCode = u"ABC1"
        screening.filmCode = u"DEF1"
        screening.showTime = datetime.datetime(2011, 1, 1, 12, 0, 0)
        screening.remainingTickets = 10
        Session.add(screening)
        
        screening = Screening()
        screening.cinemaCode = u"ABC1"
        screening.filmCode = u"DEF2"
        screening.showTime = datetime.datetime(2011, 1, 1, 12, 0, 0)
        screening.remainingTickets = 10
        Session.add(screening)
        
        Session.flush()
        
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Manager',))
        
        portal.invokeFactory('optilux.CinemaFolder', 'cinemas', title=u"Cinemas")
        
        portal['cinemas'].invokeFactory('optilux.Cinema', 'cinema1',
                title=u"Cinema 1", description=u"First cinema",
                cinemaCode=u"ABC1",
            )
        portal['cinemas'].invokeFactory('optilux.Cinema', 'cinema2',
                title=u"Cinema 2", description=u"Second cinema",
                cinemaCode=u"ABC2",
            )
        
        locator = getUtility(IScreeningLocator)
        
        cinemas = locator.cinemasForFilm(u"DEF1", 
                datetime.datetime(2011, 1, 1, 0, 0, 0),
                datetime.datetime(2011, 1, 1, 23, 59, 59),
            )
        
        self.assertEqual(cinemas, [{'address': 'First cinema',
                                    'cinemaCode': 'ABC1',
                                    'name': 'Cinema 1',
                                    'url': 'http://nohost/plone/cinemas/cinema1'}])
    
    def test_screening_locator_screening_lookup(self):
        from optilux.cinemacontent.screening import Screening
        from optilux.cinemacontent.interfaces import IScreeningLocator
        from zope.component import getUtility
        from z3c.saconfig import Session
        
        screeningId = None
        
        screening = Screening()
        screening.cinemaCode = u"ABC1"
        screening.filmCode = u"DEF1"
        screening.showTime = datetime.datetime(2011, 1, 1, 12, 0, 0)
        screening.remainingTickets = 10
        Session.add(screening)
        
        Session.flush()
        
        screeningId = screening.screeningId
        
        screening = Screening()
        screening.cinemaCode = u"ABC1"
        screening.filmCode = u"DEF2"
        screening.showTime = datetime.datetime(2011, 1, 1, 12, 0, 0)
        screening.remainingTickets = 10
        Session.add(screening)
        
        Session.flush()
        
        locator = getUtility(IScreeningLocator)
        
        screening = locator.screeningById(screeningId)
        
        self.assertEqual(screening.cinemaCode, u"ABC1")
        self.assertEqual(screening.filmCode, u"DEF1")
    
    def test_screening_locator_screening_listing(self):
        from optilux.cinemacontent.screening import Screening
        from optilux.cinemacontent.interfaces import IScreeningLocator
        from zope.component import getUtility
        from z3c.saconfig import Session
        
        screening = Screening()
        screening.cinemaCode = u"ABC1"
        screening.filmCode = u"DEF1"
        screening.showTime = datetime.datetime(2011, 1, 1, 12, 0, 0)
        screening.remainingTickets = 10
        Session.add(screening)
        
        screening = Screening()
        screening.cinemaCode = u"ABC1"
        screening.filmCode = u"DEF2"
        screening.showTime = datetime.datetime(2011, 1, 1, 12, 0, 0)
        screening.remainingTickets = 10
        Session.add(screening)
        
        Session.flush()
        
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Manager',))
        
        portal.invokeFactory('optilux.CinemaFolder', 'cinemas', title=u"Cinemas")
        
        portal['cinemas'].invokeFactory('optilux.Cinema', 'cinema1',
                title=u"Cinema 1", description=u"First cinema",
                cinemaCode=u"ABC1",
            )
        portal['cinemas'].invokeFactory('optilux.Cinema', 'cinema2',
                title=u"Cinema 2", description=u"Second cinema",
                cinemaCode=u"ABC2",
            )
        
        portal.invokeFactory('optilux.FilmFolder', 'films', title=u"Films")
        
        portal['films'].invokeFactory('optilux.Film', 'film1',
                title=u"Film 1", description=u"First film", filmCode=u"DEF1",
            )
        portal['films'].invokeFactory('optilux.Film', 'film2',
                title=u"Film 2", description=u"Second film", filmCode=u"DEF2",
            )
        
        locator = getUtility(IScreeningLocator)
        screenings = locator.screenings(u"DEF1", u"ABC1",
                datetime.datetime(2011, 1, 1, 0, 0, 0),
                datetime.datetime(2011, 1, 1, 23, 59, 59),
            )
        
        self.assertEqual(len(screenings), 1)
        self.assertEqual(screenings[0].filmCode, u"DEF1")
        self.assertEqual(screenings[0].cinemaCode, u"ABC1")
        self.assertEqual(screenings[0].remainingTickets, 10)
    
    def test_ticket_reserver(self):
        from optilux.cinemacontent.screening import Screening
        from optilux.cinemacontent.reservation import Reservation
        from optilux.cinemacontent.interfaces import ITicketReserver
        from z3c.saconfig import Session
        from zope.component import getUtility
        
        screening = Screening()
        screening.cinemaCode = u"ABC1"
        screening.filmCode = u"DEF1"
        screening.showTime = datetime.datetime(2011, 1, 1, 12, 0, 0)
        screening.remainingTickets = 10
        
        Session.add(screening)
        Session.flush()
        
        reservation = Reservation()
        reservation.numTickets = 2
        reservation.customerName = u"John Smith"
        reservation.screening = screening
        
        reserver = getUtility(ITicketReserver)
        reserver(reservation)
        
        Session.flush()
        
        self.assertTrue(reservation.reservationId is not None)
        self.assertEqual(screening.remainingTickets, 8)
    
    def test_ticket_reserver_no_remaining_tickets(self):
        from optilux.cinemacontent.screening import Screening
        from optilux.cinemacontent.reservation import Reservation
        
        from optilux.cinemacontent.interfaces import ITicketReserver
        from optilux.cinemacontent.interfaces import ReservationError
        from z3c.saconfig import Session
        from zope.component import getUtility
        
        screening = Screening()
        screening.cinemaCode = u"ABC1"
        screening.filmCode = u"DEF1"
        screening.showTime = datetime.datetime(2011, 1, 1, 12, 0, 0)
        screening.remainingTickets = 0
        
        Session.add(screening)
        Session.flush()
        
        reservation = Reservation()
        reservation.numTickets = 2
        reservation.customerName = u"John Smith"
        reservation.screening = screening
        
        reserver = getUtility(ITicketReserver)
        
        self.assertRaises(ReservationError, reserver, reservation)
    
    def test_ticket_reserver_insufficient_tickets(self):
        from optilux.cinemacontent.screening import Screening
        from optilux.cinemacontent.reservation import Reservation
        
        from optilux.cinemacontent.interfaces import ITicketReserver
        from optilux.cinemacontent.interfaces import ReservationError
        from z3c.saconfig import Session
        from zope.component import getUtility
        
        screening = Screening()
        screening.cinemaCode = u"ABC1"
        screening.filmCode = u"DEF1"
        screening.showTime = datetime.datetime(2011, 1, 1, 12, 0, 0)
        screening.remainingTickets = 10
        
        Session.add(screening)
        Session.flush()
        
        reservation = Reservation()
        reservation.numTickets = 11
        reservation.customerName = u"John Smith"
        reservation.screening = screening
        
        reserver = getUtility(ITicketReserver)
        
        self.assertRaises(ReservationError, reserver, reservation)
