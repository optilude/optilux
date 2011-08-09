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
from zope.component import getMultiAdapter
from plone.memoize.instance import memoize

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
