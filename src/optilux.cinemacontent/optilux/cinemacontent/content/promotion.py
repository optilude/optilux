"""Definition of the Promotion content type. See cinemafolder.py for more
explanation on the statements below.
"""

from zope.interface import implements
from zope.component import adapts

from Products.Archetypes import atapi
from Products.validation import V_REQUIRED

from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from plone.app.blob.field import ImageField

from optilux.cinemacontent.interfaces import IPromotion
from optilux.cinemacontent.interfaces import IBannerProvider
from optilux.cinemacontent.config import PROJECTNAME

from optilux.cinemacontent import CinemaMessageFactory as _

PromotionSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

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
                    ('checkImageMaxSize', V_REQUIRED),),
        widget=atapi.ImageWidget(label= _(u"Banner image"),
                                 show_content_type = False,),
        ),

    atapi.TextField('details',
        required=False,
        searchable=True,
        validators=('isTidyHtmlWithCleanup',),
        default_output_type='text/x-html-safe',
        widget=atapi.RichWidget(label=_(u"Promotion details"),
                                description=_(u""),
                                rows=25,
                                allow_file_upload=False),
        ),

    ))

PromotionSchema['title'].widget.label = _(u"Promotion title")
PromotionSchema['title'].widget.description = _(u"")

PromotionSchema['description'].widget.label = _("Short summary of the promotion")
PromotionSchema['description'].widget.description = _(u"")

PromotionSchema['effectiveDate'].required = True
PromotionSchema['expirationDate'].required = True

finalizeATCTSchema(PromotionSchema, folderish=False, moveDiscussion=False)

# Here, we change the effectiveDate and expirationDate fields from
# Archetypes' ExtensibleMetadata. By manipulating the effective and
# expiration date, we can be sure that Plone will not show promotion
# items in listings and searches outside the effective range. The 'schemata'
# refers to the tab that the field is shown on. Since this is normally set
# by the finalizeATCTSchema() call, we do this after that call

PromotionSchema['effectiveDate'].schemata = 'default'
PromotionSchema['expirationDate'].schemata = 'default'

class Promotion(base.ATCTContent):
    """Describe a promotion.
    """
    implements(IPromotion)
    
    schema = PromotionSchema
    
    # These two methods allow Plone to display the contained image
    # in its standard folder listings, and supports proper rendering
    # of scaled images. It is borrowed from ATContentTypes's ATNewsItem
    # class.
    
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        return self.getField('image').tag(self, **kwargs)

atapi.registerType(Promotion, PROJECTNAME)

# We use a similar adapter for the banner provider as the one described in
# film.py

class BannerProvider(object):
    implements(IBannerProvider)
    adapts(Promotion)
    
    def __init__(self, context):
        self.context = context
    
    @property
    def tag(self):
        return self.context.getField('image').tag(self.context, scale='thumb')
