from five import grok
from zope import schema
from plone.directives import form

from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.field import NamedBlobImage

from plone.app.textfield import RichText

from optilux.cinemacontent import CinemaMessageFactory as _

class IPromotion(form.Schema, IImageScaleTraversable):
    """Describes a current promotion
    
    We mix in IImageScaleTraversable so that we can use the @@images view
    to look up scaled versions of the 'image' field.
    """
    
    # We implement our own versions of some of the Dublin Core fields
    # (title, description, effective_date, expiration_date) below to change
    # their properties. As a result, we will not enable the full IDublinCore
    # behavior in the FTI XML file, preferring instead to pick only some
    # values.
    
    title = schema.TextLine(
            title=_(u'Promotion title'),
        )
    
    description = schema.Text(
            title=_(u'Description'),
            description=_(u'A short summary of the promotion'),
            required=False,
            missing_value=u'',
        )
    
    image = NamedBlobImage(
            title=_(u"Banner image"),
            description=_(u"An image used to highlight this promotion"),
        )
    
    details = RichText(
            title=_(u"Details"),
            description=_(u"A detailed description of the promotion")
        )

class View(grok.View):
    """Default view (called "@@view"") for a promotion.
    
    The associated template is found in promotion_templates/view.pt.
    """
    
    grok.context(IPromotion)
    grok.require('zope2.View')
    grok.name('view')
