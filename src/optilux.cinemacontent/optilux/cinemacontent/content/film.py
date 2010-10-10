"""Definition of the Film content type. See cinemafolder.py for more
explanation on the statements below.
"""

from zope.interface import implements, directlyProvides
from zope.component import adapts

from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

from plone.indexer import indexer

from DateTime import DateTime

from Products.Archetypes.interfaces import IObjectPostValidation
from Products.CMFCore.utils import getToolByName

from Products.Archetypes import atapi
from Products.validation import V_REQUIRED

from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from plone.app.blob.field import ImageField

from optilux.cinemacontent.interfaces import IFilm
from optilux.cinemacontent.interfaces import IBannerProvider
from optilux.cinemacontent.config import PROJECTNAME

from optilux.cinemacontent import CinemaMessageFactory as _

FilmSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    atapi.StringField('filmCode',
        required=True,
        searchable=True,
        widget=atapi.StringWidget(label=_(u"Film code"),
                                  description=_(u"This should match the film code used in the "
                                                  "booking system."))
        ),

    # By using the name 'image' we can have the image show up in preview
    # folder listings for free. We use a blob field for more efficient
    # storage of large images.
    ImageField('image',
        required=True,
        languageIndependent=True,
        swallowResizeExceptions=True,
        # pil_quality=90,
        # pil_resize_algo='antialias',
        max_size='no',
        sizes={'large'   : (768, 768),
               'preview' : (400, 400),
               'mini'    : (200, 200),
               'thumb'   : (128, 128),
               'tile'    :  (64, 64),
               'icon'    :  (32, 32),
               'listing' :  (16, 16),
               },
        validators=(('isNonEmptyFile', V_REQUIRED),
                    ('checkImageMaxSize', V_REQUIRED)),
        widget=atapi.ImageWidget(label= _(u"Banner image"),
                                 show_content_type = False,),
        ),
        
    atapi.TextField('teaser',
        required=False,
        searchable=True,
        validators=('isTidyHtmlWithCleanup',),
        default_output_type='text/x-html-safe',
        widget=atapi.RichWidget(label=_(u"Teaser"),
                                description=_(u""),
                                rows=25,
                                allow_file_upload=False),
        ),
       
    # By redefining the accessor method (which would be getStartDate() by
    # default) to start(), and similarly for end(), our content type will
    # be indexed in the same way as an Event in Plone, and the start/end
    # dates will be available for use in the calendar portlet, for example.
    
    atapi.DateTimeField('startDate',
        required=True,
        searchable=False,
        accessor='start',
        default_method=DateTime, # Default to current date
        languageIndependent=True,
        widget=atapi.CalendarWidget(label=_(u"Starts showing from"),
                                    description=_(u""),
                                    show_hm=False),
        ),

    atapi.DateTimeField('endDate',
        required=True,
        searchable=False,
        accessor='end',
        default_method=DateTime, # Default to current date
        languageIndependent=True,
        widget=atapi.CalendarWidget(label=_(u"Showing until"),
                                    description=_(u""),
                                    show_hm=False),
        ),
    ))

FilmSchema['title'].widget.label = _(u"Film name")
FilmSchema['title'].widget.description = _(u"")

FilmSchema['description'].widget.label = _(u"Short blurb or tagline")
FilmSchema['description'].widget.description = _(u"")

finalizeATCTSchema(FilmSchema, folderish=False, moveDiscussion=False)

class Film(base.ATCTContent):
    """Describe a film.
    """
    implements(IFilm)
    
    schema = FilmSchema
    
    # This method allows Plone to display the contained image
    # in its standard folder listings, and supports proper rendering
    # of scaled images. It is borrowed from ATContentTypes's ATNewsItem
    # class.
    
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        return self.getField('image').tag(self, **kwargs)

atapi.registerType(Film, PROJECTNAME)

# This simple adapter uses Archetypes' ImageField to extract an HTML tag
# for the banner image. This is used in the promotions portlet to avoid
# having a hard dependency on the AT ImageField implementation.

# Note that we adapt a class, not an interface. This means that we will only
# match adapter lookups for this class (or a subclass), which is correct in
# this case, because we are relying on internal implementation details.

class BannerProvider(object):
    implements(IBannerProvider)
    adapts(Film)
    
    def __init__(self, context):
        self.context = context
    
    @property
    def tag(self):
        return self.context.getField('image').tag(self.context, scale='thumb')
        
# This is a subscription adapter which is used to validate the film object.
# It will be called after the normal schema validation.

class ValidateFilmCodeUniqueness(object):
    """Validate site-wide uniquness of film codes.
    """
    implements(IObjectPostValidation)
    adapts(IFilm)
    
    field_name = 'filmCode'
    
    def __init__(self, context):
        self.context = context
    
    def __call__(self, request):
        value = request.form.get(self.field_name, request.get(self.field_name, None))
        if value is not None:
            catalog = getToolByName(self.context, 'portal_catalog')
            results = catalog({'filmCode': value,
                               'object_provides': IFilm.__identifier__})
            if len(results) == 0:
                return None
            elif len(results) == 1 and results[0].UID == self.context.UID():
                return None
            else:
                return {self.field_name : _(u"The film code is already in use")}
        
        # Returning None means no error
        return None
        
# A vocabulary factory to return currently valid films. The factory itself 
# is registered as a named utility in configure.zcml. This is referenced
# from cinema.py, in the highlightedFilms reference field.

def CurrentFilmsVocabularyFactory(context):
    """Vocabulary factory for currently published films
    """
    catalog = getToolByName(context, 'portal_catalog')
    items = [(r.Title, r.UID) for r in 
                catalog({'object_provides': IFilm.__identifier__,
                         'sort_on': 'sortable_title'})]
                        
    # This turns a list of title->id pairs into a vocabulary
    return SimpleVocabulary.fromItems(items)
directlyProvides(CurrentFilmsVocabularyFactory, IVocabularyFactory)

@indexer(IFilm)
def filmCodeIndexer(context):
    return context.getFilmCode()
