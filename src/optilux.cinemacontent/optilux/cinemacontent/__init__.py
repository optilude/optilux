from sqlalchemy.ext import declarative
from zope.i18nmessageid import MessageFactory

# Define a message factory for when this product is internationalised.
# This will be imported with the special name "_" in most modules. Strings
# like _(u"message") will then be extracted by i18n tools for translation.

CinemaMessageFactory = MessageFactory('optilux.cinemacontent')

# Create a base class used for object relational mapping classes
ORMBase = declarative.declarative_base()
