"""The form used to reserve tickets. This demonstrates using z3c.form
with a custom template
"""

from five import grok
from zope import schema

import sqlalchemy.types
import sqlalchemy.orm
import sqlalchemy.schema

from z3c.saconfig import Session

from zope.interface import implements
from zope.interface import Interface

from optilux.cinemacontent.interfaces import ITicketReserver
from optilux.cinemacontent.interfaces import ReservationError

from optilux.cinemacontent.screening import IScreening
from optilux.cinemacontent.screening import Screening

from optilux.cinemacontent import ORMBase
from optilux.cinemacontent import CinemaMessageFactory as _

class IReservation(Interface):
    """A ticket reservation for a particular screening
    """
    
    reservationId = schema.Int(
            title=_(u"Reservation identifier"),
        )
    
    screening = schema.Object(
            title=_(u"Screening"),
            schema=IScreening,
        )
    
    numTickets = schema.Int(
            title=_(u"Number of tickets"),
            description=_(u"Number of tickets to reserve"),
            min=1,
        )
    
    customerName = schema.TextLine(
            title=_(u"Customer name"),
            description=_(u"The name of the customer making the reservation"),
        )

class Reservation(ORMBase):
    """A reservation for a particular screening by a particular customer
    """
    
    implements(IReservation)
    
    __tablename__ = 'reservation'
    
    reservationId = sqlalchemy.schema.Column(sqlalchemy.types.Integer(),
            primary_key=True,
            autoincrement=True,
        )
    
    screeningId = sqlalchemy.schema.Column(sqlalchemy.types.Integer(),
            sqlalchemy.schema.ForeignKey('screening.screeningId'),
            nullable=False,
        )
    
    numTickets = sqlalchemy.schema.Column(sqlalchemy.types.Integer(),
            nullable=False,
        )
    
    customerName = sqlalchemy.schema.Column(sqlalchemy.types.String(64),
            nullable=False,
        )
    
    screening = sqlalchemy.orm.relation(Screening,
            primaryjoin=Screening.screeningId==screeningId,
        )

class TicketReserver(grok.GlobalUtility):
    """Utility used to make reservations
    """
    
    implements(ITicketReserver)
    
    def __call__(self, reservation):
        """Make a reservation
        """
        
        # Make sure there are still seats available
        screening = reservation.screening
        
        if screening.remainingTickets <= 0:
            raise ReservationError(_(u"This screening is sold out!"))
        elif screening.remainingTickets < reservation.numTickets:
            raise ReservationError(_(u"Not enough tickets remaining!"))
        
        # Otherwise, we can save the reservation
        screening.remainingTickets -= reservation.numTickets
        
        Session.add(reservation)
