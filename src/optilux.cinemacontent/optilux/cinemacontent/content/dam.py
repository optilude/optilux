"""Schema extension
"""

from zope.interface import directlyProvides
from zope.interface import implements

from zope.component import adapts
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
    
class DAMCodeExtender(object):
    """Perform schema extension
    """
    adapts(IHasDAMCode)
    implements(ISchemaExtender)

    fields = [
            DAMCodeField("damCode",
                    vocabulary_factory=u"optilux.cinemacontent.DAMCodes",
                    widget=atapi.SelectionWidget(
                        label=_(u"DAM code"),
                        description=_(u"Please select from the list"),
                    ),
                ),
        ]

    def __init__(self, context):
        self.context = context

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
directlyProvides(DAMCodesVocabularyFactory, IVocabularyFactory)

@indexer(IHasDAMCode)
def damCodeIndexer(context):
    return context.getField('damCode').get(context)
