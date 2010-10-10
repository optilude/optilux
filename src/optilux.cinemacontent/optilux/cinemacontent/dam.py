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
