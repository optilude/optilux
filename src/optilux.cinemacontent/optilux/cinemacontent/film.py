from five import grok
from zope import schema
from plone.directives import form

from zope.interface import Invalid

from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.field import NamedBlobImage

from plone.app.textfield import RichText

from optilux.cinemacontent import CinemaMessageFactory as _

# Indexer
from plone.indexer import indexer

# Uniqueness validator
from datetime import datetime, timedelta
from zope.component import getUtility
from z3c.form import validator
from plone.uuid.interfaces import IUUID
from plone.memoize.instance import memoize
from optilux.cinemacontent.interfaces import IScreeningLocator
from Products.CMFCore.utils import getToolByName

def filmCodeIsValid(value):
    """Contraint function to make sure the given film code is valid
    """
    if value:
        if len(value) < 4 or len(value) > 6 or not value.startswith('F'):
            raise Invalid(_(u"The film code is not of the correct format"))
    return True

class IFilm(form.Schema, IImageScaleTraversable):
    """Describes a film
    
    We mix in IImageScaleTraversable so that we can use the @@images view
    to look up scaled versions of the 'image' field.
    """

    filmCode = schema.ASCIILine(
            title=_(u"Film code"),
            description=_(u"Code used in the bookings database"),
            constraint=filmCodeIsValid,
        )
    
    image = NamedBlobImage(
            title=_(u"Banner image"),
            description=_(u"An image used to highlight this film"),
        )
    
    teaser = RichText(
            title=_(u"Teaser"),
            description=_(u"Information about the film"),
        )
    
    startDate = schema.Date(
            title=_(u'Start date'),
            description=_(u"First date that the film is showing"),
        )
        
    endDate = schema.Date(
            title=_(u'End date'),
            description=_(u"Last date that the film is showing"),
            required=True
        )

class ValidateFilmCodeUniqueness(validator.SimpleFieldValidator):
    """Validate site-wide uniqueness of film codes.
    """
    
    def validate(self, value):
        # Perform the standard validation first
        super(ValidateFilmCodeUniqueness, self).validate(value)
        
        if value is not None:
            catalog = getToolByName(self.context, 'portal_catalog')
            results = catalog({'filmCode': value,
                               'object_provides': IFilm.__identifier__})
            
            contextUUID = IUUID(self.context, None)
            for result in results:
                if result.UID != contextUUID:
                    raise Invalid(_(u"The film code is already in use"))

validator.WidgetValidatorDiscriminators(
        ValidateFilmCodeUniqueness,
        field=IFilm['filmCode'],
    )
grok.global_adapter(ValidateFilmCodeUniqueness)

@grok.adapter(IFilm, name='start')
@indexer(IFilm)
def filmStartIndexer(context):
    """Create a catalogue indexer, registered as an adapter, which can
    populate the ``start`` index with the film's start date.
    """
    return context.startDate

@grok.adapter(IFilm, name='end')
@indexer(IFilm)
def filmEndIndexer(context):
    """Create a catalogue indexer, registered as an adapter, which can
    populate the ``end`` index with the film's end date.
    """
    return context.endDate

class View(grok.View):
    """Default view (called "@@view"") for a film.
    
    The associated template is found in film_templates/view.pt.
    """
    
    grok.context(IFilm)
    grok.require('zope2.View')
    grok.name('view')
    
    def update(self):
        """Prepare information for the template
        """
        
        self.startDateFormatted = self.context.startDate.strftime("%d %b %Y")
        self.endDateFormatted = self.context.endDate.strftime("%d %b %Y")

    @memoize
    def cinemas(self, days=14):
        locator = getUtility(IScreeningLocator)
        
        fromDate = datetime.now()
        toDate = fromDate + timedelta(days)
        return locator.cinemasForFilm(self.context.filmCode,
                fromDate, toDate,
            )
