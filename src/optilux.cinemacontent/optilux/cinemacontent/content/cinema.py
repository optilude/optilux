"""Definition of the Cinema content type. See cinemafolder.py for more
explanation on the statements below.
"""

from zope.interface import implements
from zope.component import adapts

from plone.indexer import indexer

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.interfaces import IObjectPostValidation

from Products.Archetypes import atapi

from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from optilux.cinemacontent.interfaces import ICinema
from optilux.cinemacontent.config import PROJECTNAME

from optilux.cinemacontent import CinemaMessageFactory as _

CinemaSchema = folder.ATFolderSchema.copy() + atapi.Schema((
    
    atapi.StringField('cinemaCode',
        required=True,
        searchable=True,
        widget=atapi.StringWidget(label=_(u"Cinema code"),
                                  description=_(u"This should match the cinema code used in the "
                                                 "booking system."))
        ),
    
    atapi.StringField('phone',
        required=True,
        searchable=True,
        widget=atapi.StringWidget(label=_(u"Phone number"),
                                  description=_(u""))
        ),
        
    atapi.TextField('text',
        required=False,
        searchable=True,
        validators=('isTidyHtmlWithCleanup',),
        default_output_type='text/x-html-safe',
        widget=atapi.RichWidget(label=_(u"Descriptive text"),
                                description=_(u""),
                                rows=25,
                                allow_file_upload=False),
        ),
        
    atapi.ReferenceField('highlightedFilms',
        relationship='isPromotingFilm', # Should be unique among all references on this content type
        multiValued=True,
        vocabulary_factory=u"optilux.cinemacontent.CurrentFilms", # Found in film.py
        vocabulary_display_path_bound=-1, # Avoid silly Archetypes object title magic
        enforceVocabulary=True,
        widget=atapi.ReferenceWidget(label=_(u"Highlighted films"),
                                     description=_(u""))
        ),
    
    ))

# Adjust some of the fields copied from ATFolder. We re-use the standard
# 'title' and 'description' field as 'name' and 'description', respectively.
# This is because these fields enjoy special treatment in the Plone UI,
# for example in the way they are styled on the edit form. They also have
# special Dublin Core metadata-named accessor methods, Title() and 
# Description(), which are used in various listings and search results.

CinemaSchema['title'].widget.label = _(u"Cinema name")
CinemaSchema['title'].widget.description = _(u"")

CinemaSchema['description'].widget.label = _(u"Address")
CinemaSchema['description'].widget.description = _("")

finalizeATCTSchema(CinemaSchema, folderish=True, moveDiscussion=False)

class Cinema(folder.ATFolder):
    """Describe a cinema.
    
    This is a folder in that it can contain further pages with information,
    or promotions.
    """
    implements(ICinema)
    schema = CinemaSchema
    
atapi.registerType(Cinema, PROJECTNAME)

# This is a subscription adapter which is used to validate the cinema object.
# It will be called after the normal schema validation.

class ValidateCinemaCodeUniqueness(object):
    """Validate site-wide uniquness of cinema codes.
    """
    implements(IObjectPostValidation)
    adapts(ICinema)
    
    field_name = 'cinemaCode'
    
    def __init__(self, context):
        self.context = context
    
    def __call__(self, request):
        value = request.form.get(self.field_name, request.get(self.field_name, None))
        if value is not None:
            catalog = getToolByName(self.context, 'portal_catalog')
            results = catalog({'cinemaCode': value,
                               'object_provides': ICinema.__identifier__})
            if len(results) == 0:
                return None
            elif len(results) == 1 and results[0].UID == self.context.UID():
                return None
            else:
                return {self.field_name : _(u"The cinema code is already in use")}
        
        # Returning None means no error
        return None

@indexer(ICinema)
def cinemaCodeIndexer(context):
    """Indexer for the cinemaCode index/metadata column. Registered in
    configure.zcml.
    """
    return context.getCinemaCode()
