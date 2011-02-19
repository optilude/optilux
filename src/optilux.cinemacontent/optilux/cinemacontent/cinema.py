from five import grok
from zope import schema
from plone.directives import form

from zope.interface import Invalid

from plone.app.textfield import RichText

from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder

from optilux.cinemacontent import CinemaMessageFactory as _
from optilux.cinemacontent.film import IFilm

# Uniqueness validator
from z3c.form import validator
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName

# View
from datetime import datetime, timedelta

from zope.component import getUtility
from zope.component import getMultiAdapter

from plone.memoize.instance import memoize

from optilux.cinemacontent.interfaces import IScreeningLocator

# Screening view
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from optilux.cinemacontent.interfaces import MAKE_RESERVATION_PERMISSION
from AccessControl import getSecurityManager
from zExceptions import NotFound

# Reservation view
from z3c.form import field, button
from Products.statusmessages.interfaces import IStatusMessage
from optilux.cinemacontent.interfaces import ReservationError
from optilux.cinemacontent.interfaces import ITicketReserver
from optilux.cinemacontent.reservation import IReservation
from optilux.cinemacontent.reservation import Reservation

def cinemaCodeIsValid(value):
    """Contraint function to make sure the given cinema code is valid
    """
    if value:
        if len(value) < 4 or len(value) > 6 or not value.startswith('C'):
            raise Invalid(_(u"The cinema code is not of the correct format"))
    return True

class ICinema(form.Schema):
    """A cinema
    """
    
    cinemaCode = schema.ASCIILine(
            title=_(u"Cinema code"),
            description=_(u"Code used in the bookings database"),
            constraint=cinemaCodeIsValid,
        )
    
    phone = schema.TextLine(
            title=_(u"Phone number"),
            description=_(u"Please enter as the customer should dial"),
        )
    
    text = RichText(
            title=_(u"Details"),
            description=_(u"Description of the cinema"),
        )

    highlightedFilms = RelationList(
            title=_(u"Highlighted films"),
            description=_(u"Films to highlight for this cinema"),
            value_type=RelationChoice(
                    source=ObjPathSourceBinder(
                            object_provides=IFilm.__identifier__
                        ),
                ),
            required=False,
        )

class ValidateCinemaCodeUniqueness(validator.SimpleFieldValidator):
    """Validate site-wide uniquneess of cinema codes.
    """
    
    def validate(self, value):
        # Perform the standard validation first
        super(ValidateCinemaCodeUniqueness, self).validate(value)
        
        if value is not None:
            catalog = getToolByName(self.context, 'portal_catalog')
            results = catalog({'cinemaCode': value,
                               'object_provides': ICinema.__identifier__})
            
            contextUUID = IUUID(self.context, None)
            for result in results:
                if result.UID != contextUUID:
                    raise Invalid(_(u"The cinema code is already in use"))

validator.WidgetValidatorDiscriminators(
        ValidateCinemaCodeUniqueness,
        field=ICinema['cinemaCode'],
    )
grok.global_adapter(ValidateCinemaCodeUniqueness)

class View(grok.View):
    """Default view (called "@@view"") for a cinema.
    
    The associated template is found in cinema_templates/view.pt.
    """
    
    grok.context(ICinema)
    grok.require('zope2.View')
    grok.name('view')
    
    def update(self):
        self.haveHighlightedFilms = len(self.highlightedFilms()) > 0
    
    @memoize
    def highlightedFilms(self):
        
        films = []
        
        if self.context.highlightedFilms is not None:
            for ref in self.context.highlightedFilms:
                obj = ref.to_object
            
                scales = getMultiAdapter((obj, self.request), name='images')
                scale = scales.scale('image', scale='thumb')
                imageTag = None
                if scale is not None:
                    imageTag = scale.tag()
            
                films.append({
                        'url': obj.absolute_url(),
                        'title': obj.title,
                        'summary': obj.description,
                        'imageTag': imageTag,
                    })
        
        return films
    
    @memoize
    def films(self, days=14):
        locator = getUtility(IScreeningLocator)
        
        fromDate = datetime.now()
        toDate = fromDate + timedelta(days)
        
        return locator.filmsAtCinema(self.context.cinemaCode,
                fromDate, toDate,
            )

class Screenings(grok.View):
    """List screenings of a film at a cinema
    """
    
    implements(IPublishTraverse)
    
    grok.context(ICinema)
    grok.name('screenings')
    grok.require('zope2.View')
    
    filmCode = None
    
    def publishTraverse(self, request, name):
        """When traversing to .../cinema/@@screenings/filmcode, store the
        film code and return self; the next step will be to render the view,
        which can then use the code.
        """
        if self.filmCode is None:
            self.filmCode = name
            return self
        else:
            raise NotFound()
    
    def update(self):
        self.request.set('disable_border', True)
    
    @memoize
    def upcomingScreenings(self, days=14):
        cinema = self.context
        locator = getUtility(IScreeningLocator)
        
        fromDate = datetime.now()
        toDate = fromDate + timedelta(days)
        
        canReserve = getSecurityManager().checkPermission(
                MAKE_RESERVATION_PERMISSION, cinema
            )
        
        film = self.film()
        return [dict(screeningId=screening.screeningId,
                     showTime=self.localize(screening.showTime),
                     remainingTickets=screening.remainingTickets,
                     canReserve=(canReserve and
                                 screening.remainingTickets > 0))
                    for screening in 
                        locator.screenings(
                                film.filmCode,
                                cinema.cinemaCode,
                                fromDate,
                                toDate,
                            )]
        
    @memoize
    def film(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog({'filmCode': self.filmCode})[0].getObject()
    
    def localize(self, time):
        return self._time_localizer()(time.isoformat(), 
                                        long_format=True, 
                                        context=self.context,
                                        domain='plonelocales')
    
    @memoize
    def _time_localizer(self):
        translation_service = getToolByName(
                self.context, 'translation_service'
            )
        return translation_service.ulocalized_time

class Reserve(form.Form):
    """Reserve tickets for a screening
    """
    
    implements(IPublishTraverse)
    
    grok.context(ICinema)
    grok.name('reserve')
    grok.require('optilux.MakeReservation')
    
    label = _(u"Reserve tickets")
    fields = field.Fields(IReservation).omit('screening', 'reservationId')
    ignoreContext = True
    
    screeningId = None
    
    def publishTraverse(self, request, name):
        if self.screeningId is None:
            self.screeningId = int(name)
            return self
        else:
            raise NotFound()
    
    def update(self):
        
        self.request.set('disable_border', True)
        
        # Get the real screening object
        locator = getUtility(IScreeningLocator)
        self.screening = locator.screeningById(self.screeningId)
        
        # Localise the screening time
        self.screeningTime = self.localize(self.screening.showTime)
        
        # Get the film title
        catalog = getToolByName(self.context, 'portal_catalog')
        film = catalog({
                    'object_provides': IFilm.__identifier__,
                    'filmCode': self.screening.filmCode,
                })[0]
        self.filmTitle = film.Title
        
        # Let z3c.form do its magic
        super(Reserve, self).update()

    def localize(self, time):
        return self._time_localizer()(time, None, self.context, domain='plonelocales')
        
    @memoize
    def _time_localizer(self):
        translation_service = getToolByName(self.context, 'translation_service')
        return translation_service.ulocalized_time
    
    @button.buttonAndHandler(_(u"Reserve"))
    def reserve(self, action):
        """Reserve tickets
        """
        
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        
        reserver = getUtility(ITicketReserver)
        reservation = Reservation(
                            screeningId=self.screeningId,
                            screening=self.screening,
                            numTickets=data['numTickets'],
                            customerName=data['customerName'],
                        )
        
        try:
            reserver(reservation)
        except ReservationError, e:
            IStatusMessage(self.request).add(str(e), type='error')
        else:
            confirm = _(u"Thank you! Your tickets will be ready for collection at the front desk.")
            IStatusMessage(self.request).add(confirm, type='info')
            self.request.response.redirect(self.context.absolute_url())
    
    @button.buttonAndHandler(_(u"Cancel"))
    def cancel(self, action):
        """Cancel the reservation
        """
        confirm = _(u"Reservation cancelled.")
        IStatusMessage(self.request).add(confirm, type='info')
        
        self.request.response.redirect(self.context.absolute_url())
