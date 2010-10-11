"""Uses Archetypes schema extension to add a new field to standard types
"""

from five import grok

from zope.component import queryUtility

from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

from plone.registry.interfaces import IRegistry

from plone.indexer import indexer

from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField

from Products.Archetypes import atapi

from optilux.cinemacontent import CinemaMessageFactory as _
from optilux.cinemacontent.interfaces import IOptiluxSettings
from optilux.cinemacontent.interfaces import IHasDAMCode

# Report
from zope.component import getMultiAdapter
from zope.component import getUtility

from plone.memoize.instance import memoize

from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.CMFCore.utils import getToolByName

from zExceptions import Forbidden

class DAMCodeField(ExtensionField, atapi.StringField):
    """Field for holding the DAM code
    """
    
class DAMCodeExtender(grok.Adapter):
    """An adapter that extends the schema of any object marked with
    IHasDAMCode.
    """
    grok.provides(ISchemaExtender)
    grok.context(IHasDAMCode)
    grok.name("optilux.cinemacontent.DAMCodeExtender")
    
    fields = [
            DAMCodeField("damCode",
                    vocabulary_factory=u"optilux.cinemacontent.DAMCodes",
                    widget=atapi.SelectionWidget(
                        label=_(u"DAM code"),
                        description=_(u"Please select from the list"),
                    ),
                ),
        ]

    def getFields(self):
        return self.fields

def DAMCodesVocabularyFactory(context):
    """Vocabulary factory for available DAM codes
    """
    
    registry = queryUtility(IRegistry)
    if registry is None:
        return SimpleVocabulary()
    
    settings = registry.forInterface(IOptiluxSettings, check=False)
    return SimpleVocabulary.fromValues(settings.damCodes or ())

# Register this function as a global utility providing IVocabularyFactory,
# which describes a callable, with the name "optilux.cinemacontent.DAMCodes".

grok.global_utility(DAMCodesVocabularyFactory,
        provides=IVocabularyFactory,
        name="optilux.cinemacontent.DAMCodes",
        direct=True,
    )

@grok.adapter(IHasDAMCode, name='damCode')
@indexer(IHasDAMCode)
def damCodeIndexer(context):
    """Create a catalogue indexer, registered as an adapter
    """
    return context.getField('damCode').get(context)

class DAMReport(grok.View):
    """View for showing content related to a particular DAM code
    """
    
    grok.context(INavigationRoot)
    grok.name('dam-report')
    grok.require('optilux.ViewReports')
    
    def update(self):
        # Hide the editable-object border
        self.request.set('disable_border', True)
        
        # Perform CSRF check (see plone.protect) if the form was submitted
        if 'damCode' in self.request.form:
            authenticator = getMultiAdapter((self.context, self.request), name=u"authenticator")
            if not authenticator.verify():
                raise Forbidden()
        
        # Record the DAM codes
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IOptiluxSettings)
        
        self.damCodes = settings.damCodes or ()
        
        # Record the selected code
        self.selectedDAMCode = self.request.form.get('damCode') or None
        
    def relatedContent(self, start=0, size=11):
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog({
            'object_provides': IHasDAMCode.__identifier__,
            'damCode': self.selectedDAMCode,
            'sort_on': 'modified',
            'sort_order': 'reverse',
            'b_start': start,
            'b_size': size,
        })
        
    def localize(self, time):
        return self._time_localizer()(time, None, self.context, domain='plonelocales')
        
    @memoize
    def _time_localizer(self):
        translation_service = getToolByName(self.context, 'translation_service')
        return translation_service.ulocalized_time
